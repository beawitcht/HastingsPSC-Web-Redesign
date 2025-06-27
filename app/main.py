from app.blueprints import core_bp
from app.utilities import cache
from flask import Flask, make_response, render_template, g
from werkzeug.exceptions import HTTPException
from pathlib import Path
import os
import secrets

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / '.env')

is_dev = os.getenv('IS_DEV')


# configure app
app = Flask(__name__)

# configure nonce
@app.before_request
def set_nonce():
    g.nonce = secrets.token_urlsafe(16)


app.config['WTF_CSRF_ENABLED'] = True

# disable caching if in development mode
is_dev = os.getenv('IS_DEV')
if is_dev == '0':
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = Path(__file__).resolve().parent / 'tmp' / 'cache'
    app.config['CACHE_SOURCE_CHECK'] = True
else:
    app.config['CACHE_TYPE'] = 'NullCache'

cache.init_app(app)


app.register_blueprint(core_bp)


# Set headers
@app.after_request
def add_headers(response):
    nonce = g.nonce
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    if 'Content-Security-Policy' not in response.headers:
        response.headers['Content-Security-Policy'] = (
            "default-src 'none';"
            f"script-src 'self' 'nonce-{nonce}' https://js.stripe.com/v3/;"
            "img-src 'self';"
            "style-src 'self' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
            "font-src 'self' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
            "connect-src 'self';"
            "frame-src 'self';"
        )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.errorhandler(HTTPException)
def handle_error(error):
    # make description generic for rate limit
    if error.code == 429:
        error.description = 'Try again later.'
    nonce = secrets.token_urlsafe(16)
    response = make_response(render_template("error.html", name=error.name, code=error.code,
                                             description=error.description, nonce=nonce),
                             error.code
                             )
    response.headers['Content-Security-Policy'] = (
        "default-src 'none';"
        "script-src 'self';"
        "img-src 'self' data: https://http.cat/;"
        f"style-src 'self' 'nonce-{nonce}' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
        "font-src 'self' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
        "connect-src 'self';"
        "frame-src 'self';"
    )

    return response


if __name__ == '__main__':
    app.run()
