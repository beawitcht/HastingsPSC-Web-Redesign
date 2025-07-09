from app.blueprints.main_routes import core_bp
from app.blueprints.admin_routes import admin_bp
from app.utilities import cache, db, Role, User, WebAuthn, security, user_datastore
from flask import Flask, make_response, render_template, g, request
from flask_security import hash_password
from flask_wtf.csrf import CSRFProtect
# from authlib.integrations.flask_client import OAuth
from werkzeug.exceptions import HTTPException
from pathlib import Path
import os
import secrets

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / '.env')

is_dev = os.getenv('IS_DEV')


# configure app
app = Flask(__name__)


app.config['WTF_CSRF_ENABLED'] = True

# admin panel stuff
app.config['SECRET_KEY'] = os.environ.get(
    "SECRET_KEY")
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get(
    "SECURITY_PASSWORD_SALT")

app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
app.config["SESSION_COOKIE_SAMESITE"] = "strict"

if is_dev == '0':
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQL_URI')
    # 2fa settings
    app.config['SECURITY_TWO_FACTOR'] = True
    app.config['SECURITY_TWO_FACTOR_REQUIRED'] = True
    app.config['SECURITY_TWO_FACTOR_ALWAYS_VALIDATE'] = False
    app.config['SECURITY_TWO_FACTOR_ENABLED_METHODS'] = [
        'authenticator']
    app.config['SECURITY_TOTP_SECRETS'] = {
        1: os.getenv('SECURITY_TOTP_SECRETS')}
    app.config['SECURITY_TOTP_ISSUER'] = os.getenv('SECURITY_TOTP_ISSUER')
    # # OAuth settings
    # app.config['SECURITY_OAUTH_ENABLE'] = True
    # app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
    # app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_CLIENT_SECRET')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite://"
# This option makes sure that DB connections from the
# pool are still valid. Important for entire application since
# many DBaaS options automatically close idle connections.

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# password settings
app.config['SECURITY_PASSWORD_CHECK_BREACHED'] = True
app.config['SECURITY_PASSWORD_COMPLEXITY_CHECKER'] = "zxcvbn"
# WebAuthn settings
app.config['SECURITY_WEBAUTHN'] = True
app.config['SECURITY_WAN_FACTOR_ENABLED'] = True
app.config['SECURITY_WAN_FACTOR_REQUIRED'] = False
app.config['SECURITY_WAN_FACTOR_ENABLED_METHODS'] = [
    'webauthn', 'authenticator']
app.config['SECURITY_WAN_RP_NAME'] = "Hastings District PSC"
app.config['SECURITY_WAN_ID'] = "localhost"


csrf = CSRFProtect(app)
# oauth = OAuth(app)


db.init_app(app)


security.init_app(app, user_datastore)

if is_dev == '1':
    # one time setup
    with app.app_context():
        # Create User to test with
        db.create_all()
        for role_name in ["superuser", "admin", "editor"]:
            if not Role.query.filter_by(name=role_name).first():
                db.session.add(Role(name=role_name))
        if not security.datastore.find_user(email="test@me.com"):
            user = security.datastore.create_user(
                email="test@me.com", password=hash_password("password"))
        security.datastore.add_role_to_user(user, 'superuser')
        db.session.commit()

# end of admin panel stuff

# disable caching if in development mode
if is_dev == '0':
    app.config['CACHE_TYPE'] = 'FileSystemCache'
    app.config['CACHE_DIR'] = Path(__file__).resolve().parent / 'tmp' / 'cache'
    app.config['CACHE_SOURCE_CHECK'] = True
else:
    app.config['CACHE_TYPE'] = 'NullCache'

cache.init_app(app)

app.register_blueprint(core_bp)
app.register_blueprint(admin_bp)


@app.before_request
def gen_nonce():
    g.nonce = secrets.token_urlsafe(16)


# Set headers
@app.after_request
def add_headers(response):
    nonce = getattr(g, 'nonce', '')
    allow_inline_attr_styles = getattr(g, 'allow_inline_attr_styles', False)
    allow_inline_elem_styles = getattr(g, 'allow_inline_elem_styles', False)

    # Start building CSP parts
    csp_parts = [
        "default-src 'none';",
        f"script-src 'nonce-{nonce}' 'self';",
        "img-src 'self' data: https://http.cat/ https://www.hastingspalestinecampaign.org/;",
        f"style-src 'self' 'nonce-{nonce}' https://fonts.gstatic.com/ https://fonts.googleapis.com/;",
        f"font-src 'self' https://fonts.gstatic.com/ https://fonts.googleapis.com/;",
        "connect-src 'self';",
        "frame-src 'self' blob:;",
        "object-src 'self';"
    ]

    if allow_inline_attr_styles:
        csp_parts.append("style-src-attr 'unsafe-inline';")

    if allow_inline_elem_styles:
        csp_parts.append(
            "style-src-elem https://fonts.gstatic.com/ https://fonts.googleapis.com/ 'unsafe-inline';")

    # Join and set the header
    response.headers['Content-Security-Policy'] = ' '.join(csp_parts)

    # allow all images
    if request.path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico')):
        response.headers['Access-Control-Allow-Origin'] = '*'

    response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response


@app.errorhandler(HTTPException)
def handle_error(error):
    # make description generic for rate limit
    if error.code == 429:
        error.description = 'Try again later.'

    return render_template("error.html", name=error.name, code=error.code, description=error.description), error.code


@app.context_processor
def main_context_processor():
    return dict(nonce=getattr(g, 'nonce', ''))


@security.context_processor
def security_context_processor():
    return dict(nonce=getattr(g, 'nonce', ''))


if __name__ == '__main__':
    app.run()
