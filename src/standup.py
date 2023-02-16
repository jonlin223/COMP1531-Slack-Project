""" File contains functions for standup """

from datetime import datetime, timedelta
from threading import Timer
import error
import database
from message import message_send
import input_checkers

# This dictionary will hold the queues where standup message are held
# format like {channel_id1: [], channel_id2: []}
# doing this so we can hold standups in multiple channels simultaneously
QUEUES = {}
# This list will hold the current channels where standups are active
# will hold dictionaries of the format:
# {channel_id, time_finish}
STANDUPS = []

def clean_standup_database():
    """ Helper function used in testing to clear QUEUES and STANDUPS """

    STANDUPS.clear()
    QUEUES.clear()

def standup_start_helper(channel_id, token):
    """ Helper function for standup_start.
    Scheduled to run by standup_start.
    Creates standup message in correct format and then send it. """

    message_queue = QUEUES[str(channel_id)]
    string = ""
    for message in message_queue:
        string += message + '\n'
    string = string.rstrip('\n')

    # call messages_send
    # Only call message_send if string is not empty so message_send does not raise exception
    if string != "":
        message_send(token, channel_id, string)

    # remove the standup from QUEUES and STANDUPS
    del QUEUES[str(channel_id)]
    for standup in STANDUPS:
        if standup['channel_id'] == channel_id:
            STANDUPS.remove(standup)

@input_checkers.validate_token
@input_checkers.validate_c_id
def standup_active(token, channel_id):
    """ Check if standup is active in channel give. """
    # pylint: disable=unused-argument
    # NB: Supressed this warning because token is in fact used in
    # the decorator, however pylint doesn't check for this.

    # Check if standup is active by looking though standups list
    is_active = False
    time_finish = None
    for standup in STANDUPS:
        if standup['channel_id'] == channel_id:
            is_active = True
            time_finish = standup['time_finish']

    return {'is_active': is_active, 'time_finish': time_finish}

@input_checkers.validate_token
@input_checkers.validate_c_id
def standup_start(token, channel_id, length):
    """ Start a standup in channel given """

    # Check if standup is currently active in this channel, if so raise InputError
    if standup_active(token, channel_id)['is_active'] is True:
        raise error.InputError(description="There is already a standup active in this channel")

    # Calculate time_finish to return
    now = datetime.now()
    dt_finish = now + timedelta(seconds=length)
    time_finish = dt_finish.timestamp()

    # Add details of standup to STANDUPS
    STANDUPS.append({'channel_id': channel_id,
                     'time_finish': int(time_finish)})

    # Add new message queue to QUEUES
    QUEUES[str(channel_id)] = []

    # Schedule when to send dump queue from QUEUES
    Timer(length, standup_start_helper, args=[channel_id, token]).start()

    return {'time_finish': int(time_finish)}

@input_checkers.validate_token
@input_checkers.validate_c_id
def standup_send(token, channel_id, message):
    """ Add a message to standup queue """

    # If token is valid, take u_id which is used to look through users
    u_id = database.get_current_user(token)

    # Check if user is member of channel that message is within
    # if not then raise an AccessError
    channel_data = database.get_channel_data(channel_id)
    if u_id not in channel_data['member_ids']:
        raise error.AccessError(description="You are not a member of this channel")

    # Check if message if more than 1000 characters long and raise InputError if that is the case
    if len(message) > 1000:
        raise error.InputError(description="The message entered is more than 1000 characters long")

    # Check if standup is currently active in channel, raise InputError if not
    if standup_active(token, channel_id)['is_active'] is False:
        raise error.InputError(description="There are no standups active in this channel")

    # Format message to "handle_str: message"
    handle_str = database.get_user_data(u_id)['handle_str']
    string = handle_str + ": " + message

    # Now add string to the appropriate list in queues
    QUEUES[str(channel_id)].append(string)

    return {}
