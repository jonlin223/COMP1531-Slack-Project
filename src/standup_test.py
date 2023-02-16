""" File contains tests for standup functions. """

import time
import pytest
import standup
import error
import auth
import channel
import channels
import message

@pytest.fixture(autouse=True)
def clean_standup_database():
    """ Clean standup database after every pytest run. """

    standup.clean_standup_database()

###################################################################
#                                                                 #
#                      Testing standup_start                      #
#                                                                 #
###################################################################

def test_standup_start_nvid():
    """ Tests if standup_start raises an InputError if the channel_id given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Donkey", "Kong")

    with pytest.raises(error.InputError):
        standup.standup_start(user['token'], 100, 100)

def test_standup_start_active():
    """ Tests if standup_start raises an InputError if there is already an active standup. """

    user = auth.auth_register("email@email.com", "password", "Corona", "Virus")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.InputError):
        standup.standup_start(user['token'], channel_dict['channel_id'], 1000)
    time.sleep(1)

def test_standup_start_nvt():
    """ Tests if standup_start raises an AccessError if the token given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Dwayne", "Johnson")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    with pytest.raises(error.AccessError):
        standup.standup_start("InvalidToken", channel_dict['channel_id'], 100)

def test_standup_start_empty():
    """ Tests if no messages sent if no user uses standup_send during the time given. """

    user = auth.auth_register("email@email.com", "password", "Solid", "Snake")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    # Send a message so that a call of channel_messages does not raise an InputError
    message.message_send(user['token'], channel_dict['channel_id'], "message")

    # Start a 1 second long startup and then pause the code for sufficient duration of time
    standup.standup_start(user['token'], channel_dict['channel_id'], 1)
    time.sleep(2)

    # Use channel_messages to check that the only message is "message"
    message_dict = channel.channel_messages(user['token'], channel_dict['channel_id'], 0)
    assert len(message_dict['messages']) == 1
    assert message_dict['messages'][0]['message'] == "message"

def test_standup_start():
    """ Tests if standup_start and standup_send works. """

    user1 = auth.auth_register("email1@email.com", "password", "Bilbo", "Baggins")
    user2 = auth.auth_register("email2@email.com", "password", "Frodo", "Baggins")
    user3 = auth.auth_register("email3@email.com", "password", "Master", "Sauron")
    channel_dict = channels.channels_create(user1['token'], "test_channel", True)

    channel.channel_join(user2['token'], channel_dict['channel_id'])
    channel.channel_join(user3['token'], channel_dict['channel_id'])

    standup.standup_start(user1['token'], channel_dict['channel_id'], 1)
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message1")
    standup.standup_send(user2['token'], channel_dict['channel_id'], "message2")
    standup.standup_send(user3['token'], channel_dict['channel_id'], "message3")

    time.sleep(2)
    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)

    assert len(message_dict['messages']) == 1
    assert message_dict['messages'][0]['message'] == ("bilbobaggins: message1\n" +
                                                      "frodobaggins: message2\n" +
                                                      "mastersauron: message3")

####################################################################
#                                                                  #
#                      Testing standup_active                      #
#                                                                  #
####################################################################

def test_standup_active_nvid():
    """ Tests if standup_active raises an InputError if the channel_id given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Just", "Monika")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.InputError):
        standup.standup_active(user['token'], 100)
    time.sleep(1)

def test_standup_active_nvt():
    """ Tests if standup_active raises an AccessError if the token given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Bat", "Man")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.AccessError):
        standup.standup_active("InvalidToken", channel_dict['channel_id'])
    time.sleep(1)

def test_standup_active_inactive():
    """ Tests if standup_active returns correct output when no standup is active. """

    user = auth.auth_register("email@email.com", "password", "Pika", "Power")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    current = standup.standup_active(user['token'], channel_dict['channel_id'])
    assert current['is_active'] is False
    assert current['time_finish'] is None

def test_standup_active():
    """ Tests if standup_active works. """

    user = auth.auth_register("email@email.com", "password", "Lightning", "McQueen")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    time_finish = standup.standup_start(user['token'], channel_dict['channel_id'], 1)
    current = standup.standup_active(user['token'], channel_dict['channel_id'])
    assert current['is_active'] is True
    assert current['time_finish'] == time_finish['time_finish']
    time.sleep(1)

##################################################################
#                                                                #
#                      Testing standup_send                      #
#                                                                #
##################################################################

def test_standup_send_nvid():
    """ Tests if standup_send raises an InputError if channel_id given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Cat'n", "America")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], 100, "message")
    time.sleep(1)

def test_standup_send_length():
    """ Tests if standup_send raises an InputError
    if message is more than 1000 characters long. """

    user = auth.auth_register("email@email.com", "password", "Samus", "Aran")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel_dict['channel_id'], 'a' * 1001)
    time.sleep(1)

def test_standup_send_inactive():
    """ Tests if standup_send raises an InputError if no standup is active. """

    user = auth.auth_register("email@email.com", "password", "Purple", "TellyTubby")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel_dict['channel_id'], "message")

def test_standup_send_other():
    """ Tests if standup_send raises an InputError if no standup active in given channel.
    but there is an active standup in another channel. """

    user = auth.auth_register("email@email.com", "password", "Pingu", "Noot")
    channel_dict1 = channels.channels_create(user['token'], "test_channel1", False)
    channel_dict2 = channels.channels_create(user['token'], "test_channel2", False)

    standup.standup_start(user['token'], channel_dict1['channel_id'], 1)

    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel_dict2['channel_id'], "message")
    time.sleep(1)

def test_standup_send_nvt():
    """ Tests if standup_send raises an AccessError if the token given is invalid. """

    user = auth.auth_register("email@email.com", "password", "Peppa", "Pig")
    channel_dict = channels.channels_create(user['token'], "test_channel", False)

    standup.standup_start(user['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.AccessError):
        standup.standup_send("InvalidToken", channel_dict['channel_id'], "message")
    time.sleep(1)

def test_standup_send_not_member():
    """ Tests if standup_send raises an AccessError if user is not a member of the channel. """

    user1 = auth.auth_register("email1@email.com", "password", "Night", "Man")
    user2 = auth.auth_register("email2@email.com", "password", "Day", "Man")
    channel_dict = channels.channels_create(user1['token'], "test_channel", False)

    standup.standup_start(user1['token'], channel_dict['channel_id'], 1)

    with pytest.raises(error.AccessError):
        standup.standup_send(user2['token'], channel_dict['channel_id'], "message")
    time.sleep(1)

# Testing for case where standup_send works is integrated into test_standup_start
