import datetime
import praw
import requests
import time
from peewee import *
from web3 import Web3
from gasbot.secrets import *
from gasbot.constants import *
from gasbot.user import *
from gasbot.comments import *
from gasbot.drip import *


# Setup connections
print("********* Connecting to web3, reddit, and db *********")
#### Wallet
web3nova = Web3(Web3.HTTPProvider(RPC_URL_NOVA))
web3matic = Web3(Web3.HTTPProvider(RPC_URL_MATIC))
######### Generate priv key as described in client.py ########
MOON2gas_nova = web3nova.eth.account.from_key(priv_key)
MOON2gas_matic = web3matic.eth.account.from_key(priv_key)
##### Reddit
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    password=password,
    user_agent=user_agent,
    username=username,
)
subreddit = reddit.subreddit("CryptoCurrencyMoons")
#### Database
db = SqliteDatabase(DB_FILE)
class BaseModel(Model):
    class Meta:
        database = db
db.create_tables([User, Drip])

# Hacky while loop in case praw throws 503 error
while True:

    # Main loop for processing comments
    print(f"********* Starting comment stream on {subreddit.display_name} / {subreddit.name} *********")
    for comment in subreddit.stream.comments(skip_existing=True):

        try:
        # hacky try/except to catch rate limiting errors from reddit praw

            print(f"****** new comment by {comment.author} at {datetime.datetime.utcnow()} begins: {comment.body[0:20]}")
            # Get users reddit id
            try:
                reddit_id = 't2_' + comment.author.id
                name = comment.author
                account_bday = datetime.datetime.fromtimestamp(comment.author.created_utc)
            except Exception as e:
                print(f"failed to get comment info with error: {e}")

            # If user exists get instance of them from db user table
            if check_if_user_exists(name):
                user = User.get(User.name == name)
                print(f"*** Found existing user: {name}")
            # If user doesn't exist create entry in table
            else:
                user = create_user(reddit_id, name, account_bday)
                print(f"*** Creating user: {name}")

            # Refresh the user if we didn't do it in last half day
            if (datetime.datetime.utcnow() - user.last_seen).seconds > 42069:
                user.refresh(datetime.datetime.utcnow(), web3nova, web3matic)

            # Check the comment for gas request
            if comment.body.split()[0].lower() == '!gas':
                print("!!! Found gas request")
                # Update user if we didn't just do it
                if (datetime.datetime.utcnow() - user.last_seen).seconds > 10:
                    user.refresh(datetime.datetime.utcnow(), web3nova, web3matic)
                # Handle request for Arbiturm Nova
                if comment.body.split()[1].lower() == 'nova':
                    user.dripCheck('nova', comment, web3nova)
                # Handle request for Polygon Matic
                elif comment.body.split()[1].lower() == 'matic':
                    user.dripCheck('matic', comment, web3matic)
                else:
                    comment.reply(body=comment_reply_gaserr(web3nova, web3matic))


            # Check the comment for stats request
            if comment.body.split()[0].lower() == '!stats':
                print("!!! Found stats request")
                if (datetime.datetime.utcnow() - user.last_stats_time).days > 1:
                    comment.reply(body=comment_reply_stats(web3nova, web3matic))
                    user.last_stats_time = datetime.datetime.utcnow()
                    user.save()

            # Sleep so we don't get rate limited on APIs hopefully
            time.sleep(1)

        except Exception as e:
            print(f"failed to process comment (probably rate limit): {e}")
