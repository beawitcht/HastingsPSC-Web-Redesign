from flask import Blueprint, render_template, g, abort
from app.utilities import cache
# from utilities import get_latest_tweets

core_bp = Blueprint('core', __name__)


@core_bp.route("/", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def sources():
    # tweets = get_latest_tweets("HRyepsc", count=5) uncomment and add  tweets=tweets to render template
    return render_template("index.html")


@core_bp.route("/articles/<string:title>", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def article(title):
    try:
        return render_template(f"articles/{title}.html")
    except Exception:
        abort(404)


@core_bp.route("/newsletters/<string:title>", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def newsletter(title):
    g.allow_inline_attr_styles = True
    g.allow_inline_elem_styles = True
    try:
        return render_template(f"newsletters/{title}.html")
    except Exception:
        abort(404)
