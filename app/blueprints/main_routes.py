from flask import Blueprint, render_template, g, abort
from app.utilities import cache
from pathlib import Path
from datetime import datetime
import json
# from utilities import get_latest_tweets

core_bp = Blueprint('core', __name__)

data_path = Path(__file__).resolve().parent.parent / \
    'static' / 'data'


@core_bp.route("/", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def index():
    # tweets = get_latest_tweets("HRyepsc", count=5) uncomment and add  tweets=tweets to render template

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

    return render_template("index.html", newsletters=sorted_letters, articles=sorted_articles)


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


@core_bp.route("/about", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def about():

    return render_template("about.html")


@core_bp.route("/al-mawasi", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def al_mawasi():

    return render_template("al_mawasi.html")
