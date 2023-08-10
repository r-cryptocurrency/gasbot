from datetime import datetime
import requests
from peewee import *
from gasbot.secrets import priv_key
from gasbot.distribution_csv import check_address_in_csvs
import gasbot.comments as comments
import gasbot.constants as constants


db = SqliteDatabase(constants.DB_FILE)


class User(Model):
    id = AutoField()
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
            r = requests.get(f"{constants.REDDITPOINTS_URL}/wallets/{constants.rCC_SUBCODE}?userIds={self.reddit_id}")
            j = r.json()
            self.moon_balance = web3nova.fromWei(int(j[self.reddit_id]['amount']), 'ether')
            self.moon_earned = web3nova.fromWei(int(j[self.reddit_id]['amounts']['locked']['amount']), 'ether')
            r = requests.get(f"{constants.REDDITPOINTS_URL}/wallets/{constants.rFN_SUBCODE}?userIds={self.reddit_id}")
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
        from gasbot.drip import Drip
        print(f"*** Executing {network} drip check on {self.name}")
        # First check if user has a vault
        if self.has_vault == 0:
            comment.reply(comments.comment_reply_novault(self.name))
            return False
        # Second check if user has earned and holds a MOON or BRICK
        print((self.moon_balance > 1 and self.moon_earned > 1), (self.brick_balance > 1 and self.brick_earned > 1))
        if not ((self.moon_balance > 1 and self.moon_earned > 1) or
        (self.brick_balance > 1 and self.brick_earned > 1)):
            print(f"!!! Gas request denied because the user must have earned and hold at least 1 MOON or BRICK")
            comment.reply(comments.comment_reply_nopoints(self.name))
            return False
        # Third check if the account is more than 60 days old
        if ((datetime.utcnow() - self.account_bday).days < 60):
            print(f"!!! Gas request denied because account is less than 60 days old")
            comment.reply(comments.comment_reply_sixtydays(self.name))
            return False
        # Then proceed by network and check that:
        # 1) They don't have more than 100x faucet drip amount, and
        # 2) Last drip was more than days_since_last_req days ago
        if network == 'nova':
            if self.novaETH_balance > constants.TOO_RICH_MULTIPLIER*constants.AN_ETH_AMT:
                print("!!! Gas request denied because too rich")
                comment.reply(comments.comment_reply_toomucheth(self.name, self.address, self.novaETH_balance))
                return False     
            if (datetime.utcnow() - self.last_nova_drip).days >= constants.DAYS_SINCE_LAST_DRIP_REQ:
                print("!!!!!! Dripping that ETH.......")
                # calculate drip multiplier based on distribution history
                drip_multiplier = get_drip_multiplier(self)
                signed_tx = build_tx(web3, self.address, constants.AN_ETH_AMT, constants.NOVA_CHAIN_ID)
                txid = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                comment.reply(comments.comment_reply_sendeth(self.name, drip_multiplier, self.address, web3.toHex(txid)))
                self.last_nova_drip = datetime.utcnow()
                self.nova_drips += 1
                self.save()
                drip = Drip.create(reddit_id = self.reddit_id,
                                    user = self,
                                    drip_date = datetime.utcnow(),
                                    gas_type = 'nova',
                                    amount = constants.AN_ETH_AMT * drip_multiplier)
                return True
            else:
                comment.reply(comments.comment_reply_novathirty(self.name, self.last_nova_drip))
                print("!!! Gas request denied because too recent")
                return False                
        if network == 'matic':
            if self.polygonMATIC_balance > constants.TOO_RICH_MULTIPLIER*constants.P_MATIC_AMT:
                print("!!! Gas request denied because too rich")
                comment.reply(comments.comment_reply_toomuchmatic(self.name, self.address, self.polygonMATIC_balance))
                return False 
            if (datetime.utcnow() - self.last_matic_drip).days >= constants.DAYS_SINCE_LAST_DRIP_REQ:
                print("!!!!!! Dripping that MATIC.......")
                signed_tx = build_tx(web3, self.address, constants.P_MATIC_AMT, constants.MATIC_CHAIN_ID)
                txid = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                comment.reply(comments.comment_reply_sendmatic(self.name, self.address, web3.toHex(txid)))
                self.last_matic_drip = datetime.utcnow()
                self.matic_drips += 1
                self.save()
                drip = Drip.create(reddit_id = self.reddit_id,
                                   user = self,
                                   drip_date = datetime.utcnow(),
                                   gas_type = 'matic',
                                   amount = constants.P_MATIC_AMT)
                return True
            else:
                print("!!! Gas request denied because too recent")
                comment.reply(comments.comment_reply_maticthirty(self.name, self.last_matic_drip))
                return False  


