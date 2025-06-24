from flask import Blueprint, render_template
from main import cache

core_bp = Blueprint('core', __name__)


@core_bp.route("/", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def sources():
    return render_template("index.html")
