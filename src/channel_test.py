"""
This is a file which runs through tests of channel.py
It tests for valid cases, the given input and access errors, and any other errors needed.
"""

import pytest
import channel
import channels
import message
import error
import auth


############################################################################################
#
#                                   Testing channel_details
#
############################################################################################

def test_details_valid():
    """
    Tests that channel_details functions correctly
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # create a second user and add them to the channel
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    # test that channel_details has the right information about our test channel
    details = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    # ensure only one owner is test_dict
    assert len(details["owner_members"]) == 1
    assert details["owner_members"][0]["u_id"] == test_dict["u_id"]
    # ensure there are two members: test_dict & test_dict_2
    assert len(details["all_members"]) == 2
    assert details["all_members"][0]["u_id"] == test_dict["u_id"]
    assert details["all_members"][1]["u_id"] == test_dict_2["u_id"]
    # ensure the name of the channel is "test rum ham"
    assert details["name"] == "test rum ham"

def test_details_nvid():
    """
    Tests if channel_details raises an InputError when channel ID is not valid
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # invalid channel ID (not assigned by channels_create)
    channel_id = 100
    # test for input error
    with pytest.raises(error.InputError):
        (channel.channel_details(test_dict["token"], channel_id))

def test_details_not_member():
    """
    Tests if channel_details raises an AccessError when the user is not a member of the channel
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test channel", True)
    # introduce a second user not a part of the channel
    not_member = auth.auth_register("fake@email.com", "password2", "not", "member")
    # test for access error
    with pytest.raises(error.AccessError):
        (channel.channel_details(not_member["token"], c_id_dict["channel_id"]))

def test_details_nvt():
    """
    tests if channel_details raises an Access Error when the user does not have a valid token
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test channel", True)
    # create an invalid token
    invalid_token = 100
    # test for access error
    with pytest.raises(error.AccessError):
        channel.channel_details(invalid_token, c_id_dict["channel_id"])

def test_details_react_is_updated():
    """
    checks that details message checks if a person is reacted to a particular message
    """
    user_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    c_id_dict = channels.channels_create(user_dict["token"], "test channel", True)
    message_file = message.message_send(user_dict['token'], c_id_dict['channel_id'], "Test mess!")

    message.message_react(user_dict['token'], message_file['message_id'], 1)

    c_msg_dict = channel.channel_messages(user_dict['token'], c_id_dict['channel_id'], 0)

    assert c_msg_dict.get('messages')[0].get('reacts')[0].get('is_this_user_reacted') is True

############################################################################################
#
#                                   Testing channel_messages
#
############################################################################################

def test_messages_valid():
    """
    tests if channel_messages works with valid input less than 50
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # add a message to channel_messages
    message.message_send(test_dict["token"], c_id_dict["channel_id"], "hello world")
    # test that messages successfully returns the message
    sent_messages = channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 0)
    assert sent_messages["messages"][0]["message"] == "hello world"
    # check that messages returns correct end number
    assert sent_messages["end"] == -1

def test_mesages_pagination():
    """
    tests if channel_messages successfully paginates a message thread with more than 50 messages
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # send numbered messages from 0 to 127 in test rum ham
    i = 127
    while i >= 0:
        message.message_send(test_dict["token"], c_id_dict["channel_id"], str(i))
        i -= 1

    # we then return the messages from 60 to 109 inclusive
    sent_messages = channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 60)

    # we then check that the function successfully paginates and returns 50 numbers
    assert len(sent_messages["messages"]) == 50
    # and we check that channel_messages return the correct numbers associated with the messages
    i = 0
    while i < 50:
        # Most recent message sent is "0", then "1"... all the way to "127"
        # sent_messages starts from 60, so:
        assert sent_messages["messages"][i]["message"] == str(i + 60)
        i += 1
    # check that messages returns correct end number
    assert sent_messages["end"] == 60 + 50

