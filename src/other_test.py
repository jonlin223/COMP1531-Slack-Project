"""
Tests for search and users/all
"""
import datetime
import pytest
import channels
import other
import error
import auth
import message_test
import message
import message_parser

def test_users_all_valid():
    """
    Checks users all returns the valid type.
    """
    user = auth.auth_register("email@email.com", "password", "Doom", "Slayer")
    auth.auth_register("email1@email.com", "password", "Walter", "White")

    assert other.users_all(user['token']) == {"users": [{"u_id": 1,
                                                         "email": "email@email.com",
                                                         "name_first": "Doom",
                                                         "name_last": "Slayer",
                                                         "profile_img_url": auth.DEFAULT_USER_IMG,
                                                         "handle_str": "doomslayer"},
                                                        {"u_id": 2,
                                                         "email": "email1@email.com",
                                                         "name_first": "Walter",
                                                         "name_last": "White",
                                                         "profile_img_url": auth.DEFAULT_USER_IMG,
                                                         "handle_str": "walterwhite"}]}

def test_users_all_invalid_token():
    """
    Check for AccessError when invalid token
    calls users_all
    """
    login_session = auth.auth_register("email@email.com", "password", "John", "Reese")
    auth.auth_logout(login_session.get('token'))
    with pytest.raises(error.AccessError):
        other.users_all(login_session.get('token'))

# For search, Assume the search function will only return the message that contain query .
# eg. query = 'AAast' the message ='AAast' will be return and
# message = 'AAast1234' will also be return.
# Assuming that if the empty string is searched, It should return InputError


def test_search():
    """
    test search function will worke under correct condition
    """
    user_infor = auth.auth_register("email@email.com", "password", "Min", "Li")
    channel_infor = channels.channels_create(user_infor['token'], 'test_one', True)
    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    message_id = message.message_send(
        user_infor['token'], channel_infor['channel_id'], 'a'*99)
    assert other.search(user_infor['token'], 'a'*99) == {"messages": [{
        'message_id': message_id["message_id"],
        'u_id': user_infor["u_id"],
        'message': 'a'*99,
        'time_created': time_create,
        'reacts': [message_parser.set_reacts()],
        'is_pinned': False
    }]}


def test_search_part_of_query():
    """
    test search function will also return a message that part of message match query.
    """
    user_infor = auth.auth_register("email@email.com", "password", "Min", "Li")
    channel_infor = channels.channels_create(user_infor['token'], 'test_one', True)
    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    message_id = message.message_send(
        user_infor['token'], channel_infor['channel_id'], 'a'*99)
    assert other.search(user_infor['token'], 'a'*98) == {"messages": [{
        'message_id': message_id["message_id"],
        'u_id': user_infor["u_id"],
        'message': 'a'*99,
        'time_created': time_create,
        'reacts': [message_parser.set_reacts()],
        'is_pinned': False
    }]}

def test_search_no_match_return():
    """
    test if no message matched, search should return a dictionary contain empty list
    """
    login_infor = message_test.test_message_send()
    assert other.search(login_infor['token'], 'i'*98) == {"messages":[]}

def test_search_empty_sting():
    """
    test if the empty string is giving, the InputError shoud appear
    """
    login_infor = message_test.test_message_send()
    with pytest.raises(error.InputError):
        other.search(login_infor['token'], '')

def test_search_valid_v():
    """
    test if token is bad it should appear a AccessError.
    """
    login_infor = message_test.test_message_send()
    auth.auth_logout(login_infor['token'])
    with pytest.raises(error.AccessError):
        other.search(login_infor['token'], 'a'*99)
