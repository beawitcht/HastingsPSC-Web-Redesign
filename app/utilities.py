import os
import tweepy
from flask_caching import Cache
from dotenv import load_dotenv

cache = Cache()


load_dotenv()


def get_latest_tweets(username, count=5):
    bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
    client = tweepy.Client(bearer_token=bearer_token)

    try:
        # Get the user ID from the username
        user = client.get_user(username=username)
        user_id = user.data.id

        # Fetch tweets using v2 API
        tweets = client.get_users_tweets(
            id=user_id,
            max_results=count,
            tweet_fields=["created_at"],
            exclude=["replies", "retweets"]
        )

        return [{
            "created_at": tweet.created_at,
            "text": tweet.text,
            "id": tweet.id,
            "url": f"https://twitter.com/{username}/status/{tweet.id}"
        } for tweet in tweets.data] if tweets.data else []
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return []
