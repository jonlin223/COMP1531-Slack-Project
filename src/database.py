"""
This file handles all data storage across the backend.
Data types and functions to get and set are maintained in here.

"""
from datetime import datetime
import threading
import time
import os
import json

import error

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../database')

###############################################################
#
#                        Database Files
#
###############################################################

# [ {u_id, email, name_first, name_last, handle_str, profile_img_url} , ... ]
USERS = []

# [ {u_id, permission_id} , ...]
USER_GLOBAL_PERMISSIONS_LIST = []

# [ {u_id, token} , {u_id, token} , ... ]
CURRENT_USERS = []

# [ {channel_id, name} , {channel_id, name} ]
CHANNELS = []

# [ {channel_id, owner_ids, member_ids, messages, is_public} , ... ]
CHANNEL_DATA_LIST = []

# [ {message_id, channel_id} , {message_id, channel_id} ]
MESSAGE_LOCATION_LIST = []

# [ {email, password} , {email, password} ]
PASSWORD_DATA_LIST = []

# {num_users}
NUM_USERS = {'num_users': 0}




###############################################################
#
#                        User Data
#
###############################################################

def get_users():
    """ Returns a the list of registered USERS. """
    return USERS

def get_user_data(u_id):
    """
    Returns the dictionary matching the ID provided.
    If no match, then will return None.
    """

    for user in USERS:
        if user['u_id'] == u_id:
            return user

    return None

def set_user_data(user):
    """ Adds/Updates the information stored for a user. """

    target_user = get_user_data(user['u_id'])
    if target_user is None:
        USERS.append(user)
    else:
        target_user['u_id'] = user['u_id']
        target_user['email'] = user['email']
        target_user['name_first'] = user['name_first']
        target_user['name_last'] = user['name_last']
        target_user['handle_str'] = user['handle_str']
        # target_user['profile_img_url'] = user['profile_img_url']


def set_current_user(u_id, token):
    """ Adds a current user to the current user database. """

    current_user = {'u_id': u_id, 'token': token}
    CURRENT_USERS.append(current_user)

def get_current_user(token):
    """ Given a token, returns the u_id of the user.
    If token is not valid, will return None.
    Can be used to check for valid tokens, raising AccessError. """

    for current_user in CURRENT_USERS:
        if token == current_user['token']:
            return current_user['u_id']
    return None

def get_token_from_user(u_id):
    """ Given a token, returns the token of the user.
    If u_id is not valid, will return None.
    """

    for current_user in CURRENT_USERS:
        if u_id == current_user['u_id']:
            return current_user['token']
    return None

def remove_current_user(token):
    """ Given a token, removes user who owns this token from CURRENT_USERS.
    Used to logout individuals.
    Returns True is user could be logged out, False otherwise. """

    for current_user in CURRENT_USERS:
        if token == current_user['token']:
            CURRENT_USERS.remove(current_user)
            return True
    return False

###############################################################
#
#                        Permission Data
#
###############################################################

def get_permissions_list():
    """Return the list of all registered users and their respective permissions"""
    return USER_GLOBAL_PERMISSIONS_LIST

def get_permission_dict(u_id):
    """
    Return the permission_dictionary for a particular user.

    Return None if the user doesn't exist.
    """
    for perm_dictionary in USER_GLOBAL_PERMISSIONS_LIST:
        if u_id == perm_dictionary['u_id']:
            return perm_dictionary

    return None

def set_permissions(u_id, permission_id):
    """
    If no entry exists for the u_id, create a new entry in
    USER_GLOBAL_PERMISSIONS_LIST with the specified u_id and
    permission_id.

    If an entry already exists, update the permission_id of the
    given u_id.
    """
    perm_dictionary = get_permission_dict(u_id)
    new_perm_dictionary = {"u_id": u_id, "permission_id": permission_id}
    if perm_dictionary is None:
        USER_GLOBAL_PERMISSIONS_LIST.append(new_perm_dictionary)
    else:
        perm_dictionary["permission_id"] = permission_id

###############################################################
#
#                        Channel Data
#
###############################################################

def get_channels():
    """ Returns dataType *CHANNELS* (all currently created CHANNELS) """
    return CHANNELS

