"""
Test file for message.py
"""
import datetime
import threading

import pytest

from message import (message_send, message_remove,
                     message_edit, message_sendlater,
                     message_pin, message_unpin, message_react, message_unreact)
from message_parser import set_reacts
from error import InputError, AccessError
from auth import auth_register
from channels import channels_create, channel_join
from other import search

###############################################################
#
#                        Helper Functions
#
###############################################################

def message_send_helper(token, channel_id, message):
    """
    Creates a message and returns its id and the time it
    was created in a dictionary: {msg_dict, msg_time}
    """
    msg_dict = message_send(token, channel_id, message)
    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()

    return {"msg_dict": msg_dict, "msg_time": time_create}

def helper_create_react():
    """
    Create a user, channel, message and react it
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    message_react(user_info['token'], msg_info['msg_dict']['message_id'], 1)
    message_file = search(user_info['token'], "Test msg!")
    return {
        'message_id': msg_info['msg_dict']['message_id'],
        'token': user_info['token'],
        'message_file': message_file,
        'u_id': user_info['u_id'],
        'channel_id': channel_info['channel_id']
    }

def create_pinned_message():
    """
    Create a user, channel, message w/ react and then have that user pin it.
    """
    data = helper_create_react()
    message_pin(data['token'], data['message_id'])
    return {
        "token": data['token'],
        "message_id": data['message_id'],
        "message_file": data['message_file'],
        "channel_id": data['channel_id']
    }

###############################################################
#
#                        message_send_test
#
###############################################################


def test_message_send():
    """
    Assume that message could not be empty string. If empty string was sended
    The InputError should raisedcd
    test whether the message_send funtion worke as ervery input is correct.
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)

    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()

    message_id = message_send(
        user_infor['token'], channel_infor['channel_id'], 'a'*99)
    # To test that message actually exists.
    assert search(user_infor['token'], 'a'*99) == {"messages": [{
        'message_id': message_id["message_id"],
        'u_id': user_infor["u_id"],
        'message': 'a'*99,
        'time_created': time_create,
        'reacts': [set_reacts()],
        'is_pinned': False
    }]}
    # the user_infor was return for test_search.
    return user_infor

def test_mesasge_send_2():
    """
    Test the message_send function works as two message is send
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)

    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()

    message_id_1 = message_send(
        user_infor['token'], channel_infor['channel_id'], 'a'*99)
    message_id_2 = message_send(
        user_infor['token'], channel_infor['channel_id'], 'a'*99)

    assert search(user_infor['token'], 'a'*99) == {"messages": [{
        'message_id': message_id_2["message_id"],
        'u_id': user_infor["u_id"],
        'message': 'a'*99,
        'time_created': time_create,
        'reacts': [set_reacts()],
        'is_pinned': False
    }, {
        'message_id': message_id_1["message_id"],
        'u_id': user_infor["u_id"],
        'message': 'a'*99,
        'time_created': time_create,
        'reacts': [set_reacts()],
        'is_pinned': False
    }]}

def test_message_send_empty_string():
    """
    Test for sending empty string. It should return a InputError
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    with pytest.raises(InputError):
        message_send(user_infor['token'], channel_infor['channel_id'], '')


def test_message_send_1001():
    """
    Test whether the message_send function will find error if message is too long.
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    with pytest.raises(InputError):
        message_send(user_infor['token'],
                     channel_infor['channel_id'], 'a'*1001)


def test_message_send_not_in_c():
    """
    Check that AccessError is raised when a user sends a message to
    a channel they are not in.
    """
    user_infor1 = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    user_infor2 = auth_register('testmeplz@gmail.com', 'ccc337992611', 'A', 'H')

    channel_infor_2 = channels_create(user_infor2['token'], 'test_two', True)

    with pytest.raises(AccessError):
        message_send(user_infor1['token'], channel_infor_2['channel_id'],
                     'a'*100)

###############################################################
#
#                        message_remove_test
#
###############################################################


def test_message_remove():
    """
    Make sure message_remove will work if all inputs are right and authorised.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_info = channels_create(user_info['token'], 'test_channel', True)
    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test message!")

    message_remove(user_info['token'], msg_info['msg_dict']['message_id'])
    assert search(user_info['token'], "Test message!") == {"messages": []}
    # return message_infor


