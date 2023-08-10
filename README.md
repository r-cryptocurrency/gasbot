# MOON2gas Reddit bot faucet for Arbitrum Nova and Polygon

## Intro

This is a bot that operates as a reddit user u/MOON2gas, and will dispense
small amounts of Arbitrum Nova ETH or Polygon MATIC to qualified redditors.
These two networks/cryptocurrencies are used on Reddit for Reddit Community
Points (MOONs and BRICKs) on Arbitrum Nova and for Reddit Collecticle Avatars
(NFTs for profile) on Polygon. 

Reddit is currently doing its best to lock these assets
onto their platform's "Vault" (a crypto wallet built into their official mobile apps) 
and not allow users to easily transfer these digital assets out of their Vault. 
One way they do this is by distributing these ERC20 and ERC1155 
tokens to users without providing them any gas to move the tokens around 
on the network (whether that is to tip another user or sell an asset on an exchange). 

So, this bot helps users get some gas if they want to learn a bit more about how 
these assets can be moved out of their Vault and around the network into other
non-Reddit wallets or exchanges or gambling websites or whatever.

## Commands

Commands must be issued as comments in the [r/CryptoCurrencyMoons] subredditi
for the bot to detect them. Currently there are three commands:

* `!gas nova`  
* `!gas matic`  
* `!stats`

Each command should be entered as a comment beginning with one of the above 
on a post in in r/CryptoCurrencyMoons. 

## Eligibility

Currently the reddit user requesting a payout (drip) from the faucet must have: 

* A 60 day old reddit account  
* Must have earned and still hold at least one MOON or BRICK
* Users can only get one faucet drip per network every 30 days

In the future I would like to allow Collectible Avatar holders to request payout 
as well, but that is not currently implemented.

## Payouts

The faucet is currently paying out:

* 0.00004 ETH on Arbitrum Nova network (enough to cover 30-50 MOON transfers)
* 0.04 MATIC on Polygon network (enough to cover 2-4 NFT transfers)

## Code

There are definitely improvements that could be made in tx sending and fee estimation
I think, but happy to have any pull requests.

## Feed the bot

If you want to donate gas for the faucet you can send ETH on Arbitrum Nova network
or MATIC on Polygon network to the following address:

> 0x09bb9a6676A879f3Af8AF9751D72ab00d9950bbF

This code is free for anyone to use for any purpose without reservation.
