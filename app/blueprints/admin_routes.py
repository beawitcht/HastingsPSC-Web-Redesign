from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from app.utilities import security, db, User, Role, role_at_least, allowed_role_action, process_image, flatten_errors, parse_inline_links
from app.forms.admin_forms import AddUserForm, ManageUserForm, UploadArticleForm, ArticleBlockForm
from flask_security import auth_required, hash_password, current_user
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from pathlib import Path

admin_bp = Blueprint('admin', __name__)

article_path = Path(__file__).resolve().parent.parent / \
    'templates' / 'articles'
image_path = Path(__file__).resolve().parent.parent / \
    'static' / 'images' / 'uploaded'


@admin_bp.route("/HDPSC-admin-panel")
@auth_required()
def admin_login():
    return render_template("admin_panel.html")


@admin_bp.route("/HDPSC-admin-panel/manage-users", methods=["GET", "POST"])
@role_at_least('editor')
def manage_users():
    # Determine current user's roles
    current_roles = [r.name for r in current_user.roles]
    is_superuser = 'superuser' in current_roles
    is_admin = 'admin' in current_roles

    # Determine which users to show
    if is_superuser or is_admin:
        users = User.query.all()
    else:
        # Others can only see themselves
        users = [current_user]

    add_form = AddUserForm(prefix="add")
    forms = []
    for user in users:
        form = ManageUserForm(obj=user, prefix=f"user_{user.id}")
        form.user_id.data = user.id
        target = user.id

        if request.method == "GET":
            form.superuser.data = any(
                role.name == "superuser" for role in user.roles)
            form.admin.data = any(role.name == "admin" for role in user.roles)
            form.editor.data = any(
                role.name == "editor" for role in user.roles)

        forms.append((user, form))

    if request.method == "POST":
        # Handle Add User form
        if add_form.submit.data and add_form.validate_on_submit():
            requested_roles = []
            if add_form.superuser.data:
                requested_roles.append("superuser")
            if add_form.admin.data:
                requested_roles.append("admin")
            if add_form.editor.data:
                requested_roles.append("editor")

            allowed, message = allowed_role_action(
                actor_roles=current_roles,
                action='add',
                actor=current_user.id,
                target=target,
                requested_roles=requested_roles
            )
            if not allowed:
                flash(message, "error")
                return redirect(url_for("admin.manage_users"))

            email = add_form.email.data
            password = add_form.password.data
            if not email or not password:
                flash("Email and password required.", "error")
            elif User.query.filter_by(email=email).first():
                flash("User already exists.", "error")
            else:
                user = security.datastore.create_user(
                    email=email,
                    password=hash_password(password),
                    active=True
                )
                for role_name in requested_roles:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        security.datastore.add_role_to_user(user, role)
                try:
                    db.session.commit()
                    flash("User created!", "success")
                except IntegrityError:
                    db.session.rollback()
                    flash("Invalid Operation", "error")

            return redirect(url_for("admin.manage_users"))

        # Handle Edit/Delete User forms
        for user, form in forms:
            if form.user_id.data == user.id and form.validate_on_submit():
                target_roles = [r.name for r in user.roles]
                target = user.id
                requested_roles = []
                for role_name in ["superuser", "admin", "editor"]:
                    if getattr(form, role_name).data:
                        requested_roles.append(role_name)
                if form.update.data:
                    allowed, message = allowed_role_action(
                        actor_roles=current_roles,
                        action='edit',
                        actor=current_user.id,
                        target=target,
                        target_roles=target_roles,
                        requested_roles=requested_roles
                    )
                    if not allowed:
                        flash(message, "error")
                        return redirect(url_for("admin.manage_users"))
                    # Only now update roles
                    for role_name in ["superuser", "admin", "editor"]:
                        role = Role.query.filter_by(name=role_name).first()
                        has_role = role_name in target_roles
                        should_have = role_name in requested_roles
                        if should_have and not has_role:
                            security.datastore.add_role_to_user(user, role)
                        elif not should_have and has_role:
                            security.datastore.remove_role_from_user(
                                user, role)

                    # Allow email change for all
                    user.email = form.email.data
                    try:
                        db.session.commit()
                        flash(f"User {user.email} updated.", "success")
                    except IntegrityError:
                        db.session.rollback()
                        flash("Invalid Operation", "error")

                    return redirect(url_for("admin.manage_users"))

                elif form.delete.data:
                    allowed, message = allowed_role_action(
                        actor_roles=current_roles,
                        action='delete',
                        actor=current_user.id,
                        target=target,
                        target_roles=target_roles
                    )
                    if not allowed:
                        flash(message, "error")
                        return redirect(url_for("admin.manage_users"))
                    db.session.delete(user)
                    try:
                        db.session.commit()
                        flash(f"User {user.email} deleted.", "success")
                    except IntegrityError:
                        db.session.rollback()
                        flash("Invalid Operation", "error")
                    return redirect(url_for("admin.manage_users"))
            else:
                flash("Invalid Operation", "error")
                return redirect(url_for("admin.manage_users"))

    # Only show add_form to superuser or admin
    show_add_form = is_superuser or is_admin

    return render_template("manage_users.html", forms=forms, add_form=add_form, show_add_form=show_add_form)


