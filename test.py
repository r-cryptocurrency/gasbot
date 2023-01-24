import datetime
import praw
import requests
import time
from peewee import *
from web3 import Web3
from gasbot.process_comment import process_comment
from gasbot.secrets import *
from gasbot.constants import *
from gasbot.user import *
from gasbot.comments import *
from gasbot.drip import *


db = SqliteDatabase(DB_FILE)
#### Database
db = SqliteDatabase(DB_FILE)
class BaseModel(Model):
    class Meta:
        database = db
db.create_tables([User, Drip])

data = Drip.select().where(Drip.gas_type == 'nova')
for u in data:
    print(u.user.name)

# web3nova = Web3(Web3.HTTPProvider(RPC_URL_NOVA))
# web3nova.isConnected()


# tx = {
#     'to': MOON2gas_address,
#     'value': web3nova.toWei(AN_ETH_AMT, 'ether'),
#     'nonce': web3nova.eth.get_transaction_count(MOON2gas_address),
#     'gas': 40000,
#     'chainId': NOVA_CHAIN_ID,
#     }


# gas_est = web3nova.eth.estimate_gas(tx)
# tx['gas'] = gas_est
# basefee = web3nova.fromWei(web3nova.eth.get_block('latest').baseFeePerGas, 'gwei')
# print(basefee)
# tx['maxFeePerGas'] = web3nova.toWei(basefee+2, 'gwei')
# tx['maxPriorityFeePerGas'] = web3nova.toWei(2, 'gwei') 
# print(tx)

# signed_tx = web3nova.eth.account.sign_transaction(tx, priv_key)

# txid = web3nova.eth.send_raw_transaction(signed_tx.rawTransaction)