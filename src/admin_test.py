"""
Tests for admin.py at the unit level.
"""

import pytest

import auth
import channel
import channels
import message
import error
import database
import admin

####################################################################
#
#                     Testing change_user_perms
#
#####################################################################

def test_perms_invalid_token():
    """
    Test that change permission with invalid token raises
    AccessError
    """
    with pytest.raises(error.AccessError):
        admin.change_user_permission(123123, 1, 1)

def test_perms_invalid_user():
    """
    Test that change permission with invalid u_id raises
    InputError
    """
    user = auth.auth_register("test@email.com", "password", "Barry", "Benson")
    with pytest.raises(error.InputError):
        admin.change_user_permission(user['token'], 213123, 1)

def test_perms_invalid_perm():
    """
    Test that change permission with invalid permission_id raises
    InputError
    """
    user = auth.auth_register("test@email.com", "password", "Barry", "Benson")
    with pytest.raises(error.InputError):
        admin.change_user_permission(user['token'], user['u_id'], 4)

def test_perms_not_owner():
    """
    Test that change permission with invalid permissions raises
    AccessError
    """
    # Global owner
    user = auth.auth_register("test@email.com", "password", "Barry", "Benson")
    # Global member
    user2 = auth.auth_register("test2@email.com", "password", "Barry", "Benson")

    with pytest.raises(error.AccessError):
        admin.change_user_permission(user2['token'], user['u_id'], 1)

def test_perms_single_owner():
    """
    Test that change permission with only one
    owner raises AccessError
    """
    user = auth.auth_register("test@email.com", "password", "Barry", "Benson")

    with pytest.raises(error.AccessError):
        admin.change_user_permission(user['token'], user['u_id'], 2)


def test_perms_valid():
    """
    Test the valid condition.
    """
    user = auth.auth_register("test@email.com", "password", "Barry", "Benson")
    user2 = auth.auth_register("test2@email.com", "password", "Barry", "Benson")

    admin.change_user_permission(user['token'], user2['u_id'], 1)

    assert database.get_permission_dict(user2['u_id']).get('permission_id') == 1

####################################################################
#
#                      Testing remove_user
#
####################################################################

def test_remove_user_nvt():
    """ Test if AccessError raised if token not valid. """

    user = auth.auth_register("email@email.com", "password", "Meh", "Emoji")

    with pytest.raises(error.AccessError):
        admin.remove_user("invalidtoken", user['u_id'])

def test_remove_user_not_owner():
    """ Test if AccessError raised if user not an owner of the Slackr. """

    user1 = auth.auth_register("email@email.com", "password", "Pepe", "Silvia")
    user2 = auth.auth_register("email2@email.com", "password", "Ongo", "Gablogian")

    with pytest.raises(error.AccessError):
        admin.remove_user(user2['token'], user1['u_id'])

def test_remove_user_invalid_target():
    """ Test if InputError raised if u_id does not refer to a valid user. """

    user = auth.auth_register("email@email.com", "password", "Ru", "Paul")

    with pytest.raises(error.InputError):
        admin.remove_user(user['token'], -100)

def test_remove_user():
    """
    Tests if user_remove correctly removes a user from the required parts of database:

    -retained in USERS, PASSWORD_DATA_LIST and in CHANNEL_DATA_LIST (for messages)
    -permission_id of user is now terminated (66)
    -removed from:
        CURRENT_USERS,
        CHANNELS[owner_id]/[member_ID],
    """

    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")

    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)

    # create a second user and add them to the channel as an owner
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    channel.channel_addowner(test_dict["token"], c_id_dict["channel_id"], test_dict_2["u_id"])

    # store our details before the leave
    details_before = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    # ensure there are two members: test_dict & test_dict_2
    assert len(details_before["all_members"]) == 2
    assert details_before["all_members"][0]["u_id"] == test_dict["u_id"]
    assert details_before["all_members"][1]["u_id"] == test_dict_2["u_id"]
    #ensure there are two owners: test_dict & test_dict_2
    assert len(details_before["owner_members"]) == 2
    assert details_before["owner_members"][0]["u_id"] == test_dict["u_id"]
    assert details_before["owner_members"][1]["u_id"] == test_dict_2["u_id"]

    # now we send a message to test rum ham
    message.message_send(test_dict_2["token"], c_id_dict["channel_id"], "hello world")
    # test that messages successfully returns the message
    sent_messages = channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 0)
    assert sent_messages["messages"][0]["message"] == "hello world"

    ######## Now we call the user_remove function:
    admin.remove_user(test_dict["token"], test_dict_2["u_id"])
    ########

    # we test that they still remain in user
    all_users = database.get_users()
    assert len(all_users) == 2
    assert all_users[0]["u_id"] == test_dict["u_id"]
    assert all_users[1]["u_id"] == test_dict_2["u_id"]

    # we test that their messages can still be printed
    messages_post_remove = channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 0)
    assert messages_post_remove["messages"][0]["message"] == "hello world"
    assert messages_post_remove["messages"][0]["u_id"] == test_dict_2["u_id"]

    # we test that their permission is changed to 66
    terminated_id = 66
    permissions_post_remove = database.get_permission_dict(test_dict_2["u_id"])
    assert permissions_post_remove["u_id"] == test_dict_2["u_id"]
    assert permissions_post_remove["permission_id"] == terminated_id

    # we test that they are no longer a part of CURRENT_USERS,
    assert database.get_current_user(test_dict_2["token"]) is None

    # we test that they are no longer a part of CHANNELS[owner_id]/[member_ID],
    details_after = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    # ensure there is one member: test_dict
    assert len(details_after["all_members"]) == 1
    assert details_after["all_members"][0]["u_id"] == test_dict["u_id"]
    # ensure there is one owner: test_dict
    assert len(details_after["owner_members"]) == 1
    assert details_after["owner_members"][0]["u_id"] == test_dict["u_id"]

    # we test that they are unable to log in again
    password_test = "qwertyuiop"
    with pytest.raises(error.AccessError):
        auth.auth_login("test2@email.com", "password2")

    # Test that the InputError raised when an unregistered email is entered
    # still takes priority over the AccessError of admin_user_remove.
    with pytest.raises(error.InputError):
        auth.auth_login("wroing@email.com", password_test)

    # Check incorrect password works stil
    with pytest.raises(error.AccessError):
        auth.auth_login("test2@email.com", password_test)

    with pytest.raises(error.InputError):
        auth.auth_login("wrongemailformat", password_test)