def get_channel(channel_id):
    """ Returns the channel dictionary with the matching ID. """
    for channel in CHANNELS:
        if channel['channel_id'] == channel_id:
            return channel

    return None

def get_channel_data(channel_id):
    """ Returns the channel_data dictionary with the matching ID. """
    for channel_data in CHANNEL_DATA_LIST:
        if channel_data['channel_id'] == channel_id:
            return channel_data

    return None


def set_channel(channel):
    """
    Update the CHANNELS list with a name if it already exists

    If channel_id doesn't exist, new *channel* will be appended
    to the list, and a new entry will be made to CHANNEL_DATA_LIST
    with the same channel_id and empty parameters.
    """

    target_channel = get_channel(channel['channel_id'])

    if target_channel is not None:
        target_channel['name'] = channel['name']
    else:
        CHANNELS.append(channel)
        new_channel_data = {"channel_id": channel['channel_id'], "owner_ids": [],
                            "member_ids": [], "messages": [], "is_public": True}
        CHANNEL_DATA_LIST.append(new_channel_data)


def set_channel_data(channel_data):
    """
    If channel_id doesn't exist, raise InputError, otherwise:

    Create/update the data stored in channel_data of the given channel_ID.

    Messages passed into this function WILL NOT BE SAVED. To store messages
    in a channel you must explicitly use set_message.
    """

    target_channel_data = get_channel_data(channel_data['channel_id'])
    if target_channel_data is None:
        raise error.InputError(description="No entry in list 'CHANNELS' with ID supplied"
                                           " - create an entry in CHANNELS before creating"
                                           " one in CHANNEL_DATA_LIST.")

    target_channel_data['owner_ids'] = channel_data['owner_ids']
    target_channel_data['member_ids'] = channel_data['member_ids']
    target_channel_data['is_public'] = channel_data['is_public']


###############################################################
#
#                     MESSAGE Data
#
###############################################################

def get_message_locations():
    """ Return a list of all message_location dictionaries. """
    return MESSAGE_LOCATION_LIST

def get_message_location(message_id):
    """
    Given a message_id, return the message_location dictionary containing
    that ID, and the channel it is stored under
    """
    for message_location in MESSAGE_LOCATION_LIST:
        if message_location['message_id'] == message_id:
            return message_location

    return None

def get_message(message_id):
    """
    Return a message stored in channel.
    Returns None if no message is found with a matching message_id.
    """

    channel = get_message_location(message_id)

    if channel is None:
        return None

    channel_id = channel.get('channel_id')
    target_channel = get_channel_data(channel_id)

    target_message = {}
    for message in target_channel['messages']:
        if message['message_id'] == message_id:
            target_message = message
    return target_message

def set_message(channel_id, message):
    """
    Add/update a message stored in channel_data in CHANNEL_DATA_LIST.

    If the message is new, add a reference to its location in
    MESSAGE_LOCATION_LIST and PREPEND it to messages in channel_data.
    """

    target_message = get_message(message['message_id'])
    # i.e. Message exists already.
    time_create_date = datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    if target_message is not None:
        #experiment
        target_message['message'] = message['message']
        #target_message['time_created'] = time_create
        target_message['reacts'] = message['reacts']
        target_message['is_pinned'] = message['is_pinned']
    else:
        message['time_created'] = time_create
        target_channel = get_channel_data(channel_id)
        target_channel['messages'].insert(0, message)
        MESSAGE_LOCATION_LIST.append({"message_id": message['message_id'],
                                      "channel_id": channel_id})


def remove_message(message_id):
    """
    Delete entry from list of messages in relevant channel_data dictionary.
    Remove reference to location in message_location list.
    """

    channel_id = get_message_location(message_id).get('channel_id')
    target_channel_data = get_channel_data(channel_id)
    message_locations = get_message_locations()
    message_location = get_message_location(message_id)
    message_to_remove = {}

    for message in target_channel_data['messages']:
        if message['message_id'] == message_id:
            message_to_remove = message

    target_channel_data['messages'].remove(message_to_remove)
    message_locations.remove(message_location)


###############################################################
#
#                        Password Data
#
###############################################################

def get_password_data(user_email):
    """
    Return the dictionary storing {'email': ____, 'password': ____}
    whose email matches userEmail given.
    """
    for pwd_data in PASSWORD_DATA_LIST:
        if pwd_data['email'] == user_email:
            return pwd_data


    return None

