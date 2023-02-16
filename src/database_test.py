"""
Test file to cover cases not covered by all other file tests.

In most cases these tests are checking issues that are checked for
in database.py which prevent other coders from improperly using the functions
provided.
"""
import pytest
import database
import auth
import channels
import channel
import error


def test_remove_token_invalid_token():
    """
    Token Database called with invalid token
    """
    assert database.remove_current_user(11121235) is False

def test_get_perms_list():
    """
    Perms database called with invalid u_id
    """
    assert database.get_permissions_list() == []

def test_set_perms_invalid_id():
    """ Invalid u_id given to set_perms """
    auth.auth_register("email@email.com", "password", "Bob", "Will")
    user2 = auth.auth_register("email2@email.com", "password", "Bobby", "Will")

    database.set_permissions(user2['u_id'], 1)

    assert database.get_permission_dict(user2['u_id']).get('permission_id') == 1

def test_channel_change_name():
    """ Test that update channel name works """
    user = auth.auth_register("email@email.com", "password", "Bob", "Will")
    c_id_dict = channels.channels_create(user['token'], "test_channel", True)

    assert channel.channel_details(user['token'], c_id_dict['channel_id'])['name'] == 'test_channel'

    new_channel = {'channel_id': c_id_dict['channel_id'], "name": "Billy"}

    database.set_channel(new_channel)

    assert channel.channel_details(user['token'], c_id_dict['channel_id'])['name'] == 'Billy'

def test_channel_data_modify_early():
    """
    Test that if channel_data is directly modified without channel
    being created first an error is raised.
    """
    with pytest.raises(error.InputError):
        database.set_channel_data({'channel_id': 1234123, "owner_ids": [], "member_ids": [],
                                   "messages": [], "is_public": True})

def test_get_message_not_found():
    """ Non-existent message_id_entered """
    assert database.get_message(112341423) is None


def test_update_password():
    """ Update a password test """
    auth.auth_register("email@email.com", "password4", "test", "name")

    database.set_password("email@email.com", "anotherPassword23")
    assert database.get_password_data("email@email.com")['password'] == "anotherPassword23"
