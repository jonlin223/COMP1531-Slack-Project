""" Functions for hangman bot. """

import database
import channel

BOT_TOKEN = "thisisthetokenforthebot"
BOT_IMG = "http://127.0.0.1:8080/static/image0.jpg"

def register_bot():
    """ Bot is given the u_id of -1.
    Bot bypassed usual method of registration. """

    # Set the user details of the bot
    # Assumption is that No one will have the handle_str hangmanbot
    user = {'u_id': -1,
            'email': "hsascomp1531@gmail.com",
            'name_first': "Hangman",
            'name_last': "Bot",
            'handle_str': "hangmanbot",
            'profile_img_url': BOT_IMG}
    database.set_user_data(user)

    # Set the bot as an owner so it can join all channels
    database.set_permissions(-1, 1)

    # Add the bot to current users
    login_bot()

def login_bot():
    """ If bot is not in CURRENT_USERS but is in USERS,
    then simply add back to CURRENT_USERS """

    database.set_current_user(-1, BOT_TOKEN)

def call_bot(channel_id):
    """ Bot is registered if not a user.
    Bot is logged in if not logged in.
    Bot joins the channel if not a member of the channel. """

    if database.get_user_data(-1) is None:
        register_bot()
    elif database.get_token_from_user(-1) is None:
        login_bot()

    channel_data = database.get_channel_data(channel_id)
    if -1 not in channel_data['member_ids']:
        channel.channel_join(BOT_TOKEN, channel_id)

    return {"bot_id": -1}