def set_password(user_email, password):
    """
    Update the password element of the password_data dictionary
    for a certain user.
    """
    target_pwd_data = get_password_data(user_email)

    if target_pwd_data is None:
        PASSWORD_DATA_LIST.append({"email": user_email, "password": password})
    else:
        target_pwd_data['password'] = password

###############################################################
#
#                    NUM_USER FUNCTIONS
#
###############################################################

def generate_u_id():
    """ Tick NUM_USERS up by 1 and return new NUM_USERS. """

    NUM_USERS['num_users'] = NUM_USERS.get('num_users', 0) + 1

    return NUM_USERS['num_users']

###############################################################
#
#                 General Database Functions
#
###############################################################
def clear_database():
    """ Wipes the whole database clean."""
    USERS.clear()
    USER_GLOBAL_PERMISSIONS_LIST.clear()
    CURRENT_USERS.clear()
    CHANNELS.clear()
    CHANNEL_DATA_LIST.clear()
    MESSAGE_LOCATION_LIST.clear()
    PASSWORD_DATA_LIST.clear()
    NUM_USERS['num_users'] = 0

def transcribe_database():
    """
    Write the stored databases into a JSON file.
    """
    with open(os.path.join(DATABASE_PATH, "channel_data.json"), "w") as output:
        json.dump(CHANNEL_DATA_LIST, output)

    with open(os.path.join(DATABASE_PATH, "channels.json"), "w") as output:
        json.dump(CHANNELS, output)

    with open(os.path.join(DATABASE_PATH, "message_locations.json"), "w") as output:
        json.dump(MESSAGE_LOCATION_LIST, output)

    with open(os.path.join(DATABASE_PATH, "num_users.json"), "w") as output:
        json.dump(NUM_USERS, output)

    with open(os.path.join(DATABASE_PATH, "passwords.json"), "w") as output:
        json.dump(PASSWORD_DATA_LIST, output)

    with open(os.path.join(DATABASE_PATH, "users.json"), "w") as output:
        json.dump(USERS, output)

    with open(os.path.join(DATABASE_PATH, "permissions.json"), "w") as output:
        json.dump(USER_GLOBAL_PERMISSIONS_LIST, output)

    print("Transcribed database information to JSON files.")

def start_db_backup_scheduler():
    """
    Creates a daemon thread that will run transcribe database every
    30 seconds.
    """

    def transcribe_timed():
        """ Helper function to run the delayed loop on transcribe_database """
        while True:
            time.sleep(30)
            transcribe_database()

    backup_thread = threading.Thread(target=transcribe_timed)
    backup_thread.daemon = True
    backup_thread.start()


def retrieve_data_from_files():
    """
    Fetch information from the database files into
    the global variables.
    """
    with open(os.path.join(DATABASE_PATH, "channel_data.json"), "r") as output:
        data = json.load(output)
        CHANNEL_DATA_LIST.clear()
        CHANNEL_DATA_LIST.extend(data)

    with open(os.path.join(DATABASE_PATH, "channels.json"), "r") as output:
        data = json.load(output)
        CHANNELS.clear()
        CHANNELS.extend(data)

    with open(os.path.join(DATABASE_PATH, "message_locations.json"), "r") as output:
        data = json.load(output)
        MESSAGE_LOCATION_LIST.clear()
        MESSAGE_LOCATION_LIST.extend(data)

    with open(os.path.join(DATABASE_PATH, "num_users.json"), "r") as output:
        data = json.load(output)
        NUM_USERS['num_users'] = 0
        NUM_USERS['num_users'] = data['num_users']

    with open(os.path.join(DATABASE_PATH, "passwords.json"), "r") as output:
        data = json.load(output)
        PASSWORD_DATA_LIST.clear()
        PASSWORD_DATA_LIST.extend(data)

    with open(os.path.join(DATABASE_PATH, "users.json"), "r") as output:
        data = json.load(output)
        USERS.clear()
        USERS.extend(data)

    with open(os.path.join(DATABASE_PATH, "permissions.json"), "r") as output:
        data = json.load(output)
        USER_GLOBAL_PERMISSIONS_LIST.clear()
        USER_GLOBAL_PERMISSIONS_LIST.extend(data)
