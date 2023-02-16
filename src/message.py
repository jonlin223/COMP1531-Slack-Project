"""
The file contain all message function.
"""
import time
from datetime import datetime
from error import InputError, AccessError
from database import (set_message,
                      get_message_location, remove_message, get_message, get_channel_data,
                      get_current_user, get_permission_dict
                     )
from channel import is_user_channel_member
import hangman
import input_checkers
import message_parser

###############################################################
#
#                        Helper Functions
#
###############################################################

def check_command(channel_id, message):
    """
    A helper function to check whether the message given is a command for hangman
    Start a hangman if the message is "/hangman" or make a guess if message is "/guess X"
    X i a single letter.
    """
    if message == "/hangman":
        hangman.hangman_start(channel_id)
        return True

    message_data = message.split()
    if message_data[0] == "/guess":
        if len(message_data) == 2 and len(message_data[1]) == 1:
            hangman.hangman_guess(message_data[1], channel_id)
        else:
            raise InputError(description='Incorrect guess format,' +
                             ' only one letter per guess is allowed')
        return True

    return False


def user_in_message_channel(message_id, u_id):
    """
    A helper function to check whether the user is in channel with channel_id provided
    Returns True if passes check - otherwise raises InputError.
    """
    message_location = get_message_location(message_id)
    channel_id = message_location["channel_id"]
    channel_data = get_channel_data(channel_id)
    check = False

    for user in channel_data["member_ids"]:
        if user == u_id:
            check = True
    if check is False:
        raise InputError(
            description='message_id is not a valid message within' +
            'a channel that the authorised user has joined')
    else:
        return check


###############################################################
#
#                        Message functions
#
###############################################################


# token check | channel_id check | user_in_channel check | msg_len check
@input_checkers.validate_token
@input_checkers.validate_c_id
def message_send(token, channel_id, message):
    """
    Grab information from the frontend chat bar and send it.
    """

    u_id = get_current_user(token)

    if is_user_channel_member(channel_id, u_id) is False:
        raise AccessError(description='The authorised user has not ' +
                          'joined the channel they are trying to post to')

    # raise error if the message is longer than 1000 or empty string is given.
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters')

    if message == '':
        raise InputError(description='Cannot send an empty message')

    # Now parse the message
    message_id = message_parser.parse_message(u_id, channel_id, message)
    check_command(channel_id, message)

    return {
        "message_id": message_id,
    }

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_remove(token, message_id):
    """
    Given a message_id for a message, this message is removed from the channel.
    """
    u_id = get_current_user(token)

    message_location = get_message_location(message_id)

    channel_id = message_location["channel_id"]
    channel_data = get_channel_data(channel_id)

    if u_id not in channel_data['member_ids']:
        raise AccessError(description="User must be a member of the channel they are trying" +
                          " to access.")

    # Find the message to be deleted. At this point
    #   The message definitely exists and the user is definitely a member of the channel
    #   it exists in.
    for message in channel_data["messages"]:
        if message['message_id'] == message_id:
            if message["u_id"] != u_id and get_permission_dict(u_id).get('permission_id') != 1:
                raise AccessError(description="Authorised user did not send the message " +
                                  "and is not a server/channel owner.")
            else:
                remove_message(message_id)

    return {}

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_edit(token, message_id, message):
    """
    Given a message, update it's text with new text.
    If the new message is an empty string, the message is deleted.
    """
    u_id = get_current_user(token)

    message_location = get_message_location(message_id)

    # if message is longer than 1000 an Inputerror should be raised.
    if len(message) > 1000:
        raise InputError(
            description='Message is more than 1000 characters or try to send an empty message')

    channel_id = message_location["channel_id"]
    channel_data = get_channel_data(channel_id)

    if u_id not in channel_data['member_ids']:
        raise AccessError(description="User must be a member of the channel they are trying" +
                          " to access.")

    # Find the message to be deleted (assume it definitely exists)
    msg_to_edit = next(msg for msg in channel_data['messages'] if msg['message_id'] == message_id)

    if msg_to_edit['u_id'] != u_id and get_permission_dict(u_id)['permission_id'] != 1:
        raise AccessError(description="Authorised user did not send the message " +
                          "and is not a server/channel owner.")

    if message == '':
        remove_message(message_id)
    else:
        msg_to_edit['message'] = message
        set_message(channel_id, msg_to_edit)

    return {}


