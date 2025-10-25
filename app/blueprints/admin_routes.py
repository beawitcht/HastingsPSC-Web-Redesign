from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, Response
from app.utilities import security, db, User, Role, role_at_least, allowed_role_action, flatten_errors, build_blocks, mjml_convert, process_thumbnail
from app.forms.admin_forms import AddUserForm, ManageUserForm, UploadArticleForm, ArticleBlockForm, NewsBlockForm, UploadNewsForm, ManageFilesForm
from flask_security import auth_required, hash_password, current_user
from flask_security.utils import password_complexity_validator, password_length_validator, password_breached_validator
from sqlalchemy.exc import IntegrityError
from pathlib import Path
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import json


admin_bp = Blueprint('admin', __name__)

article_path = Path(__file__).resolve().parent.parent / \
    'templates' / 'articles'

newsletter_path = Path(__file__).resolve().parent.parent / \
    'templates' / 'newsletters'

image_path = Path(__file__).resolve().parent.parent / \
    'static' / 'images' / 'uploaded'

data_path = Path(__file__).resolve().parent.parent / \
    'static' / 'data'


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

            complexity = password_complexity_validator(password, True)
            length = password_length_validator(password)
            breached = password_breached_validator(password)

            if email == password:
                flash("Password cannot be your email", "error")
                return redirect(url_for("admin.manage_users"))

            if complexity:
                flash(str(complexity), "error")
                return redirect(url_for("admin.manage_users"))
            if length:
                flash(str(length), "error")
                return redirect(url_for("admin.manage_users"))
            if breached:
                flash(str(breached), "error")
                return redirect(url_for("admin.manage_users"))

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
        title = secure_filename(form.title.data)

        new_article = render_template(
            "article_frame.html",
            title=form.title.data,
            blocks=blocks
        )

        id = form.title.data
        alt_text = form.thumb_alt.data
        descriptor = form.descriptor.data
        date = form.date.data.strftime('%-d %B %Y')
        date = date.replace(' ', '-')

        with open(data_path / "articles.json", 'r') as f:
            json_data = json.load(f)

        new_entry = {
            "id": title,
            "alt": alt_text,
            "descriptor": descriptor,
            "date": date
        }
        for entry in json_data:
            if entry["id"] == id:
                flash(
                    "Newsletter already exists, please delete the existing letter before continuing", "error")
                return redirect(url_for("admin.post_newsletter"))

        thumbnail = process_thumbnail(request.files.get(
            "article-thumbnail"), image_path / "thumbs", title)

        if not thumbnail:
            flash(
                "You must include a thumbnail, it must be wider than it is tall", "error")
            return redirect(url_for("admin.post_article"))

        json_data.append(new_entry)

        with open(data_path / "articles.json", 'w+') as f:
            json.dump(json_data, f, indent=2)

        with open(article_path / f"{title}.html", "w+") as f:
            f.write(new_article)

        return redirect(f'/articles/{title}')

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
            blocks = build_blocks(request, form.blocks.entries, tmp=True)
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

    if request.method == "POST" and form.validate_on_submit():
        allowed, message = allowed_role_action(
            actor_roles=current_roles,
            action='add-article'
        )
        if not allowed:
            flash(message, "error")
            return redirect(url_for("admin.post_newsletter"))

        blocks = build_blocks(request, form.blocks.entries, news=True)

        with open(data_path / "newsletters.json", 'r') as f:
            json_data = json.load(f)

        date = form.date.data.strftime('%-d %B %Y')
        path_date = date.replace(' ', '-')
        new_newsletter = render_template(
            "newsletter_frame.html",
            blocks=blocks,
            url_base=url_base,
            book_recs=form.book_recs.data,
            date=date,
            path_date=path_date
        )

        new_newsletter = mjml_convert(new_newsletter)
        date = path_date
        alt_text = form.thumb_alt.data
        id = date

        for entry in json_data:
            if entry["id"] == id:
                flash(
                    "Newsletter already exists, please delete the existing letter before continuing", "error")
                return redirect(url_for("admin.post_newsletter"))

        # create email version
        email_ver_html = render_template(
            "newsletter_frame.html",
            blocks=blocks,
            url_base=url_base,
            book_recs=form.book_recs.data,
            date=date,
            path_date=path_date,
            for_download=True
        )
        email_ver_html = mjml_convert(email_ver_html)
        email_ver_path = Path(__file__).resolve(
        ).parent.parent / "templates" / "newsletters" / "email_ver"
        email_ver_path.mkdir(parents=True, exist_ok=True)

        with open(email_ver_path / f"{date}.html", "w+") as f:
            f.write(email_ver_html)

        new_entry = {
            "id": id,
            "alt": alt_text
        }

        thumbnail = process_thumbnail(request.files.get(
            "article-thumbnail"), image_path / "thumbs", date)

        if not thumbnail:
            flash(
                "You must include a thumbnail, it must be wider than it is tall", "error")
            return redirect(url_for("admin.post_newsletter"))

        json_data.append(new_entry)

        with open(data_path / "newsletters.json", 'w+') as f:
            json.dump(json_data, f, indent=2)

        with open(newsletter_path / f"{date}.html", "w+") as f:
            f.write(new_newsletter)

        return redirect(f'/newsletters/{date}')

    return render_template("add_newsletter.html", form=form, block_template=block_template)


