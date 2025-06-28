from app.blueprints.main_routes import core_bp
from app.blueprints.admin_routes import admin_bp
from app.utilities import cache
from flask import Flask, make_response, render_template, g, request
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_security.models import fsqla_v3 as fsqla
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

# admin panel stuff
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")

app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

# This option makes sure that DB connections from the
# pool are still valid. Important for entire application since
# many DBaaS options automatically close idle connections.

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Define models
fsqla.FsModels.set_db_info(db)

class Role(db.Model, fsqla.FsRoleMixin):
    pass

class User(db.Model, fsqla.FsUserMixin):
    pass

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# one time setup
with app.app_context():
    # Create User to test with
    db.create_all()
    if not security.datastore.find_user(email="test@me.com"):
        security.datastore.create_user(email="test@me.com", password=hash_password("password"))
    db.session.commit()

# end of admin panel stuff

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
app.register_blueprint(admin_bp)


# Set headers
@app.after_request
def add_headers(response):
    nonce = g.nonce
    path = request.path
    if path.startswith('/login') or path.startswith('/register'):
         # Relax style-src only for these routes
        response.headers['Content-Security-Policy'] = (
            "default-src 'none';"
            f"script-src 'self' 'nonce-{nonce}';"
            "img-src 'self';"
            "style-src 'self' 'unsafe-inline' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
            "font-src 'self' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
            "connect-src 'self';"
            "frame-src 'self';"
        )
    else:
        response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
        if 'Content-Security-Policy' not in response.headers:
            response.headers['Content-Security-Policy'] = (
                "default-src 'none';"
                f"script-src 'self' 'nonce-{nonce}' https://js.stripe.com/v3/;"
                "img-src 'self';"
                f"style-src 'self' 'nonce-{nonce}' https://fonts.gstatic.com/ https://fonts.googleapis.com/;"
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
