""" File contains channels functions """

import error
import database
from channel import channel_join
import input_checkers

@input_checkers.validate_token
def channels_list(token):
    """ Returns {channels}, where channels is a list of channels that the user is part of.
    i.e. {'channels': [{channel_id, name}, {channel_id, name}]} """

    u_id = database.get_current_user(token)

    output = {'channels': []}

    # obtain channels so that I can see lists of members
    # insert channel into the output list if user is a member
    for channel in database.get_channels():
        channeldata = database.get_channel_data(channel['channel_id'])
        if u_id in channeldata['member_ids']:
            output['channels'].append(channel)

    return output

@input_checkers.validate_token
def channels_listall(token):
    """  Returns {channels}, where channels is a list of all channels
    i.e. {'channels': [{channel_id, name}, {channel_id, name}]} """
    # pylint: disable=unused-argument
    # NB: Supressed this warning because token is in fact used in
    # the decorator, however pylint doesn't check for this.

    output = {'channels': []}
    for channel in database.get_channels():
        output['channels'].append(channel)

    return output

@input_checkers.validate_token
def channels_create(token, name, is_public):
    """ Create a channel using the given parameters """

    # Check if name is more than 20 characters long and return InputError if this is the case
    if len(name) > 20:
        raise error.InputError(description="The name you entered is more than 20 characters long")

    # Generate a channel_id for the new channel
    # Simply done in order of time of creation (1..)
    # Generation of channel_id will be done in this way as long as ability to delete channels
    # remains unimplemented
    num_channels = len(database.get_channels())
    channel_id = num_channels + 1

    # Use database.set_channel to create channel in the database
    channel = {'channel_id': channel_id, 'name': name}
    database.set_channel(channel)
    channel_data = database.get_channel_data(channel_id)
    channel_data['is_public'] = is_public
    database.set_channel_data(channel_data)

    # User who creates the channel joins it automatically
    channel_join(token, channel_id)

    return {'channel_id': channel_id}