@admin_bp.route("/HDPSC-admin-panel/download-newsletter", methods=["POST"])
@role_at_least('editor')
def donwload_newsletter():
    # Determine current user's roles
    current_roles = [r.name for r in current_user.roles]
    form = UploadNewsForm(prefix="article")
    block_template = NewsBlockForm(prefix="article-blocks-__INDEX__")
    form.user_id.data = current_user.id
    url_base = os.getenv('URL_BASE')

    if request.method == "POST" and form.validate_on_submit():
        allowed, message = allowed_role_action(
            actor_roles=current_roles,
            action='add-article'
        )
        if not allowed:
            flash(message, "error")
            return redirect(url_for("admin.download_newsletter"))

        blocks = build_blocks(
            request, form.blocks.entries, news=True, tmp=True)

        date = form.date.data.strftime('%-d %B %Y')
        path_date = date.replace(' ', '-')
        new_newsletter = render_template(
            "newsletter_frame.html",
            blocks=blocks,
            url_base=url_base,
            book_recs=form.book_recs.data,
            date=date,
            path_date=path_date,
            for_download=True
        )

        new_newsletter = mjml_convert(new_newsletter)
        date = path_date
        thumbnail = process_thumbnail(request.files.get(
            "article-thumbnail"), image_path / "thumbs", date)
        if not thumbnail:
            return "Error thumbnail must exist and be wider than it is tall"

        return new_newsletter

    return "Error occurred"


def delete_entry_by_id(data, target_id):
    # Filter out any entry whose id matches target_id
    new_data = [entry for entry in data if entry['id'] != target_id]
    return new_data


@admin_bp.route("/HDPSC-admin-panel/manage-files", methods=["GET", "POST"])
@role_at_least('editor')
def manage_files():
    current_roles = [r.name for r in current_user.roles]
    form = ManageFilesForm()
    allowed, message = allowed_role_action(
        actor_roles=current_roles,
        action='add-article'
    )
    if not allowed:
        flash(message, "error")
        return redirect(url_for("admin.manage_files"))

    with open(data_path / "newsletters.json", 'r') as f:
        newsletter_data = json.load(f)

    sorted_letters = sorted(
        newsletter_data,
        key=lambda d: datetime.strptime(d["id"], "%d-%B-%Y"),
        reverse=True  # most recent first
    )

    with open(data_path / "articles.json", 'r') as f:
        article_data = json.load(f)

    sorted_articles = sorted(
        article_data,
        key=lambda d: datetime.strptime(d["date"], "%d-%B-%Y"),
        reverse=True  # most recent first
    )

    if request.method == "POST" and form.validate_on_submit():
        letter_id = None
        article_id = None
        dl_letter_id = None

        if "delete-article" in request.form:
            allowed, message = allowed_role_action(
                actor_roles=current_roles,
                action='delete'
            )
            if not allowed:
                flash("You do not have permission to delete this", "error")
                return redirect(url_for("admin.manage_files"))

            article_id = request.form["delete-article"]

        if "delete-newsletter" in request.form:

            allowed, message = allowed_role_action(
                actor_roles=current_roles,
                action='delete'
            )
            if not allowed:
                flash("You do not have permission to delete this", "error")
                return redirect(url_for("admin.manage_files"))

            letter_id = request.form["delete-newsletter"]

        if "download-newsletter" in request.form:
            dl_letter_id = request.form["download-newsletter"]

        if dl_letter_id:
            return Response(
                render_template(
                    f"newsletters/email_ver/{secure_filename(dl_letter_id)}.html"),
                mimetype='text/html',
                headers={
                    "Content-Disposition": f"attachment;filename={secure_filename(dl_letter_id)}.html"}
            )

        if letter_id:
            letter_id = secure_filename(letter_id)
            output = delete_entry_by_id(newsletter_data, letter_id)

            with open(data_path / "newsletters.json", 'w+') as f:
                json.dump(output, f, indent=2)

            os.remove(newsletter_path / f"{letter_id}.html")
            os.remove(newsletter_path / 'email_ver' / f"{letter_id}.html")

            return render_template('manage_files.html', newsletters=output,
                                   articles=sorted_articles, form=form)

        elif article_id:
            article_id = secure_filename(article_id)
            output = delete_entry_by_id(article_data, article_id)

            with open(data_path / "articles.json", 'w+') as f:
                json.dump(output, f, indent=2)

            os.remove(article_path / f"{article_id}.html")

            return render_template('manage_files.html', newsletters=sorted_letters,
                                   articles=output, form=form)

    return render_template('manage_files.html', newsletters=sorted_letters, articles=sorted_articles, form=form)
