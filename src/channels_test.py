""" Contains tests for channels functions. """

import pytest
import channels
import error
import channel
from auth import auth_register

#####################################################################
#                                                                   #
#                      Testing channels_create                      #
#                                                                   #
#####################################################################

def test_channels_create_length():
    """ Tests if channels_create raises an InputError when name is more than 20 characters long """

    user = auth_register("email@email.com", "password", "Bob", "Ross")
    with pytest.raises(error.InputError):
        channels.channels_create(user["token"], "a"*21, True)

def test_channels_create_nvt():
    """ Tests if channels_create raises an AccessError when the token passed is invalid. """

    with pytest.raises(error.AccessError):
        channels.channels_create("invalid_token", "test_channel", True)

def test_channels_create():
    """ Tests if channels_create works by checking stored values with channels_list. """

    user = auth_register("email@email.com", "password", "Steve", "Ross")

    channel_id = channels.channels_create(user["token"], "Channel", True)
    channels_dict = channels.channels_list(user["token"])

    assert channels_dict["channels"][0]["channel_id"] == channel_id["channel_id"]
    assert channels_dict["channels"][0]["name"] == "Channel"

###################################################################
#                                                                 #
#                      Testing channels_list                      #
#                                                                 #
###################################################################

def test_channels_list_nvt():
    """ Tests if channels_list raises an AccessError when the token passed is invalid. """

    with pytest.raises(error.AccessError):
        channels.channels_list("invalid_token")

def test_channels_list_empty():
    """ Tests if channels_list returns an empty list in a dictionary,
    if user is a member of no channels. """

    user1 = auth_register("email@email.com", "password", "Tommy", "Wiseau")
    user2 = auth_register("email2@email.com", "password", "He", "Man")

    channels.channels_create(user1["token"], "private_channel1", False)
    channels.channels_create(user1["token"], "private_channel2", False)

    c_list = channels.channels_list(user2["token"])
    assert c_list["channels"] == []

def test_channels_list():
    """ Tests if channels_list works by creating some public and private channels. """

    user1 = auth_register("email@email.com", "password", "Dr", "Phil")
    user2 = auth_register("email2@email.com", "password", "Judge", "Judy")

    channel1 = channels.channels_create(user1["token"], "public_channel1", True)
    channels.channels_create(user1["token"], "private_channel1", False)
    channels.channels_create(user1["token"], "private_channel2", False)
    channel2 = channels.channels_create(user1["token"], "public_channel2", True)

    channel.channel_join(user2["token"], channel1["channel_id"])
    channel.channel_join(user2["token"], channel2["channel_id"])

    c_list = channels.channels_list(user2["token"])
    assert c_list["channels"][0]["channel_id"] == channel1["channel_id"]
    assert c_list["channels"][1]["channel_id"] == channel2["channel_id"]

######################################################################
#                                                                    #
#                      Testing channels_listall                      #
#                                                                    #
######################################################################

def test_channels_listall_nvt():
    """ Tests if channels_listall raises an AccessError whn the token passed is invalid. """

    with pytest.raises(error.AccessError):
        channels.channels_listall("invalid_token")

def test_channels_listall_empty():
    """ Tests if channels_listall returns an empty list in a dictionary if no channels exist. """

    user = auth_register("email@email.com", "password", "Mr", "Bean")

    c_list = channels.channels_listall(user["token"])
    assert c_list["channels"] == []

def test_channels_listall():
    """ Tests if channels_listall works by creating public and private channels. """

    user1 = auth_register("email@email.com", "password", "Cookie", "Monster")
    user2 = auth_register("email2@email.com", "password", "Big", "Bird")

    channel1 = channels.channels_create(user1["token"], "public_channel1", True)
    channel2 = channels.channels_create(user1["token"], "private_channel1", False)
    channel3 = channels.channels_create(user1["token"], "private_channel2", False)
    channel4 = channels.channels_create(user1["token"], "public_channel2", True)

    channel.channel_join(user2["token"], channel1["channel_id"])
    channel.channel_join(user2["token"], channel4["channel_id"])

    c_list = channels.channels_listall(user2["token"])
    assert c_list["channels"][0]["channel_id"] == channel1["channel_id"]
    assert c_list["channels"][1]["channel_id"] == channel2["channel_id"]
    assert c_list["channels"][2]["channel_id"] == channel3["channel_id"]
    assert c_list["channels"][3]["channel_id"] == channel4["channel_id"]
