client_id = 'reddit_bot_id'
client_secret = 'reddit_bot_secret'
username = 'reddit_bot_username'
password = 'reddit_bot_password'
user_agent = 'praw44'

ethaccount = '0x....eth_address'
priv_key = b'bytestring'

##############################################################
######### To generate an ethaccount and priv_key you can #####
######### run the following code in interactive python shell #
######### and store output in client.py ethaccount/priv_key ##
# from web3 import Web3
# web3 = Web3(Web3.HTTPProvider('https://nova.arbitrum.io/rpc'))
# ethaccount = web3.eth.account.create()
# print(ethaccount._address, ethaccount._private_key)