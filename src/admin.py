"""
File to handle all working with admin privileges in the Slackr.
"""

import database
import error
import input_checkers
import channel
import auth

VALID_PERMISSION_IDS = {"owner": 1, "member": 2}

@input_checkers.validate_token
@input_checkers.validate_u_id
def change_user_permission(token, u_id, permission_id):
    """
    Given a User by their user ID, set their permissions
    to new permissions described by permission_id
    """
    # Store u_id of person running command
    user_from_token = database.get_current_user(token)

    if permission_id not in VALID_PERMISSION_IDS.values():
        raise error.InputError(description="permission_id does not refer to a value permission")
    if (database.get_permission_dict(user_from_token).get("permission_id")
            != VALID_PERMISSION_IDS['owner']):
        # User is not a global owner.
        raise error.AccessError(description="The authorised user is not an owner")

    number_of_owners = 0
    for member in database.get_permissions_list():
        if member.get('permission_id') == VALID_PERMISSION_IDS['owner']:
            number_of_owners += 1

    if (u_id == user_from_token and number_of_owners == 1):
        # i.e. Owner calling this function is only owner.
        raise error.AccessError(description="Owner cannot remove" +
                                " permissions when he is the only owner")


    # Now, having checked for all errors, run function:
    database.set_permissions(u_id, permission_id)

@input_checkers.validate_token
@input_checkers.validate_u_id
def remove_user(token, u_id):
    """ Given a u_id, remove the user from the Slackr. """

    # we get the current user data
    terminator = database.get_current_user(token)

    # Raise AccessError if user is not an owner of the Slackr
    terminator_perm = database.get_permission_dict(terminator)
    if terminator_perm['permission_id'] != 1:
        raise error.AccessError(description="""Action cannot be performed
                                               because you are not a Slackr owner.""")

    # Do a soft remove
    # they stay a part of everything, but they are removed from owner/memberID
    # in channels, and they are also banned from ever logging in again.

    # we get the token of the user to be removed

    # introduce a new permission ID 66:
    # terminated and set the user to be removed to perm_id 66: terminated
    terminated_id = 66
    database.set_permissions(u_id, terminated_id)

    # remove the user from every channel's member_id and owner_id
    #first we call a list of every channel
    all_channels = database.get_channels()
    # we then get the data for each channel
    for each_channel in all_channels:
        channel_data = database.get_channel_data(each_channel["channel_id"])

        # remove user u_id from owner_ids
        for owner_id in channel_data['owner_ids']:
            if u_id == owner_id:
                channel.channel_removeowner(token, channel_data["channel_id"], u_id)

        # remove user u_id from member_ids
        if u_id in channel_data['member_ids']:
            channel_data['member_ids'].remove(u_id)
        database.set_channel_data(channel_data)

    # finally we log the user out of the session (invalidating terminated token)
    terminated_token = database.get_token_from_user(u_id)
    if terminated_token is not None:
        auth.auth_logout(terminated_token)
