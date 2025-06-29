# import os
# import tweepy
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from flask_security.models import fsqla_v3 as fsqla

from dotenv import load_dotenv

cache = Cache()


load_dotenv()

#DB stuff
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
