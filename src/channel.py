"""
This file contains the neccessary functions for the channel_ interactions
"""

import error
import database
import input_checkers

####################################################################
#
#                      Helper functions
#
#####################################################################

def is_user_channel_member(channel_id, u_id):
    """
    Helper function to check if a user is part of a channel
    """
    for selected_id in database.get_channel_data(channel_id)["member_ids"]:
        if selected_id == u_id:
            return True
    return False

####################################################################
#
#                      Channel Functions
#
#####################################################################

@input_checkers.validate_token
@input_checkers.validate_c_id
def channel_details(token, channel_id):
    """
    This function is given a valid token and channel_id.
    It then returns the name, owners and members of the channel
    """
    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)

    # check if user is a member of channel with channel_ID and return AccessError if not
    if is_user_channel_member(channel_id, curr_id) is False:
        raise error.AccessError(description="""You must be a member of the channel to view its
                                details.""")

    # now we return the name, owners and members of the channel
    details = {"name": "", "owner_members": [], "all_members": []}
    # for owner/all_members we need a list of dictionaries containing u_id, first name and last name
    # {"u_id": [], "name_first": "", "name_last": ""}

    channel = database.get_channel(channel_id)
    members = database.get_channel_data(channel_id)

    details["name"] = channel["name"]
    for user_id in members["owner_ids"]:

        owner_id = user_id
        user_data = database.get_user_data(owner_id)
        name_first = user_data["name_first"]
        name_last = user_data["name_last"]
        profile_img_url = user_data['profile_img_url']
        details["owner_members"].append({"u_id": owner_id, "name_first": name_first,
                                         "name_last": name_last,
                                         "profile_img_url": profile_img_url})

    for user_id in members["member_ids"]:
        member_id = user_id
        user_data = database.get_user_data(member_id)
        name_first = user_data["name_first"]
        name_last = user_data["name_last"]
        profile_img_url = user_data['profile_img_url']
        details["all_members"].append({"u_id": member_id, "name_first": name_first,
                                       "name_last": name_last,
                                       "profile_img_url": profile_img_url})

    return details

@input_checkers.validate_token
@input_checkers.validate_c_id
def channel_messages(token, channel_id, start):
    """
    Retrieve a set of 50 or less messages from the channel.
    Returns a {messages, start, end} dictionary.
    """
    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)

    # check if user is a member of channel with channel_ID and return AccessError if not
    if is_user_channel_member(channel_id, curr_id) is False:
        raise error.AccessError(description="user is not a member of this channel")

    #get channel data
    curr_channel = database.get_channel_data(channel_id)
    # find the length of messages
    messages_length = len(curr_channel["messages"])

    # if start is after the oldest message in messages InputError is raised
    # if messages is called and start is 0 on an empty channel, it returns an empty channel.
    # if start is after the oldest message in messages InputError is raised

    if messages_length <= start and (messages_length != 0 or start > 0):
        raise error.InputError(description="""The start value selected is
                               past the oldest message in the list""")

    if messages_length == 0 and start == 0:
        return {"messages": [], "start": start, "end": -1}

    # get the list of dictionaries 'message'
    curr_messages = curr_channel["messages"]
    messages_returned = []

    end = start + 50
    num_msgs_to_check = messages_length - start

    # If end is larger than the total no. of messages,
    # the function will print till end and return -1
    if num_msgs_to_check < 50:

        counter = 0
        while counter < num_msgs_to_check:
            target_message_index = start + counter
            messages_returned.append(curr_messages[target_message_index])
            counter += 1

        end = -1
    # else if end is within total no of messages,
    # function will print 50 messaages from start and return start + 50
    else:
        # loop to add each message to return up till 50 messages is returned
        counter = 0
        while counter < 50:
            target_message_index = start + counter
            messages_returned.append(curr_messages[target_message_index])
            counter += 1

    for msg in messages_returned:
        for react in msg['reacts']:
            react['is_this_user_reacted'] = curr_id in react['u_ids']

    return {"messages": messages_returned, "start": start, "end": end}

@input_checkers.validate_token
@input_checkers.validate_c_id
def channel_leave(token, channel_id):
    """
    This function takes in a token and channel ID.
    if both are valid, it will then remove the member from channel
    """

    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)

    # check if user is a member of channel with channel_ID and return AccessError if not
    user_channel = is_user_channel_member(channel_id, curr_id)
    if user_channel is False:
        raise error.AccessError(description="user is not a member of this channel")

    # remove user with u_id from the channel (from member_ids)
    curr_channel = database.get_channel_data(channel_id)

    curr_channel["member_ids"].remove(curr_id)
    # if user is an owner it removes them as an owner as well
    for owner_id in curr_channel["owner_ids"]:
        if owner_id == curr_id:
            curr_channel["owner_ids"].remove(curr_id)

    database.set_channel_data(curr_channel)