def test_message_remove_404():
    """
    Test remove sends an InputError if msg_id is invalid.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    with pytest.raises(InputError):
        message_remove(user_info['token'], 0)


def test_message_remove_none_of_two():
    """
    Test that when someone tries to remove a message that they
    did not send and they are not an owner AccessError is raised
    """

    # This user is the global owner
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    user_info2 = auth_register("33799@gamil.com", "ccc337992611", "Min", "Li")
    channel_join(user_info2['token'], channel_info['channel_id'])

    with pytest.raises(AccessError):
        message_remove(user_info2['token'], msg_info['msg_dict']['message_id'])


def test_messages_remove_owner():
    """
    Someone tries to remove another users message, but they
    are an owner so they are allowed to
    """
    owner_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    user_info = auth_register("392611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)
    channel_join(owner_info['token'], channel_info['channel_id'])

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")
    message_remove(owner_info['token'], msg_info['msg_dict']['message_id'])

    search_data = search(owner_info['token'], "Test msg!")

    assert search_data['messages'] == []


###############################################################
#
#                        message_edit_test
#
###############################################################


def test_message_edit():
    """
    test message_edit worke under all authorid and valid input.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    message_edit(user_info['token'], msg_info['msg_dict']['message_id'], 'a'*97)
    assert search(user_info['token'], 'a'*97) == {"messages": [{
        'message_id': msg_info['msg_dict']['message_id'],
        'u_id': user_info['u_id'],
        'message': 'a'*97,
        'time_created': msg_info['msg_time'],
        'reacts': [set_reacts()],
        'is_pinned': False
    }]}


def test_message_edit_removed():
    """
    Test whether the edit removed messag will raise InputError.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    message_remove(user_info['token'], msg_info['msg_dict']['message_id'])
    with pytest.raises(InputError):
        message_edit(user_info['token'], msg_info['msg_dict']['message_id'], 'a'*11)


def test_message_edit_too_long():
    """
    test if the new message that replaced the original one is too long.
    This shoud appear a InputError (also added in assumption.md)
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    with pytest.raises(InputError):
        message_edit(user_info['token'], msg_info['msg_dict']['message_id'], 'a'*1111)


def test_message_edit_non_of_two():
    """
    Check for AccessError when person editing did not send the message
    and is not an owner.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    user2_info = auth_register("337992@gamil.com", "ccc337992611", "Min", "Li")
    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    with pytest.raises(AccessError):
        message_edit(user2_info['token'], msg_info['msg_dict']['message_id'], 'A'*11)


def test_message_edit_emty_string():
    """
    test if the empty string is giving to message_edit, It should delete the message.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send_helper(user_info['token'], channel_info['channel_id'], "Test msg!")

    message_edit(user_info['token'], msg_info['msg_dict']['message_id'], '')
    assert search(user_info['token'], 'a'*99) == {"messages": []}

###############################################################
#
#                        message_sendlater_test
#
###############################################################


def test_message_sendlater():
    """
    test whether message_sendlater works as expect.
    """
    def helper_func(token):
        """
        Run search in a seperate thread, so it checks before message is sent.
        We use threads here because the flask side of thing uses local threads
        for routes, so we just use time.sleep inside the functions. This means
        we need a seperate thread to check before sendlater finishes.
        """
        messages = search(token, 'a'*99)
        assert messages['messages'] == []

    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) + datetime.timedelta(0, 4)
    time_sent = time_sent_date.timestamp()

    # Run test check empty a second after message_sendlater has been
    # called (but hasn't finished executing)
    new_thread = threading.Timer(1, helper_func, args=(user_infor['token']))
    new_thread.start()

    message_id = message_sendlater(user_infor['token'],
                                   channel_infor['channel_id'], 'a'*99, time_sent)

    messages = search(user_infor['token'], 'a'*99)
    assert messages['messages'][0]['message_id'] == message_id['message_id']
    assert messages['messages'][0]['time_created'] == time_sent


def test_message_sendlater_0_string():
    """
    test whether the empy string input will raise InputError
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time_sent_date.timestamp()
    with pytest.raises(InputError):
        message_sendlater(user_infor['token'],
                          channel_infor['channel_id'], '', time_sent)


def test_message_sendlater_too_long():
    """
    test whether the 1001 len string input will raise InputError
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time_sent_date.timestamp()
    with pytest.raises(InputError):
        message_sendlater(user_infor['token'],
                          channel_infor['channel_id'], 'a'*1001, time_sent)


def test_message_sendlater_i_c():
    """
    test whether the invalid channel_id
    """
    # Asumm the negative number is a invalided channel_id
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time_sent_date.timestamp()
    with pytest.raises(InputError):
        message_sendlater(user_infor['token'], -1, 'a'*99, time_sent)