@admin_bp.route("/HDPSC-admin-panel/post-article", methods=["GET", "POST"])
@role_at_least('editor')
def post_article():
    # Determine current user's roles
    current_roles = [r.name for r in current_user.roles]
    form = UploadArticleForm(prefix="article")
    block_template = ArticleBlockForm(prefix="article-blocks-__INDEX__")
    form.user_id.data = current_user.id

    # Handle dynamic add block
    if request.method == "POST" and "add_block" in request.form:
        form.blocks.append_entry()
        return render_template("add_article.html", form=form, block_template=block_template)

    if request.method == "POST" and form.validate_on_submit():
        allowed, message = allowed_role_action(
            actor_roles=current_roles,
            action='add-article'
        )
        if not allowed:
            flash(message, "error")
            return redirect(url_for("admin.post_article"))

        # Build the article content from blocks
        blocks = []

        for i, block_form in enumerate(form.blocks.entries):
            file_key = f'article-blocks-{i}-image'
            uploaded_file = request.files.get(file_key)

            if uploaded_file and uploaded_file.filename:
                # resize and reduce file size
                processed = process_image(uploaded_file)

                filename = secure_filename(uploaded_file.filename)
                with open(image_path / filename, "wb+") as f:
                    f.write(processed)

                image = "/static/images/uploaded/" + filename
            else:
                image = None

            block = {
                "type": block_form.block_type.data,
                "content": block_form.content.data,
                "image": image,
                "alt_text": block_form.alt_text.data,
                "url_text": block_form.url_text.data
            }
            blocks.append(block)

            for block in blocks:
                if block["type"] == "paragraph":
                    block["content"] = parse_inline_links(block["content"])

        new_article = render_template(
            "article_frame.html",
            title=form.title.data,
            blocks=blocks
        )

        with open(article_path / f"{form.title.data}.html", "w+") as f:
            f.write(new_article)

        return redirect(f'/articles/{form.title.data}')

    return render_template("add_article.html", form=form, block_template=block_template)


@admin_bp.route("/HDPSC-admin-panel/preview-article", methods=["POST"])
@role_at_least('editor')
def preview_article():
    current_roles = [r.name for r in current_user.roles]
    form = UploadArticleForm(prefix="article")
    block_template = ArticleBlockForm(prefix="article-blocks-__INDEX__")

    if not form.validate_on_submit():
        return jsonify({'errors': flatten_errors(form.errors)}), 400

    if request.method == "POST" and form.validate_on_submit():
        allowed, message = allowed_role_action(
            actor_roles=current_roles,
            action='add-article'
        )
        if not allowed:
            return jsonify({'error': 'You do not have permission to perform this action'}), 403

        try:
            # Build the article content from blocks
            blocks = []

            for i, block_form in enumerate(form.blocks.entries):
                file_key = f'article-blocks-{i}-image'
                uploaded_file = request.files.get(file_key)

                if uploaded_file and uploaded_file.filename:
                    # resize and reduce file size
                    processed = process_image(uploaded_file)

                    filename = secure_filename(uploaded_file.filename)
                    with open(image_path / "tmp" / filename, "wb+") as f:
                        f.write(processed)

                    image = "/static/images/uploaded/tmp/" + filename
                else:
                    image = None

                block = {
                    "type": block_form.block_type.data,
                    "content": block_form.content.data,
                    "image": image,
                    "alt_text": block_form.alt_text.data,
                    "url_text": block_form.url_text.data
                }
                blocks.append(block)

                for block in blocks:
                    if block["type"] == "paragraph":
                        block["content"] = parse_inline_links(block["content"])

            return render_template("article_preview.html", title=form.title.data, blocks=blocks)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    flash("Preview failed. Please check your input.", "error")
    return "An error has occured, please check that article fields are valid."
