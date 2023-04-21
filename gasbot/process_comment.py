import datetime
from gasbot.comments import comment_reply_gaserr, comment_reply_stats
from gasbot.user import User, check_if_user_exists, create_user


def process_comment(comment, web3nova, web3matic):
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
        #if (datetime.datetime.utcnow() - user.last_stats_time).days > 1:
        comment.reply(body=comment_reply_stats(web3nova, web3matic))
        user.last_stats_time = datetime.datetime.utcnow()
        user.save()
        
    # Check the comment for help request
    if comment.body.split()[0].lower() == '!help':
        print("!!! Found help request")
        comment.reply(body=comment_reply_gaserr(web3nova, web3matic))
        