def test_message_sendlater_n_i_c():
    """
    Test whether user not in channel sent message will case AccessError
    """
    user_infor1 = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    user_infor2 = auth_register('testmeplz@gmail.com', 'ccc337992611', 'A', 'H')
    channels_create(user_infor1['token'], 'test_one', True)
    channel_infor_2 = channels_create(user_infor2['token'], 'test_two', True)
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time_sent_date.timestamp()
    # user_2 creat the channel_2 and user_1 is not in channel_2
    # so if user_1 try to send message in channel_infor_2, it will return error
    with pytest.raises(AccessError):
        message_sendlater(user_infor1['token'], channel_infor_2['channel_id'],
                          'a'*100, time_sent)


def test_message_sendlater_in_pass():
    """
    Test whether set the time to send in the pass will raise InputError.
    """
    user_infor = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    time_sent_date = datetime.datetime.now().replace(
        microsecond=0) - datetime.timedelta(0, 100)
    time_sent = time_sent_date.timestamp()
    with pytest.raises(InputError):
        message_sendlater(user_infor['token'],
                          channel_infor['channel_id'], 'a'*100, time_sent)

###############################################################
#
#                   test_message_react
#
###############################################################

def test_react_valid():
    """
    Test whether the react works with all valid input.
    """
    data = helper_create_react()
    # Find the first message in the list of matches and check the u_ids in its react.
    for user in data["message_file"]['messages'][0]['reacts'][0]['u_ids']:
        if user == data["u_id"] and (
                data["message_file"]['messages'][0]['reacts'][0]['react_id'] == 1
        ):
            check = True
    assert check is True

def test_react_invalid_token():
    """
    Test invalid tokeon will raise AccessError
    """

    with pytest.raises(AccessError):
        message_react("2130847", -1, -1)

