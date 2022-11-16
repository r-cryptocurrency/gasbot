from web3 import Web3
from gasbot.secrets import *
from gasbot.constants import *
from gasbot.user import *
from gasbot.drip import *

web3nova = Web3(Web3.HTTPProvider(RPC_URL_NOVA))
web3nova.isConnected()
signed_tx = build_tx(web3nova, MOON2gas_address, AN_ETH_AMT, NOVA_CHAIN_ID)
txid = web3nova.eth.send_raw_transaction(signed_tx.rawTransaction)
print(txid)