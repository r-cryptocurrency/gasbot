import datetime
import requests
from peewee import *
from gasbot.constants import *
from gasbot.secrets import *
from gasbot.drip import *
from gasbot.comments import *


db = SqliteDatabase(DB_FILE)


class User(Model):
    reddit_id = CharField()
    name = CharField()
    account_bday = DateTimeField()
    begin_date = DateTimeField()
    last_seen = DateTimeField()
    has_vault = IntegerField()
    address = CharField()
    moon_balance = FloatField()
    moon_earned = FloatField()
    brick_balance = FloatField()
    brick_earned = FloatField()
    novaETH_balance = FloatField()
    polygonMATIC_balance = FloatField()
    last_nova_drip = DateTimeField()
    nova_drips = IntegerField()
    last_matic_drip = DateTimeField()
    matic_drips = IntegerField()
    last_stats_time = DateTimeField()
    
    class Meta:
            database = db
    
    def refresh(self, last_seen, web3nova, web3matic):
        print(f"*** Refreshing user: {self.name}")
        # Get vault info
        try:
            r = requests.get(f"{REDDITPOINTS_URL}/wallets/{rCC_SUBCODE}?userIds={self.reddit_id}")
            j = r.json()
            self.moon_balance = web3nova.fromWei(int(j[self.reddit_id]['amount']), 'ether')
            self.moon_earned = web3nova.fromWei(int(j[self.reddit_id]['amounts']['locked']['amount']), 'ether')
            r = requests.get(f"{REDDITPOINTS_URL}/wallets/{rFN_SUBCODE}?userIds={self.reddit_id}")
            j = r.json()
            self.brick_balance = web3nova.fromWei(int(j[self.reddit_id]['amount']), 'ether')
            self.brick_earned = web3nova.fromWei(int(j[self.reddit_id]['amounts']['locked']['amount']), 'ether')
            self.address = j[self.reddit_id]['publicAddress']
            self.has_vault = True
            self.novaETH_balance = web3nova.fromWei(web3nova.eth.getBalance(self.address), 'ether')
            self.polygonMATIC_balance = web3nova.fromWei(web3matic.eth.getBalance(self.address), 'ether')
        except Exception as e:
            self.has_vault = False
            print(f"failed to get reddit vault info with error: {e}") 
        self.last_seen = last_seen
        self.save()
        print(f"* User {self.name} with {self.moon_balance} MOON and {self.brick_balance} BRICK updated at {self.last_seen}")
    
    def dripCheck(self, network, comment, web3):
        print(f"*** Executing {network} drip check on {self.name}")
        print_user(self)
        # First check if user has a vault
        if self.has_vault == 0:
            comment.reply(comment_reply_novault(self.name))
            return False
        # Second check if user has earned and holds a MOON or BRICK
        print((self.moon_balance > 1 and self.moon_earned > 1), (self.brick_balance > 1 and self.brick_earned > 1))
        if not ((self.moon_balance > 1 and self.moon_earned > 1) or
        (self.brick_balance > 1 and self.brick_earned > 1)):
            print(f"!!! Gas request denied because no points")
            comment.reply(comment_reply_nopoints(self.name))
            return False
        # Third check if the account is more than 60 days old
        if ((datetime.datetime.utcnow() - self.account_bday).days < 60):
            print(f"!!! Gas request denied because too young")
            comment.reply(comment_reply_sixtydays(self.name))
            return False
        # Then proceed by network and check that:
        # 1) They don't have more than 100x faucet drip amount, and
        # 2) Last drip was more than 30 days ago
        if network == 'nova':
            if self.novaETH_balance > 1000*AN_ETH_AMT:
                print("!!! Gas request denied because too rich")
                comment.reply(comment_reply_toomucheth(self.name, self.address, self.novaETH_balance))
                return False     
            if (datetime.datetime.utcnow() - self.last_nova_drip).days > 30:
                print("!!!!!! Dripping that ETH.......")
                signed_tx = build_tx(web3, self.address, AN_ETH_AMT, NOVA_CHAIN_ID)
                txid = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                comment.reply(comment_reply_sendeth(self.name, self.address, web3.toHex(txid)))
                self.last_nova_drip = datetime.datetime.utcnow()
                self.nova_drips += 1
                self.save()
                drip = Drip.create(reddit_id = self.reddit_id,
                                    name = self.name,
                                    drip_date = datetime.datetime.utcnow(),
                                    gas_type = 'nova')
                return True
            else:
                comment.reply(comment_reply_novathirty(self.name, self.last_nova_drip))
                print("!!! Gas request denied because too recent")
                return False                
        if network == 'matic':
            if self.polygonMATIC_balance > 1000*P_MATIC_AMT:
                print("!!! Gas request denied because too rich")
                comment.reply(comment_reply_toomuchmatic(self.name, self.address, self.polygonMATIC_balance))
                return False 
            if (datetime.datetime.utcnow() - self.last_matic_drip).days > 30:
                print("!!!!!! Dripping that MATIC.......")
                signed_tx = build_tx(web3, self.address, P_MATIC_AMT, MATIC_CHAIN_ID)
                txid = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                comment.reply(comment_reply_sendmatic(self.name, self.address, web3.toHex(txid)))
                self.last_matic_drip = datetime.datetime.utcnow()
                self.matic_drips += 1
                self.save()
                drip = Drip.create(reddit_id = self.reddit_id,
                                    name = self.name,
                                    drip_date = datetime.datetime.utcnow(),
                                    gas_type = 'matic')
                return True
            else:
                print("!!! Gas request denied because too recent")
                comment.reply(comment_reply_maticthirty(self.name, self.last_matic_drip))
                return False  

    
def create_user(reddit_id, name, account_bday):
    user = User.create(reddit_id = reddit_id,
                        name = name,
                        account_bday = account_bday,
                        begin_date = datetime.datetime.utcnow(),
                        last_seen = datetime.datetime.fromtimestamp(0),
                        has_vault = 0,
                        address = '',
                        moon_balance = 0,
                        moon_earned = 0,
                        brick_balance = 0,
                        brick_earned = 0,
                        novaETH_balance = 0,
                        polygonMATIC_balance = 0,
                        last_nova_drip = datetime.datetime.fromtimestamp(0),
                        nova_drips = 0,
                        last_matic_drip = datetime.datetime.fromtimestamp(0),
                        matic_drips = 0,
                        last_stats_time = datetime.datetime.fromtimestamp(0)                           
                        )
    return user      


def check_if_user_exists(name):
    try:
        print(User.select().where(User.name == name).get())
        return True
    except:
        return False


def build_tx(web3, address, amount, chainid):
    if chainid == NOVA_CHAIN_ID:
        mfpg, mpfpg = 50, 5
    else:
        mfpg, mpfpg = 250, 50
    tx = {
        'to': address,
        'maxFeePerGas': web3.toWei(mfpg, 'gwei'),
        'maxPriorityFeePerGas': web3.toWei(mpfpg, 'gwei'),
        'gas': 21762,
        'value': web3.toWei(amount, 'ether'),
        'nonce': web3.eth.get_transaction_count(MOON2gas_address),
        'chainId': chainid,
        }
    signed_tx = web3.eth.account.sign_transaction(tx, priv_key)
    return signed_tx

def print_user(user):
    print(user.name)
    print(user.account_bday)
    print(user.last_seen)
    print(user.has_vault)
    print(user.address)
    print(user.moon_balance)
    print(user.brick_balance)