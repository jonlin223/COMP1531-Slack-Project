""" File to handle parsing of messages to the database. """

import database

def set_reacts():
    """
    A helper function to set the default reacts in a message.
    """
    return {
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False
    }

def create_message(u_id, message):
    """
    A helper function which generates the message_id and returns a dictionary
    containing this new id, the u_id who called it and the message.
    """
    message_location_list = database.get_message_locations()
    if message_location_list != []:
        new_message_id = message_location_list[-1]['message_id'] + 1
    else:
        new_message_id = 0
    return {
        'message_id': new_message_id,
        'u_id': u_id,
        'message': message,
        'time_created': 0,
        'reacts': [set_reacts()],
        'is_pinned': False
    }

def parse_message(u_id, channel_id, message):
    """
    A function which will generate a message_id and immediately send
    that message to the database.
    """
    message_file = create_message(u_id, message)
    database.set_message(channel_id, message_file)
    return message_file['message_id']
