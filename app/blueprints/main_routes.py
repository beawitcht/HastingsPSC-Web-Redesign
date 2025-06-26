from flask import Blueprint, render_template, g
from utilities import cache
#from utilities import get_latest_tweets

core_bp = Blueprint('core', __name__)

@core_bp.route("/", methods=['GET'])
@cache.cached(timeout=60 * 60 * 24 * 7)
def sources():
    #tweets = get_latest_tweets("HRyepsc", count=5) uncomment and add  tweets=tweets to render template
    return render_template("index.html", nonce=g.nonce)
