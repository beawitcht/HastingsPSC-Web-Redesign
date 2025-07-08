from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from app.utilities import security, db, User, Role, role_at_least, allowed_role_action, flatten_errors, build_blocks, mjml_convert
from app.forms.admin_forms import AddUserForm, ManageUserForm, UploadArticleForm, ArticleBlockForm, NewsBlockForm, UploadNewsForm
from flask_security import auth_required, hash_password, current_user
from sqlalchemy.exc import IntegrityError
from pathlib import Path
import os

admin_bp = Blueprint('admin', __name__)

article_path = Path(__file__).resolve().parent.parent / \
    'templates' / 'articles'

newsletter_path = Path(__file__).resolve().parent.parent / \
    'templates' / 'newsletters'

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
        blocks = build_blocks(request, form.blocks.entries)

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
            blocks = build_blocks(request, form.blocks.entries)
            return render_template("article_preview.html", title=form.title.data, blocks=blocks)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    flash("Preview failed. Please check your input.", "error")
    return "An error has occured, please check that article fields are valid."

# newsletter route


@admin_bp.route("/HDPSC-admin-panel/post-newsletter", methods=["GET", "POST"])
@role_at_least('editor')
def post_newsletter():
    # Determine current user's roles
    current_roles = [r.name for r in current_user.roles]
    form = UploadNewsForm(prefix="article")
    block_template = NewsBlockForm(prefix="article-blocks-__INDEX__")
    form.user_id.data = current_user.id
    url_base = os.getenv('URL_BASE')

    # # Handle dynamic add block
    # if request.method == "POST" and "add_block" in request.form:
    #     form.blocks.append_entry()
    #     return render_template("add_newsletter.html", form=form, block_template=block_template)

    if request.method == "POST" and form.validate_on_submit():
        allowed, message = allowed_role_action(
            actor_roles=current_roles,
            action='add-article'
        )
        if not allowed:
            flash(message, "error")
            return redirect(url_for("admin.post_newsletter"))

        blocks = build_blocks(request, form.blocks.entries, news=True)

        date = form.date.data.strftime('%-d %B %Y')

        new_newsletter = render_template(
            "newsletter_frame.html",
            blocks=blocks,
            url_base=url_base,
            book_recs=form.book_recs.data,
            date=date
        )

        new_newsletter = mjml_convert(new_newsletter)

        with open(newsletter_path / f"{date}.html", "w+") as f:
            f.write(new_newsletter)

        return redirect(f'/newsletters/{date}')

    return render_template("add_newsletter.html", form=form, block_template=block_template)
