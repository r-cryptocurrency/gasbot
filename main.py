import datetime
import praw
import requests
import time
from apscheduler.schedulers.background import BackgroundScheduler
from peewee import *
from web3 import Web3
from gasbot.process_comment import process_comment
from gasbot.secrets import *
from gasbot.constants import *
from gasbot.user import *
from gasbot.comments import *
from gasbot.drip import *
from gasbot.distribution_csv import download_and_save_csv, calculate_snapshot_date


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

# Dowload and update distribution CSV every 28 days
scheduler = BackgroundScheduler(timezone="UTC")
download_and_save_csv()
scheduler.add_job(lambda: scheduler.add_job(download_and_save_csv, 'interval', days=28), 
                  trigger='date', run_date=calculate_snapshot_date())
scheduler.start()


# Main loop for processing comments
print(f"********* Starting comment stream on {subreddit.display_name} / {subreddit.name} *********")
for comment in subreddit.stream.comments(skip_existing=True):

    #try:
    # hacky try/except to catch rate limiting errors from reddit praw
        process_comment(comment, web3nova, web3matic)
        # Sleep so we don't get rate limited on APIs hopefully
        time.sleep(1)

    #except Exception as e:
    #    print(f"failed to process comment (probably rate limit): {e}")