def test_messages_nvid():
    """
    tests if channel_messages returns an InputError when channel ID is not a valid channel
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # invalid channel ID (not assigned by channels_create)
    channel_id = 100
    # check for Input Error
    with pytest.raises(error.InputError):
        (channel.channel_messages(test_dict["token"], channel_id, 0))

def test_messages_start_too_large():
    """
    tests if channel_messages returns an InputError when start > total number of messages in channel
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # add a message to channel_messages
    message.message_send(test_dict["token"], c_id_dict["channel_id"], "hello world")
    # test that channel_messages returns an input error when start is larger than no. of messages
    with pytest.raises(error.InputError):
        (channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 42))

def test_messages_empty_messages():
    """
    Tests if messages is called on an empty channel, an empty list is returned
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # test that channel_messages returns an empty list when start = 0
    messages = channel.channel_messages(test_dict["token"], c_id_dict["channel_id"], 0)
    assert messages["messages"] == []

def test_messages_not_member():
    """
    tests if channel_messages returns an AccessError when the user is not a member of channel_ID
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # add a message to channel_messages
    message.message_send(test_dict["token"], c_id_dict["channel_id"], "hello world")
    # introduce a second user not a member of test rum ham channel
    not_member = auth.auth_register("fake@email.com", "password2", "not", "member")
    # test that channel_messages raises an access error when not member attempts to read messages
    with pytest.raises(error.AccessError):
        (channel.channel_messages(not_member["token"], c_id_dict["channel_id"], 0))

def test_messages_nvt():
    """
    tests if channel_messages returns an AccessError when an invalid token is used
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # add a message to channel_messages
    message.message_send(test_dict["token"], c_id_dict["channel_id"], "hello world")
    # create an invalid token
    invalid_token = 100
    # test for access error
    with pytest.raises(error.AccessError):
        channel.channel_messages(invalid_token, c_id_dict["channel_id"], 0)

############################################################################################
#
#                                   Testing channel_leave
#
############################################################################################

def test_leave_valid():
    """
    Tests if channel_leave works with a valid token and channel ID
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # create a second user and add them to the channel
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    # store our details before the leave
    details_before = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    # ensure there are two members: test_dict & test_dict_2
    assert len(details_before["all_members"]) == 2
    assert details_before["all_members"][0]["u_id"] == test_dict["u_id"]
    assert details_before["all_members"][1]["u_id"] == test_dict_2["u_id"]
    # test channel_leave to have James May(test_dict_2) leave
    channel.channel_leave(test_dict_2["token"], c_id_dict["channel_id"])
    # check that "test rum ham" only has 1 user in it: Bob Ross
    details_after = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    assert len(details_after["all_members"]) == 1
    assert details_after["all_members"][0]["u_id"] == test_dict["u_id"]

def test_leave_nvid():
    """
    Tests if channel_leave raises an InputError when channel ID given is invalid
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # invalid channel ID (not assigned by channels_create)
    channel_id = 100
    # test for input error
    with pytest.raises(error.InputError):
        (channel.channel_leave(test_dict["token"], channel_id))

def test_leave_not_member():
    """
    Tests if channel_leave raises an AccessError when the user is not a member of channel ID given
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test channel", True)
    # introduce a second user not a part of the channel
    not_member = auth.auth_register("fake@email.com", "password2", "not", "member")
    #   test for access error
    with pytest.raises(error.AccessError):
        (channel.channel_leave(not_member["token"], c_id_dict["channel_id"]))

