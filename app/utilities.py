# import os
# import tweepy
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from markupsafe import Markup
import requests
import os
from werkzeug.utils import secure_filename
from pathlib import Path
from flask import abort
from functools import wraps
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_security.models import fsqla_v3 as fsqla
from PIL import Image
import io
import markdown
from dotenv import load_dotenv

cache = Cache()


load_dotenv()

# --------------------------------------

# DB stuff
db = SQLAlchemy()
security = Security()


# Define models
fsqla.FsModels.set_db_info(db)


class Role(db.Model, fsqla.FsRoleMixin):
    pass


class User(db.Model, fsqla.FsUserMixin):
    pass


class WebAuthn(db.Model, fsqla.FsWebAuthnMixin):
    pass


user_datastore = SQLAlchemyUserDatastore(db, User, Role, WebAuthn)

# --------------------------------------

# Role hierarchy

ROLE_HIERARCHY = {
    'superuser': 3,
    'admin': 2,
    'editor': 1,
}


def role_at_least(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_roles = [r.name for r in current_user.roles]
            user_level = max([ROLE_HIERARCHY.get(r, 0)
                             for r in user_roles], default=0)
            required_level = ROLE_HIERARCHY.get(required_role, 0)
            if user_level >= required_level:
                return fn(*args, **kwargs)
            abort(403)
        return wrapper
    return decorator

# --------------------------------------


def allowed_role_action(actor_roles, action, actor=None, target=None, target_roles=None, requested_roles=None):
    """
    actor_roles: list of role names for the acting user
    action: 'add', 'edit', or 'delete'
    target_roles: list of role names for the target user
    requested_roles: list of role names requested for the target user (from form)
    Returns: (allowed: bool, message: str)
    """
    if 'superuser' in actor_roles:
        return True, "Article Added successfully"

    if 'admin' in actor_roles:
        # add articles to site
        if action == 'add-article' and 'editor' in actor_roles:
            return True, "Article Added successfully"

        if action == 'add':
            # Admins can only add users with no roles or just editor
            if requested_roles:
                if 'superuser' in requested_roles or 'admin' in requested_roles:
                    return False, "Admins cannot assign admin or superuser roles."
                if set(requested_roles) == {'editor'}:
                    return True, ""
            if not requested_roles:
                return True, ""
            return False, "Admins can only add users with the editor role or no role."

        if action == 'edit':
            # Admins can only manage editors or no-role users, not other admins or superusers
            if target_roles:
                if 'superuser' in target_roles or ('admin' in target_roles and actor != target):
                    return False, "Admins cannot modify or delete other admins or superusers."

                # Admin can edit themselves (admin or admin+editor), including toggling editor role
                if actor == target and set(target_roles) in [{'admin'}, {'admin', 'editor'}] and set(requested_roles) in [{'admin'}, {'admin', 'editor'}]:
                    return True, ""
            # Admins cannot assign admin or superuser roles to others
            if requested_roles:
                if 'superuser' in requested_roles or ('admin' in requested_roles and actor != target):
                    return False, "Admins cannot assign admin or superuser roles."

            # Admins can edit editors or no-role users
            return True, ""

        if action == 'delete':
            # Admin can delete themselves if only admin or admin+editor
            if actor == target and set(target_roles) in [{'admin'}, {'admin', 'editor'}]:
                return True, ""
            # Admins can only delete editors or no-role users, not other admins or superusers
            if 'superuser' in target_roles or ('admin' in target_roles and actor != target):
                return False, "Admins cannot delete other admins or superusers."
            # Admins can delete editors or no-role users
            return True, ""

    if 'editor' in actor_roles or not actor_roles:
        if action == 'add-article' and 'editor' in actor_roles:
            return True, "Article Added successfully"
        if action == 'add':
            return False, "Editors cannot add users."
        if action == 'edit':
            # Can only edit self
            if actor != target:
                return False, "Editors can only edit themselves."
            # Prevent removing their own editor role
            if 'editor' in target_roles and requested_roles is not None and 'editor' not in requested_roles:
                return False, "Editors cannot remove their own editor role."
            # Cannot change roles at all (must match exactly)
            if set(target_roles) != set(requested_roles or target_roles):
                return False, "Editors cannot change roles."
            return True, ""
        if action == 'delete':
            # Editors and no-role users cannot delete themselves
            return False, "Editors cannot delete themselves."
    return False, "Insufficient privileges."

# Get the latest tweets from using Twitter API v2
# def get_latest_tweets(username, count=5):
#     bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
#     client = tweepy.Client(bearer_token=bearer_token)

#     try:
#         # Get the user ID from the username
#         user = client.get_user(username=username)
#         user_id = user.data.id

#         # Fetch tweets using v2 API
#         tweets = client.get_users_tweets(
#             id=user_id,
#             max_results=count,
#             tweet_fields=["created_at"],
#             exclude=["replies", "retweets"]
#         )

#         return [{
#             "created_at": tweet.created_at,
#             "text": tweet.text,
#             "id": tweet.id,
#             "url": f"https://twitter.com/{username}/status/{tweet.id}"
#         } for tweet in tweets.data] if tweets.data else []
#     except Exception as e:
#         print(f"Error fetching tweets: {e}")
#         return []


def process_image(input, max_size=800):
    # Open image
    img = Image.open(input)
    original_format = img.format

    # Resize if the image is taller than wider and larger than acceptable
    if img.height > img.width and img.height > 601:
        new_height = 600
        new_width = int((new_height / img.height) * img.width)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Resize if wider than acceptable
    elif img.width > max_size + 1:
        new_width = max_size
        new_height = int((new_width / img.width) * img.height)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Compress if size > 200KB
    quality = 95
    while True:
        buffer = io.BytesIO()
        img.save(buffer, format=original_format,
                 optimize=True, quality=quality)
        size_kb = buffer.tell() / 1024

        if size_kb <= 200 or quality <= 20:
            break
        quality -= 5
    return buffer.getvalue()

# get nested errors out for easier handling


def flatten_errors(errors):
    flat = {}
    for key, val in errors.items():
        if isinstance(val, list) and all(isinstance(i, dict) for i in val):
            # Nested FormField or FieldList
            for index, subfield_errors in enumerate(val):
                for subkey, submessages in subfield_errors.items():
                    flat_key = f"{key}-{index}-{subkey}"
                    flat[flat_key] = submessages
        else:
            flat[key] = val
    return flat


# markdown stuff


# Custom Treeprocessor to add target and rel attributes to links

class LinkTargetProcessor(Treeprocessor):
    def run(self, root):
        for element in root.iter('a'):
            element.set('target', '_blank')
            element.set('rel', 'noopener')

# Custom Extension to register the processor

class LinkTargetExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(LinkTargetProcessor(md), 'link_target', 15)


def parse_inline_links(text):
    html = markdown.markdown(
        text,
        extensions=[LinkTargetExtension()],
        output_format='html5'
    )
    return Markup(html)


# build blocks for articles


def build_blocks(request, entries, news=False):
    # Build the article content from blocks
    blocks = []
    image_path = Path(__file__).resolve().parent / \
        'static' / 'images' / 'uploaded'

    for i, block_form in enumerate(entries):
        file_key = f'article-blocks-{i}-image'
        uploaded_file = request.files.get(file_key)

        if uploaded_file and uploaded_file.filename:
            # resize and reduce file size
            if news:
                processed = process_image(uploaded_file, max_size=600)
            else:
                processed = process_image(uploaded_file)

            filename = secure_filename(uploaded_file.filename)
            with open(image_path / filename, "wb+") as f:
                f.write(processed)

            image = "/static/images/uploaded/" + filename
        else:
            image = None

        if not news:
            block = {
                "type": block_form.block_type.data,
                "content": block_form.content.data,
                "image": image,
                "alt_text": block_form.alt_text.data,
                "url_text": block_form.url_text.data
            }
        else:
            block = {
                "type": block_form.block_type.data,
                "content": block_form.content.data,
                "image": image,
                "alt_text": block_form.alt_text.data,
                "url_text": block_form.url_text.data,
                "colour": block_form.colour.data
            }

        blocks.append(block)

        for block in blocks:
            if block["type"] == "paragraph":
                block["content"] = parse_inline_links(block["content"])

    return blocks


# mjml api parse


def mjml_convert(mjml):
    url = "https://api.mjml.io/v1/render"
    id = os.getenv("MJML_ID")
    sec = os.getenv("MJML_SEC")

    response = requests.post(
        url,
        auth=(id, sec),
        json={"mjml": str(mjml)}
    )
    return response.json()["html"]