@input_checkers.validate_token
@input_checkers.validate_c_id
def message_sendlater(token, channel_id, message, time_sent):
    """
    Send a message from authorised_user to the channel specified by
    channel_id automatically at a specified time in the future.
    """
    u_id = get_current_user(token)

    if is_user_channel_member(channel_id, u_id) is False:
        raise AccessError(description='The authorised user has not ' +
                          'joined the channel they are trying to post to')

    # raise error if the message is longer than 1000 or empty string is given.
    if len(message) > 1000:
        raise InputError(description='Message is more than 1000 characters')

    if message == '':
        raise InputError(description='Cannot send an empty message')

    time_now_datetime = datetime.now().replace(microsecond=0)
    time_now = time_now_datetime.timestamp()
    if time_now > time_sent:
        raise InputError(description='Time sent is a time in the past')
    else:
        # Run sendlater
        time_diff = time_sent - time_now

        time.sleep(time_diff)
        return message_send(token, channel_id, message)

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_react(token, message_id, react_id):
    """
    Given a message within a channel the authorised user is part of,
    add a "react" to that particular message.
    """

    u_id = get_current_user(token)

    # React_id check
    if react_id != 1:
        raise InputError(
            description='react_id is not a valid React ID.' +
            'The only valid react ID the frontend has is 1')

    # Check user is in channel they are reacting in and if they are,
    # execute.
    if user_in_message_channel(message_id, u_id) is True:
        message_file = get_message(message_id)
        u_id_to_react = next((i for i in message_file['reacts'][0]['u_ids'] if u_id == i), False)

        if u_id_to_react is not False:
            # This user has already reacted.
            raise InputError(
                description='Message with ID message_id already'
                + 'contains an active React with ID react_id')
        else:
            # User has not already reacted.
            message_file['reacts'][0]['u_ids'].append(u_id)

    return {}

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_unreact(token, message_id, react_id):
    """
    Given a message within a channel the authorised user is part of,
    remove a "react" to that particular message.
    """
    # Token check
    u_id = get_current_user(token)

    # React_id check
    if react_id != 1:
        raise InputError(
            description='react_id is not a valid React ID.' +
            'The only valid react ID the frontend has is 1')

    # Check user is in channel they are reacting in and if they are,
    # execute.
    if user_in_message_channel(message_id, u_id) is True:
        message_file = get_message(message_id)
        u_id_to_unreact = next((i for i in message_file['reacts'][0]['u_ids'] if u_id == i), None)

        if u_id_to_unreact is not None:
            # If there was a react from the user.
            message_file['reacts'][0]['u_ids'].remove(u_id)
        else:
            # If there wasn't a react from the user.
            raise InputError(
                description='Message with ID message_id does not'
                + 'contain an active React with ID react_id')

    return {}

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_pin(token, message_id):
    """
    Given a message within a channel, mark it as "pinned"
    to be given special display treatment by the frontend.
    """
    u_id = get_current_user(token)
    message_location = get_message_location(message_id)
    message_file = get_message(message_id)

    ################### START ERROR CHECKS ############################

    channel_data = get_channel_data(message_location['channel_id'])

    check = next((i for i in channel_data['member_ids'] if i == u_id), False)

    if check is False:
        raise AccessError(description='The authorised user is not ' +
                          'a member of the channel that the message is within')

    if u_id not in channel_data['owner_ids']:
        raise AccessError(description='The authorised user is not an owner')

    ##################### END ERROR CHECKS ########################

    if message_file['is_pinned'] is True:
        raise InputError(
            description='Message with ID message_id is already pinned')
    else:
        message_file['is_pinned'] = True

    return {}

@input_checkers.validate_token
@input_checkers.validate_msg_id
def message_unpin(token, message_id):
    """
    Given a message within a channel, remove it's mark as unpinned.
    """
    u_id = get_current_user(token)
    message_location = get_message_location(message_id)
    message_file = get_message(message_id)

    ################### START ERROR CHECKS ############################

    channel_data = get_channel_data(message_location['channel_id'])

    check = next((i for i in channel_data['member_ids'] if i == u_id), False)

    if check is False:
        raise AccessError(description='The authorised user is not ' +
                          'a member of the channel that the message is within')

    if u_id not in channel_data['owner_ids']:
        raise AccessError(description='The authorised user is not an owner')

    ##################### END ERROR CHECKS ########################

    if message_file['is_pinned'] is False:
        raise InputError(description='Message with ID message_id is already unpinned')
    else:
        message_file['is_pinned'] = False
    return {}