def test_leave_nvt():
    """
    Tests if channel_leave raises an AccessError when an invalid token is used
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test channel", True)
    # create a second user and add them to the channel
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    # create an invalid token
    invalid_token = 100
    # test for AccessError
    with pytest.raises(error.AccessError):
        (channel.channel_leave(invalid_token, c_id_dict["channel_id"]))

############################################################################################
#
#                                   Testing channel_invite
#
############################################################################################

def test_join_valid():
    """
    Tests if channel join works with all valid information
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # store details before using channel_join
    details_before = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    # check that there is only one member: Bob Ross
    assert len(details_before["all_members"]) == 1
    assert details_before["all_members"][0]["u_id"] == test_dict["u_id"]
    # we then register a second user
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    # Then we add them to the channel 'test rum ham'
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    # Now we test whether the join worked (now test_dict and test_dict_2 are part of channel)
    details_after = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    assert len(details_after["all_members"]) == 2
    assert details_after["all_members"][0]["u_id"] == test_dict["u_id"]
    assert details_after["all_members"][1]["u_id"] == test_dict_2["u_id"]
    assert len(details_after["owner_members"]) == 1
    # this extra part tests if channel_join works if an empty channel is joined
    # user joining is made an owner
    channel.channel_leave(test_dict["token"], c_id_dict["channel_id"])
    channel.channel_leave(test_dict_2["token"], c_id_dict["channel_id"])
    channel.channel_join(test_dict["token"], c_id_dict["channel_id"])
    details_empty_after = channel.channel_details(test_dict["token"], c_id_dict["channel_id"])
    assert len(details_empty_after["owner_members"]) == 1
    assert details_empty_after["all_members"][0]["u_id"] == test_dict["u_id"]


