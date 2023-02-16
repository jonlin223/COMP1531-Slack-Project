"""
Implementation for other.py
"""
from operator import itemgetter
import error
import database
import channels
import input_checkers

@input_checkers.validate_token
def users_all(token):
    """
    returns a list of dictionaries for all users
    """
    # pylint: disable=unused-argument
    # NB: Supressed this warning because token is in fact used in
    # the decorator, however pylint doesn't check for this.
    users_list = ([usr for usr in database.get_users()
                   if database.get_permission_dict(usr['u_id']).get('permission_id') != 66])

    return {"users": users_list}

@input_checkers.validate_token
def search(token, query_str):
    """
    returns all messages that user is in with certain quesry string
    """
    if query_str == "":
        raise error.InputError(description="search received an empty query string")
    # user_channels = {'channels': [], []}
    user_channels = channels.channels_list(token)
    message_list = []
    for channel in user_channels['channels']:
        channel_data = database.get_channel_data(channel['channel_id'])
        for message in channel_data['messages']:
            if query_str in message['message']:
                message_list.append(message)
    message_list.sort(key=itemgetter('time_created'), reverse=True)
    return {"messages" : message_list}