def get_drip_multiplier(self):
    """
    Determines the size multiplier of the ETH drip for the user based on the following criteria:

    - Full Drip (multiplier: 1.0):
        - Present in the two most recent distribution CSVs with over 50 karma.
        - Moon earned/balance of at least 100.

    - Half Drip (multiplier: 0.5):
        - Present in the most recent distribution CSV with over 5 karma.
        - Moon earned/balance of at least 10.

    - Small Drip (multiplier: 0.2):
        - Has at least 1 moon or brick.

    Returns:
        float: Multiplier value (1.0, 0.5, 0.2) indicating the size of the drip the user qualifies for.
    """
    karma_in_current_csv, karma_in_previous_csv = check_address_in_csvs(self.address)

    if (karma_in_current_csv >= 50 and karma_in_previous_csv >= 50 and
        self.moon_balance >= 100 and self.moon_earned >= 100):
        print(f"full-drip authorized for {self.name}")
        return 1.0
    elif karma_in_current_csv >= 5 and self.moon_balance >= 10 and self.moon_earned >= 10:
        print(f"half-drip authorized for {self.name}")
        return 0.5
    else:
        print(f"basic drip authorized for {self.name}")
        return 0.2


def create_user(reddit_id, name, account_bday):
    user = User.create(reddit_id = reddit_id,
                        name = name,
                        account_bday = account_bday,
                        begin_date = datetime.utcnow(),
                        last_seen = datetime.fromtimestamp(0),
                        has_vault = 0,
                        address = '',
                        moon_balance = 0,
                        moon_earned = 0,
                        brick_balance = 0,
                        brick_earned = 0,
                        novaETH_balance = 0,
                        polygonMATIC_balance = 0,
                        last_nova_drip = datetime.fromtimestamp(0),
                        nova_drips = 0,
                        last_matic_drip = datetime.fromtimestamp(0),
                        matic_drips = 0,
                        last_stats_time = datetime.fromtimestamp(0)                           
                        )
    return user      


def check_if_user_exists(name):
    try:
        print(User.select().where(User.name == name).get())
        return True
    except:
        return False


def build_tx(web3, address, amount, chainid):
    tx = {
        'to': address,
        'gas': 40000,
        'value': web3.toWei(amount, 'ether'),
        'nonce': web3.eth.get_transaction_count(constants.MOON2GAS_ADDRESS),
        'chainId': chainid,
        }
    if chainid == constants.NOVA_CHAIN_ID:
        basefee = web3.fromWei(web3.eth.get_block('latest').baseFeePerGas, 'gwei')
        max_priority_fee_per_gas = 2
    elif chainid == constants.MATIC_CHAIN_ID:
        r = requests.get('https://gasstation-mainnet.matic.network/v2')
        j = r.json()
        basefee = j['estimatedBaseFee']
        max_priority_fee_per_gas = j['safeLow']['maxPriorityFee']
    gas_est = web3.eth.estimate_gas(tx)
    tx['gas'] = gas_est
    print(basefee)
    tx['maxFeePerGas'] = web3.toWei(basefee+max_priority_fee_per_gas, 'gwei')
    tx['maxPriorityFeePerGas'] = web3.toWei(max_priority_fee_per_gas, 'gwei') 
    print(tx)
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

