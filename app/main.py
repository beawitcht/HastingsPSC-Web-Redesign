from flask import Flask, make_response, render_template
from flask_caching import Cache
from werkzeug.exceptions import HTTPException
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / '.env')

is_dev = os.getenv('IS_DEV')


# configure app
app = Flask(__name__)

app.config['WTF_CSRF_ENABLED'] = False

# disable caching if in development mode
if is_dev == '0':
    cache = Cache(app, config={'CACHE_TYPE': 'FileSystemCache', 'CACHE_DIR': Path(
        __file__).resolve().parent / 'tmp' / 'cache', 'CACHE_SOURCE_CHECK': True})
else:
    cache = Cache(app, config={'CACHE_TYPE': 'NullCache'})

# Set headers

@app.after_request
def add_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    response.headers['Content-Security-Policy'] = 'default-src \'none\'; script-src \'self\'' \
        ' https://js.stripe.com/v3/; img-src \'self\' data: https://http.cat/;  style-src \'self\'' \
        ' https://fonts.gstatic.com/ https://fonts.googleapis.com/; font-src \'self\'' \
        ' https://fonts.gstatic.com/ https://fonts.googleapis.com/; connect-src \'self\'; ' \
        'frame-src https://js.stripe.com/v3/;'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


from blueprints import core_bp

app.register_blueprint(core_bp)


@app.errorhandler(HTTPException)
def handle_error(error):
    # make description generic for rate limit
    if error.code == 429:
        error.description = 'Try again later.'
    return make_response(render_template("error.html", name=error.name, code=error.code, description=error.description),
                         error.code)


if __name__ == '__main__':
    app.run()