def test_join_nvid():
    """
    Tests if channel_join raises an InputError when channel ID is not a valid channel
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # invalid channel ID (not assigned by channels_create)
    channel_id = 100
    # test for input error
    with pytest.raises(error.InputError):
        (channel.channel_join(test_dict["token"], channel_id))

def test_join_private():
    """
    Tests if channel_join raises an AccessError when channel_id is private (and user is not admin)
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # generate a valid channel ID which is private
    c_id_dict = channels.channels_create(test_dict["token"], "test channel", False)
    # introduce a second test register
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    # test that channel_join raises an access error joining a private channel
    with pytest.raises(error.InputError):
        (channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"]))

def test_join_admin():
    """
    Tests if channel_join allows an admin to join a private channel
    """
    # establish a test register
    # since test_dict is first member he is owner of slackr/admin (per assumptions)
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # create a second user
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    # second user creates a private channel (which bob ross is not a part of)
    c_id_dict = channels.channels_create(test_dict_2["token"], "test admin", False)
    # store details before using channel_join
    details_before = channel.channel_details(test_dict_2["token"], c_id_dict["channel_id"])
    # check that only test_dict_2 is owner in channel
    assert len(details_before["owner_members"]) == 1
    assert details_before["owner_members"][0]["u_id"] == test_dict_2["u_id"]
    # we then test that test_dict(admin) can join the private channel
    channel.channel_join(test_dict["token"], c_id_dict["channel_id"])
    details_after = channel.channel_details(test_dict_2["token"], c_id_dict["channel_id"])
    # we check that there are now two owners in the channel
    assert len(details_after["owner_members"]) == 2
    assert details_after["owner_members"][0]["u_id"] == test_dict_2["u_id"]
    assert details_after["owner_members"][1]["u_id"] == test_dict["u_id"]

def test_join_already_joined():
    """
    Tests if channel_join raises an AccessError if the member is already a part of channel ID
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # create a second user and add them to the channel
    test_dict_2 = auth.auth_register("test2@email.com", "password2", "James", "May")
    channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"])
    # test that channel_join returns an access error
    with pytest.raises(error.InputError):
        (channel.channel_join(test_dict_2["token"], c_id_dict["channel_id"]))

def test_join_nvt():
    """
    tests if channel_join returns an access error if invalid token used
    """
    # establish a test register
    test_dict = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    # valid channel ID (assigned by channels_create)
    c_id_dict = channels.channels_create(test_dict["token"], "test rum ham", True)
    # create an invalid token
    invalid_token = 100
    # test for AccessError
    with pytest.raises(error.AccessError):
        channel.channel_join(invalid_token, c_id_dict["channel_id"])

def test_invite_already_in():
    """
    tests if channel_invite returns an input error if the invitee is already in the channel
    """
    user = auth.auth_register("test@email.com", "password", "Bob", "Ross")
    user2 = auth.auth_register("test2@email.com", "password", "Bobby", "Rossy")
    c_id_dict = channels.channels_create(user["token"], "test rum ham", True)
    channel.channel_join(user2['token'], c_id_dict['channel_id'])
    with pytest.raises(error.InputError):
        channel.channel_invite(user['token'], c_id_dict['channel_id'], user2['u_id'])



############################################################################################
#
#                                   Testing channel_addowner
#
############################################################################################

def test_addowner_nvid():
    """
    Tests if channel_addowner raises an InputError when channel id is not valid
    """
    user = auth.auth_register("email@email.com", "password", "Kazuma", "Sato")
    with pytest.raises(error.InputError):
        channel.channel_addowner(user["token"], 100, user["u_id"])

def test_addowner_already_owner():
    """
    Tests if channel_addowner raises an InputError when u_id is already an owner
    """
    user = auth.auth_register("email@email.com", "password", "Harry", "Potter")
    c_id_dict = channels.channels_create(user["token"], "test_channel", True)
    with pytest.raises(error.InputError):
        channel.channel_addowner(user["token"], c_id_dict["channel_id"], user["u_id"])

def test_addowner_not_member():
    """
    Tests if channel_addowner does nothing if u_id is not a member
    """
    user1 = auth.auth_register("email@email.com", "password", "Tony", "TheTiger")
    user2 = auth.auth_register("email2@email.com", "password", "Captain", "Crunch")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_addowner(user1["token"], c_id_dict["channel_id"], user2["u_id"])

    details = channel.channel_details(user1["token"], c_id_dict["channel_id"])
    assert len(details["owner_members"]) == 1
    assert details["owner_members"][0]["u_id"] == user1["u_id"]

def test_addowner_not_valid_uid():
    """
    Tests if addowner will reject an invalid u_id
    """
    user1 = auth.auth_register("email@email.com", "password", "Rum", "Ham")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    fake_user_id = -33

    with pytest.raises(error.InputError):
        channel.channel_addowner(user1["token"], c_id_dict["channel_id"], fake_user_id)

def test_addowner_nvt():
    """
    Tests if channel_addowner raises an AccessError when the token passed is invalid
    """
    user1 = auth.auth_register("email@email.com", "password", "Rum", "Ham")
    user2 = auth.auth_register("email2@email.com", "password", "Danny", "DeVito")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_join(user2["token"], c_id_dict["channel_id"])
    with pytest.raises(error.AccessError):
        channel.channel_addowner("invalid_token", c_id_dict["channel_id"], user2["u_id"])

def test_addowner_no_owner():
    """
    Tests if channel_addowner raises an AccessError when user is not owner of channel or slackr
    i.e. test if AccessError raised if user is not an owner of BOTH
    """
    user1 = auth.auth_register("email@email.com", "password", "Hayden", "Smith")
    user2 = auth.auth_register("email2@email.com", "password", "John", "Cena")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_join(user2["token"], c_id_dict["channel_id"])
    with pytest.raises(error.AccessError):
        channel.channel_addowner(user2["token"], c_id_dict["channel_id"], user2["u_id"])

def test_addowner_slackr():
    """
    Tests if channel_addowner works if Slackr owner who is not a channel owner tries to use it
    """
    user1 = auth.auth_register("email@email.com", "password", "Severus", "Snape")
    user2 = auth.auth_register("email2@email.com", "password", "Albus", "Dumbledore")
    user3 = auth.auth_register("email3@email.com", "Potions", "Harry", "Potter")

    c_id_dict = channels.channels_create(user2["token"], "test_channel", True)
    channel.channel_join(user1["token"], c_id_dict["channel_id"])
    channel.channel_join(user3["token"], c_id_dict["channel_id"])

    details_before = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert details_before["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_before["owner_members"][1]["u_id"] == user1["u_id"]
    assert len(details_before["owner_members"]) == 2
    assert len(details_before["all_members"]) == 3
    assert details_before["all_members"][2]["u_id"] == user3["u_id"]

    channel.channel_addowner(user1["token"], c_id_dict["channel_id"], user3["u_id"])
    details_after = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert len(details_after["owner_members"]) == 3
    assert details_after["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_after["owner_members"][1]["u_id"] == user1["u_id"]
    assert details_after["owner_members"][2]["u_id"] == user3["u_id"]

def test_addowner_channel():
    """
    Tests if channel_addowner works if user is a channel owner but not a Slackr owner
    """
    user1 = auth.auth_register("email@email.com", "password", "Earthworm", "Jim")
    user2 = auth.auth_register("email2@email.com", "password", "Gabe", "Newell")
    user3 = auth.auth_register("email3@email.com", "Potions", "Harry", "Potter")

    # user2 creates a channel, they should be the only owner
    c_id_dict = channels.channels_create(user2["token"], "test_channel", True)
    channel.channel_join(user3["token"], c_id_dict["channel_id"])
    details_before = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert details_before["owner_members"][0]["u_id"] == user2["u_id"]
    assert len(details_before["owner_members"]) == 1

    # user2 makes user3 an owner, channel_details should now show two owners
    channel.channel_addowner(user2["token"], c_id_dict["channel_id"], user3["u_id"])
    details_after = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert len(details_after["owner_members"]) == 2
    assert details_after["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_after["owner_members"][1]["u_id"] == user3["u_id"]

    # user1 (admin) joins the channel, he should be owner
    channel.channel_join(user1["token"], c_id_dict["channel_id"])
    details_admin = channel.channel_details(user1["token"], c_id_dict["channel_id"])
    assert len(details_admin["owner_members"]) == 3
    assert details_admin["owner_members"][2]["u_id"] == user1["u_id"]
############################################################################################
#
#                                   Testing channel_removeowner
#
############################################################################################

def test_removeowner_nvid():
    """
    Tests if channel_removeowner raises an InputError when channel id is not valid
    """
    user = auth.auth_register("email@email.com", "password", "Darth", "Vader")
    with pytest.raises(error.InputError):
        channel.channel_removeowner(user["token"], 100, user["u_id"])

def test_removeowner_not_owner():
    """
    Tests if channel_removeowner raises an InputError when u_id is not an owner
    """
    user1 = auth.auth_register("email@email.com", "password", "Callum", "Jones")
    user2 = auth.auth_register("email2@email.com", "password", "Jason", "Lin")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_join(user2["token"], c_id_dict["channel_id"])
    with pytest.raises(error.InputError):
        channel.channel_removeowner(user1["token"], c_id_dict["channel_id"], user2["u_id"])

def test_removeowner_not_member():
    """
    Tests if channel_removeowner raises InputError when u_id is not a member (and not an owner)
    """
    user1 = auth.auth_register("email@email.com", "password", "Lord", "Voldemort")
    user2 = auth.auth_register("email2@email.com", "password", "Tom", "Riddle")

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    with pytest.raises(error.InputError):
        channel.channel_removeowner(user1["token"], c_id_dict["channel_id"], user2["token"])

def test_removeowner_nvt():
    """
    Tests if channel_removeowner raises an AccessError when the token passed is invalid
    """
    user1 = auth.auth_register("email@email.com", "password", "Dr", "Robotnik")
    user2 = auth.auth_register("email2@email.com", "password", "Sonic", "Thehedgehog")

    # user1 makes user2 an owner and then tries to remove them with an invalid token
    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_join(user2["token"], c_id_dict["channel_id"])
    channel.channel_addowner(user1["token"], c_id_dict["channel_id"], user2["u_id"])
    with pytest.raises(error.AccessError):
        channel.channel_removeowner("invalid_token", c_id_dict["channel_id"], user2["u_id"])

def test_removeowner_no_owner():
    """
    Tests if channel_removeowner raises an AccessError
    when the user is not an owner of the channel/Slackr
    i.e. test if AccessError raised if user is not an owner of BOTH
    """
    user1 = auth.auth_register("email@email.com", "password", "Crazy", "Frog")
    user2 = auth.auth_register("email2@email.com", "password", "Gummy", "Bear")
    user3 = auth.auth_register("email3@email.com", "password", "Gummy", "Bear")
    user4 = auth.auth_register("email4@email.com", "password", "Gummy", "Bear")

    # USER1 is owner of channel and slackr
    # USER2 is not owner of either.

    c_id_dict = channels.channels_create(user1["token"], "test_channel", True)
    channel.channel_join(user2["token"], c_id_dict["channel_id"])
    channel.channel_join(user3["token"], c_id_dict["channel_id"])
    channel.channel_join(user4["token"], c_id_dict["channel_id"])
    channel.channel_addowner(user1['token'], c_id_dict['channel_id'], user4['u_id'])
    with pytest.raises(error.AccessError):
        channel.channel_removeowner(user2["token"], c_id_dict["channel_id"], user1["u_id"])
    with pytest.raises(error.AccessError):
        channel.channel_removeowner(user3["token"], c_id_dict["channel_id"], user4["u_id"])

def test_removeowner_slackr():
    """
    Tests if channel_removeowner works when user is a Slackr owner but not a channel owner
    """
    user1 = auth.auth_register("email@email.com", "password", "Santa", "Claus")
    user2 = auth.auth_register("email2@email.com", "password", "Mrs", "Claus")

    # user2 creates a channel, user1 joins it and is added as an owner
    c_id_dict = channels.channels_create(user2["token"], "test_channel", True)
    channel.channel_join(user1["token"], c_id_dict["channel_id"])
    details_before = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert details_before["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_before["owner_members"][1]["u_id"] == user1["u_id"]

    # user1 removes user2 as an owner
    channel.channel_removeowner(user1["token"], c_id_dict["channel_id"], user2["u_id"])
    details_after = channel.channel_details(user1["token"], c_id_dict["channel_id"])
    assert len(details_after["owner_members"]) == 1
    assert details_after["owner_members"][0]["u_id"] == user1["u_id"]

def test_removeowner_channel():
    """
    Tests if channel_removeowner works when user is a channel owner but not a Slackr owner
    """
    user1 = auth.auth_register("email@email.com", "password", "Tom", "Nook")
    user2 = auth.auth_register("email2@email.com", "password", "Ash", "Ketchum")
    user3 = auth.auth_register("email3@email.com", "password3", "Simon", "Guest")

    # user2 creates a private channel and adds user1 and
    # user3 to it, channel_details should show two owners
    c_id_dict = channels.channels_create(user2["token"], "test_channel", True)
    channel.channel_join(user1["token"], c_id_dict["channel_id"])
    channel.channel_join(user3["token"], c_id_dict["channel_id"])
    channel.channel_addowner(user2["token"], c_id_dict["channel_id"], user3["u_id"])
    details_before = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert details_before["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_before["owner_members"][1]["u_id"] == user1["u_id"]
    assert details_before["owner_members"][2]["u_id"] == user3["u_id"]
    assert len(details_before["owner_members"]) == 3
    assert details_before["all_members"][0]["u_id"] == user2["u_id"]
    assert details_before["all_members"][1]["u_id"] == user1["u_id"]
    assert details_before["all_members"][2]["u_id"] == user3["u_id"]
    assert len(details_before["all_members"]) == 3


    # user2 removes user3 as an owner, channel_details should only show two owners
    channel.channel_removeowner(user2["token"], c_id_dict["channel_id"], user3["u_id"])
    details_after = channel.channel_details(user2["token"], c_id_dict["channel_id"])
    assert len(details_after["owner_members"]) == 2
    assert details_after["owner_members"][0]["u_id"] == user2["u_id"]

    assert details_after["all_members"][0]["u_id"] == user2["u_id"]
    assert details_after["all_members"][1]["u_id"] == user1["u_id"]
    assert details_after["all_members"][2]["u_id"] == user3["u_id"]
    assert len(details_after["all_members"]) == 3


############################################################################################
#
#                                   Testing channel_invite
#
############################################################################################

def test_valid_invite_public():
    """
    tests that valid invite works in a public channel
    """
    user1 = auth.auth_register("email1@email.com", "password", "Michael", "Palin")
    user2 = auth.auth_register("email2@email.com", "password", "Tony", "Stark")

    # User 1 creates a new public channel:
    c_id = channels.channels_create(user1.get('token'), "testChannel", True)

    # User 1 invites User 2 to the channel:
    channel.channel_invite(user1.get('token'), c_id.get('channel_id'), user2.get('u_id'))
    details_after = channel.channel_details(user2["token"], c_id["channel_id"])
    assert details_after["all_members"][0]["u_id"] == user1["u_id"]
    assert details_after["all_members"][1]["u_id"] == user2["u_id"]
    assert len(details_after["all_members"]) == 2
    assert details_after["owner_members"][0]["u_id"] == user1["u_id"]
    assert len(details_after["owner_members"]) == 1


def test_valid_invite_to_admin():
    """
    checks that if an admin is invited they are allowed in and are given owner privlages
    """
    user1 = auth.auth_register("email1@email.com", "password", "Michael", "Palin")
    user2 = auth.auth_register("email2@email.com", "password", "Tony", "Stark")

    # User 2 creates a new public channel:
    c_id = channels.channels_create(user2.get('token'), "testChannel", True)

    # User 2 invites User 1 to the channel:
    channel.channel_invite(user2.get('token'), c_id.get('channel_id'), user1.get('u_id'))

    details_after = channel.channel_details(user2["token"], c_id["channel_id"])
    assert details_after["owner_members"][0]["u_id"] == user2["u_id"]
    assert details_after["owner_members"][1]["u_id"] == user1["u_id"]
    assert len(details_after["owner_members"]) == 2

def test_valid_invite_private():
    """
    tests that an invite to a private channel works
    """

    user1 = auth.auth_register("email1@email.com", "password", "Ada", "Lovelace")
    user2 = auth.auth_register("email2@email.com", "password", "Ewan", "McGregor")

    # User 1 creates a new private channel:
    c_id = channels.channels_create(user1.get('token'), "testChannel", False)

    # User 1 invites User 2 to the channel:
    channel.channel_invite(user1.get('token'), c_id.get('channel_id'), user2.get('u_id'))

    #assert that both users are now in the channel
    details_after = channel.channel_details(user2["token"], c_id["channel_id"])
    assert len(details_after["all_members"]) == 2

def test_invalid_channel_id():
    """
    checks invite returns an input error if channel id invalid
    """
    user1 = auth.auth_register("email1@email.com", "password", "James", "Bond")
    user2 = auth.auth_register("email2@email.com", "password", "Commander", "Cody")

    with pytest.raises(error.InputError):
        channel.channel_invite(user1.get('token'), 3, user2.get('u_id'))

def test_invalid_user_id():
    """
    checks invite returns an input error if user id (target) invalid
    """
    user1 = auth.auth_register("email1@email.com", "password", "Sameen", "Shaw")

    # User 1 creates a new public channel:
    c_id = channels.channels_create(user1.get('token'), "testChannel", True)

    with pytest.raises(error.InputError):
        channel.channel_invite(user1.get('token'), c_id.get('channel_id'), 123)

def test_inviter_not_channel_member():
    """
    checks invite returns an access error if the curr auth user is not a member of the channel
    """
    user1 = auth.auth_register("email1@email.com", "password", "G", "Man")
    user2 = auth.auth_register("email2@email.com", "password", "Jeremy", "Lambert")
    user3 = auth.auth_register("email3@email.com", "password", "Samantha", "Groves")

    # User 1 creates a new public channel:
    c_id = channels.channels_create(user1.get('token'), "testChannel", True)

    # User 3 tries to invite user 2 - should throw AccessError
    with pytest.raises(error.AccessError):
        channel.channel_invite(user3.get('token'), c_id.get('channel_id'), user2.get('u_id'))

def test_inviter_token_expired():
    """
    tests if invite raises an access error if token supplied is expired
    """
    user1 = auth.auth_register("email1@email.com", "password", "Billy", "Butcher")
    user2 = auth.auth_register("email2@email.com", "password", "Simon", "Pegg")

    c_id = channels.channels_create(user1.get('token'), "testChannel", True)

    auth.auth_logout(user1.get('token'))

    with pytest.raises(error.AccessError):
        channel.channel_invite(user1.get('token'), c_id.get('channel_id'), user2.get('u_id'))
