import datetime
from gasbot.drip import get_nova_drips, get_matic_drips
import gasbot.constants as constants

def comment_reply_gaserr(web3nova, web3matic):
    reply = f"""Please select either Arbitrum Nova or Polygon 
network faucet by using either the `!gas nova` or  `!gas matic` command if 
you would like to receive a drip of gas from the faucet.  

**Currently dispensing:**  
* Up to {constants.AN_ETH_AMT} ETH on Arbitrum Nova network *(amount depends on previous activity and moons earned)*  
* Up to {constants.P_MATIC_AMT} MATIC on Polygon network *(amount depends on previous activity and moons earned)*  

**Remaining Balances:**  
* {web3nova.fromWei(web3nova.eth.get_balance(constants.MOON2GAS_ADDRESS), 'ether')} ETH on Arbitrum Nova  
* {web3nova.fromWei(web3matic.eth.get_balance(constants.MOON2GAS_ADDRESS), 'ether')} MATIC on Polygon"""
    return reply


def comment_reply_stats(web3nova, web3matic):
    nova_drips, nova_users, nova_amt = get_nova_drips()
    matic_drips, matic_users, matic_amt = get_matic_drips()

    reply = f"""Some stats from the u/MOON2gas faucet:  

**Currently dispensing:**  
* Up to {constants.AN_ETH_AMT} ETH on Arbitrum Nova network *(amount depends on previous activity and moons earned)*  
* Up to {constants.P_MATIC_AMT} MATIC on Polygon network *(amount depends on previous activity and moons earned)*  

**Remaining Balances:**  
* {web3nova.fromWei(web3nova.eth.get_balance(constants.MOON2GAS_ADDRESS), 'ether'):.4f} ETH on Arbitrum Nova  
* {web3nova.fromWei(web3matic.eth.get_balance(constants.MOON2GAS_ADDRESS), 'ether'):.4f} MATIC on Polygon  

**Drips sent:**  
* {nova_amt} ETH dispensed in {nova_drips} drips of Arbitrum Nova ETH to {nova_users} unique redditors  
* {matic_amt} MATIC dispensed in {matic_drips} drips of Polygon MATIC to {matic_users} unique redditors
"""
    return reply


def comment_reply_novault(name):
    reply = f"""Hi u/{name}, in order to use this faucet bot 
you must [have created a vault](https://reddit.zendesk.com/hc/en-us/articles/7558997757332-Reddit-Vault-Basics).""" 
    return reply


def comment_reply_nopoints(name):
    reply = f"""Hi u/{name}, in order to use this faucet bot 
you must [have earned at least one MOON or BRICK](https://www.reddit.com/community-points/)
on r/CryptoCurrency or r/FortNiteBR.""" 
    return reply


def comment_reply_toomucheth(name, address, balance):
    reply = f"""Hi u/{name}, 
your address {address} has an Arbitrum Nova ETH balance, 
{balance} ETH, that is more than {constants.TOO_RICH_MULTIPLIER}x the amount being dispensed
from the faucet right now, only {constants.AN_ETH_AMT} ETH at this time.
"""
    return reply


def comment_reply_toomuchmatic(name, address, balance):
    reply = f"""Hi u/{name}, 
your address {address} has a Polygon MATIC balance, 
{balance} MATIC, that is more than {constants.TOO_RICH_MULTIPLIER}x the amount 
being dispensed from the faucet right now, 
only {constants.P_MATIC_AMT} MATIC at this time.
"""
    return reply


def comment_reply_sendeth(name, multiplier, address, txid):
    reply = f"""Hi u/{name}, {constants.AN_ETH_AMT * multiplier} ETH has been sent
on the Arbitrum Nova Network to your [vault address](https://nova-explorer.arbitrum.io/address/{address}) 
in [txid](https://nova-explorer.arbitrum.io/tx/{txid})". 

You will be eligible for another drip from the Arbitrum Nova
faucet in {constants.DAYS_SINCE_LAST_DRIP_REQ} days.

If you appreciate this service, you can tip me a MOON or BRICK, or you
can donate Arbitrum Nova ETH or Polygon MATIC to the following address: 

{constants.MOON2GAS_ADDRESS} """
    return reply


def comment_reply_sendmatic(name, multipier, address, txid):
    reply = f"""Hi u/{name}, {constants.P_MATIC_AMT * multipier} MATIC has been sent
on the Polygon Network to your [vault address](https://polygonscan.com/address/{address}) 
in [txid](https://polygonscan.com/tx/{txid}). 

You will be eligible for another drip from the Polygon MATIC
faucet in {constants.DAYS_SINCE_LAST_DRIP_REQ} days.

If you appreciate this service, you can tip me a MOON or BRICK, or you
can donate Arbitrum Nova ETH or Polygon MATIC to the following address: 

{constants.MOON2GAS_ADDRESS} """
    return reply


def comment_reply_sixtydays(name):
    reply = f"""Hi u/{name}, in order to use this bot 
your account must be at least 60 days old AND you must have at least
one MOON that you earned by participating in r/CryptoCurrency or one BRICK
that you earned by participating in r/FortNiteBR."""
    return reply


def comment_reply_novathirty(name, last_drip):
    reply = f"""Hi u/{name}, you can only use this 
Arbitrum Nova ETH faucet once every {constants.DAYS_SINCE_LAST_DRIP_REQ} days. You last received a drip
{(datetime.datetime.utcnow() - last_drip).days} days ago """
    return reply


def comment_reply_maticthirty(name, last_drip):
    reply = f"""Hi u/{name}, you can only use this 
Polygon MATIC faucet once every {constants.DAYS_SINCE_LAST_DRIP_REQ} days. You last received a drip
{(datetime.datetime.utcnow() - last_drip).days} days ago """
    return reply 

def comment_reply_stats_too_often(name):
    reply = f"Hi u/{name}, you can only use the ```!stats``` command once per hour. Please try again later."
    return reply