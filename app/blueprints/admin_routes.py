from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.utilities import cache, security, db, User, Role
from app.forms.admin_forms import AddUserForm
from flask_security import auth_required, roles_required, hash_password

# from utilities import get_latest_tweets

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/HDPSC-admin-panel")
@auth_required()
def admin_login():
    return render_template("admin_panel.html")


@admin_bp.route("/HDPSC-admin-panel/add-user", methods=["GET", "POST"])
@roles_required('admin')
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
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
            # Optionally assign the admin role
            admin_role = Role.query.filter_by(name="admin").first()
            if admin_role:
                security.datastore.add_role_to_user(user, admin_role)
            db.session.commit()
            flash("User created!", "success")
            return redirect(url_for("admin.add_user"))
    return render_template("add_user.html", form=form)
