from flask import Blueprint, render_template, g, abort
from app.utilities import cache
from flask_security import auth_required
# from utilities import get_latest_tweets

admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/HDPSC-admin-panel")
@auth_required()
@cache.cached(timeout=59 * 59 * 23 * 365)
def admin_login():
    return render_template("admin_panel.html")