def test_react_invalid_msg_id():
    """
    Test whether react on an invalid message_id will raise InputError.
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    with pytest.raises(InputError):
        message_react(user_info['token'], -1, 1)

def test_react_invalid_react_id():
    """
    Check that invalid react id (e.g. "-1") will raise InputError
    """
    data = helper_create_react()
    with pytest.raises(InputError):
        message_react(data['token'], data['message_id'], -1)

def test_react_twice():
    """
    Test whether message react twice will raise InputError
    """
    data = helper_create_react()
    with pytest.raises(InputError):
        message_react(data["token"], data["message_id"], 1)

def test_react_no_access():
    """
    Test that reacting a message in a channel you're not in
    will raise an InputError.
    """
    data = helper_create_react()
    user2 = auth_register("33611@gamil.com", "ccc337992611", "Min", "Li")
    with pytest.raises(InputError):
        message_react(user2['token'], data['message_id'], 1)


###############################################################
#
#                   test_message_unreact
#
###############################################################

def test_unreact_valid():
    """
    Test for valided input
    """
    data = helper_create_react()
    message_unreact(data['token'], data['message_id'], 1)
    assert data['message_file']['messages'][0]['reacts'][0]['u_ids'] == []

def test_unreact_msg_removed():
    """
    Test whether unreact on a message is deleted will raise InputError.
    """
    data = helper_create_react()
    message_remove(data['token'], data['message_id'])
    with pytest.raises(InputError):
        message_unreact(data['token'], data['message_id'], 1)

def test_unreact_invalid_react_id():
    """
    Test whether invailed react id will raise InputError
    """
    data = helper_create_react()
    with pytest.raises(InputError):
        message_unreact(data['token'], data['message_id'], -1)

def test_unreact_bad_msg_id():
    """
    Test whether invalid message id will raise InputError
    """
    user_info = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    with pytest.raises(InputError):
        message_unreact(user_info['token'], -1, 1)

def test_unreact_twice():
    """
    Test whether message unreact twic will raise InputError
    """
    data = helper_create_react()
    message_unreact(data["token"], data["message_id"], 1)
    with pytest.raises(InputError):
        message_unreact(data["token"], data["message_id"], 1)

def test_unreact_invalid_token():
    """
    Test invalid token will raise AccessError
    """
    with pytest.raises(AccessError):
        message_unreact("2130847", -1, -1)

###############################################################
#
#                   test_message_pin
#
###############################################################

def test_pin_valid():
    """
    Test for valid message_pin execution
    """
    data = create_pinned_message()
    assert data["message_file"]["messages"][0]["is_pinned"] is True

def test_pin_invalid_token():
    """
    Test for invalid token
    """

    with pytest.raises(AccessError):
        message_pin("notatoken", -1)

def test_pin_invalid_msg_id():
    """
    Test whether pin invalid message will raise InputError.
    """
    user = auth_register("337992611@gamil.com", "ccc337992611", "Min", "Li")

    with pytest.raises(InputError):
        message_pin(user['token'], -1)

def test_message_pin_twice():
    """
    Test whether message pin twice will raise InputError
    """
    data = create_pinned_message()
    with pytest.raises(InputError):
        message_pin(data["token"], data["message_id"])

def test_pin_msg_not_owner():
    """
    Test whether pin other person's message
    as a regular user will raise AccessError.
    """
    data = helper_create_react()
    # Create second user and join the channel with the message.
    user_infor = auth_register('337992611@qq.com', 'HereyouAreMyP', 'not', 'exit')
    channel_join(user_infor['token'], data['channel_id'])
    with pytest.raises(AccessError):
        message_pin(user_infor['token'], data['message_id'])

def test_pin_not_in_channel():
    """
    Test whether pin other person's message
    when not in the channel will raise AccessError.
    """
    data = helper_create_react()
    user_infor = auth_register('337992611@qq.com', 'HereyouAreMyP', 'not', 'exit')
    with pytest.raises(AccessError):
        message_pin(user_infor['token'], data['message_id'])

###############################################################
#
#                   test_message_unpin
#
###############################################################

def test_message_unpin_valid():
    """
    Test for valid input
    """
    data = create_pinned_message()
    message_unpin(data["token"], data["message_id"])
    assert data["message_file"]["messages"][0]["is_pinned"] is False

def test_unpin_invalid_token():
    """
    Test for invalid token
    """
    with pytest.raises(AccessError):
        message_unpin("notatoken", -1)

def test_unpin_msg_removed():
    """
    Test whether unpin invalid message_id will raise InputError.
    """
    data = create_pinned_message()
    message_remove(data['token'], data['message_id'])
    with pytest.raises(InputError):
        message_pin(data['token'], data['message_id'])

def test_message_unpin_twice():
    """
    Test whether message unreact twice will raise InputError
    """
    data = create_pinned_message()
    message_unpin(data["token"], data["message_id"])
    with pytest.raises(InputError):
        message_unpin(data["token"], data["message_id"])

def test_unpin_msg_not_owner():
    """
    Test whether unpin other person's message
    as a regular user will raise AccessError.
    """
    data = create_pinned_message()
    # Create second user and join the channel with the message.
    user_infor = auth_register('337992611@qq.com', 'HereyouAreMyP', 'not', 'exit')
    channel_join(user_infor['token'], data['channel_id'])
    with pytest.raises(AccessError):
        message_unpin(user_infor['token'], data['message_id'])

def test_unpin_not_in_channel():
    """
    Test whether unpin other person's message
    when not in the channel will raise AccessError.
    """
    data = create_pinned_message()
    user_infor = auth_register('337992611@qq.com', 'HereyouAreMyP', 'not', 'exit')
    with pytest.raises(AccessError):
        message_unpin(user_infor['token'], data['message_id'])


###############################################################
#
#          all message function to test invalid token
#
###############################################################

def test_m_send_for_valied_token():
    """
    test for all message function for valid token
    otherwise It should return a AccessError.
    """
    with pytest.raises(AccessError):
        message_send("notatoken", -1, "test")


def test_m_sendlater_not_valid_t():
    """
    Test for invalided token
    """
    with pytest.raises(AccessError):
        message_sendlater("notatoken", -1, "test", datetime.datetime.now())


def test_message_remove_token_v():
    """
    test if token is not correct, message_remove should return AccessError
    """
    with pytest.raises(AccessError):
        message_remove("notatoken", -1)


def test_message_edit_token_v():
    """
    test if token is not correct, message_edit should return AccessError.
    """
    with pytest.raises(AccessError):
        message_edit("notatoken", -1, "test")


####### Additional Tests

def test_hangman_wrong_guess():
    """ Too many guess inputs """
    data = create_pinned_message()
    message_send(data['token'], data['channel_id'], "/hangman")
    with pytest.raises(InputError):
        message_send(data['token'], data['channel_id'], "/guess a a")

def test_remove_no_access():
    """ Test if AccessError raised if user doesn't have permission to remove message """
    data = create_pinned_message()
    user2 = auth_register("ema222@email.com", "password", "Bill", "Bill")
    with pytest.raises(AccessError):
        message_remove(user2['token'], data['message_id'])

def test_edit_msg_no_access():
    """ Test if AccessError raised if user doesn't have permission to edit message """
    data = create_pinned_message()
    user2 = auth_register("ema222@email.com", "password", "Bill", "Bill")
    channel_join(user2['token'], data['channel_id'])
    with pytest.raises(AccessError):
        message_edit(user2['token'], data['message_id'], "test")