@input_checkers.validate_token
@input_checkers.validate_c_id
def channel_join(token, channel_id):
    """
    this function is passed a valid token and channel_id.
    It adds the user associated with the token into the channel, unless the channel is private
    """

    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)

    # gets current channel data
    curr_channel = database.get_channel_data(channel_id)
    # gets the permissions of current user from database
    user_perms = database.get_permission_dict(curr_id)

    # checks if user is already a part of channel
    for user_id in curr_channel["member_ids"]:
        if curr_id == user_id:
            raise error.InputError(description="user is joining a channel user is already in")

    # this checks if the channel is empty (or new) in this case we make the new member an owner.
    if curr_channel["member_ids"] == []:
        # adds the user into channel_member
        curr_channel["member_ids"].append(curr_id)
        # adds the user into channel_owner
        curr_channel["owner_ids"].append(curr_id)
    # this checks if the user is an owner of the slacker
    # if they are they are given owner privelages in the channel
    # else they are a member
    elif user_perms["permission_id"] == 1:
        # adds the user into channel_member
        curr_channel["member_ids"].append(curr_id)
        # adds the user into channel_owner
        curr_channel["owner_ids"].append(curr_id)
    elif curr_channel["is_public"] is True:
        # adds the user into the channel_member
        curr_channel["member_ids"].append(curr_id)
    elif curr_channel["is_public"] is False:
        raise error.InputError(description="""channel_join recieved a channel_id
                               for a private channel""")

@input_checkers.validate_token
@input_checkers.validate_u_id
@input_checkers.validate_c_id
def channel_addowner(token, channel_id, u_id):
    """
    This function intakes the token of current authorised (auth) user, channel_id and a user u_id
    It then adds the user u_id as an owner of the channel,
    as long as the current auth user is an owner of slackr/channel
    """
    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)
    # gets current channel data
    curr_channel = database.get_channel_data(channel_id)
    # gets the permissions of current user from database
    user_perms = database.get_permission_dict(curr_id)

    # check if user u_id is already an owner of the channel and raise InputError if so
    # also checks to see if current auth user is a owner of channel

    # a counter to check if user is a member of the channel
    is_curr_owner = False
    for owner_id in curr_channel["owner_ids"]:
        if u_id == owner_id:
            raise error.InputError(description="user u_id is already an owner of this channel")
        # checks if curr_id is an owner of channel
        if curr_id == owner_id:
            is_curr_owner = True

    # checks if the user u_id is a member of the channel already
    is_u_member = False
    for member_id in curr_channel["member_ids"]:
        if u_id == member_id:
            is_u_member = True


    # if the auth user is an owner of the slackr, allow him to add u_id as owner of channel
    if is_u_member is True:
        if user_perms["permission_id"] == 1:
            # adds the user into channel_owner
            curr_channel["owner_ids"].append(u_id)
        # if the auth user is an owner of the channel, allow him to add u_id as owner of channel
        elif is_curr_owner is True:
            # adds the user into channel_owner
            curr_channel["owner_ids"].append(u_id)
        # else the auth user is not an owner and thus cannot use addowner
        else:
            raise error.AccessError(description="""current user is not an owner of the channel,
                                    or of the slackr""")

@input_checkers.validate_token
@input_checkers.validate_u_id
@input_checkers.validate_c_id
def channel_removeowner(token, channel_id, u_id):
    """
    This function intakes the token of current authorised (auth) user, channel_id and a user u_id
    It then removes the user u_id as an owner of the channel,
    as long as the current auth user is an owner of slackr/channel
    and the user u_id is an owner
    """
    # Check if token is valid and raise AccessError if not
    curr_id = database.get_current_user(token)
    # gets current channel data
    curr_channel = database.get_channel_data(channel_id)
    # gets the permissions of current user from database
    user_perms = database.get_permission_dict(curr_id)

    u_id_permission = database.get_permission_dict(u_id)
    if u_id_permission["permission_id"] == 1:
        raise error.AccessError(description="user being removed is the owner of the slackr")

    # checks if u_id is not an owner of the channel
    # also checks if current auth user is an owner of the channel
    is_u_owner = False
    is_curr_owner = False
    for owner_id in curr_channel["owner_ids"]:
        if u_id == owner_id:
            is_u_owner = True
        if curr_id == owner_id:
            is_curr_owner = True
    if is_u_owner is False:
        raise error.InputError(description="user being removed is not an owner of the channel")


    # if the auth user is owner of slackr, allows him to remove u_id as owner
    if user_perms["permission_id"] == 1:
        # removes the user from channel_owner
        curr_channel["owner_ids"].remove(u_id)
    # if the auth user is an owner of the channel, allow him to remove u_id as owner of channel
    elif is_curr_owner is True:
        # adds the user into channel_owner
        curr_channel["owner_ids"].remove(u_id)
    # else the auth user is not an owner and thus cannot use addowner
    else:
        raise error.AccessError(description="""Authorised user user is not an owner of the channel,
                                or of the slackr""")

@input_checkers.validate_token
@input_checkers.validate_c_id
@input_checkers.validate_u_id
def channel_invite(token, channel_id, u_id):
    """
    Invites a user (with user id u_id) to join a channel with
    ID channel_id. Once invited the user is added to the channel immediately
    """

    if database.get_current_user(token) not in database.get_channel_data(channel_id)['member_ids']:
        raise error.AccessError(description="""Authorised user is not
                                a member of channel with that channel_id.""")
    if u_id in database.get_channel_data(channel_id).get('member_ids'):
        raise error.InputError(description="This user is already a part of the channel.")

    new_channel_data = database.get_channel_data(channel_id)

    new_channel_data['member_ids'].append(u_id)
    if database.get_permission_dict(u_id).get('permission_id') == 1:
        new_channel_data['owner_ids'].append(u_id)

    database.set_channel_data(new_channel_data)

    return {}
