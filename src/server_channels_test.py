""" System testing for channels routes. """

import json
import urllib.request

from server import get_url
from server_test_helpers import server_create_user, server_create_channel, server_channel_join


def test_channels_list():
    """ HTTP testing for channels_list """

    # Register users
    user1 = server_create_user("email@email.com", "password", "Donald", "Duck")
    user2 = server_create_user("email2@email.com", "password", "Mickey", "Mouse")

    # Create channels
    channel1 = server_create_channel(user1['token'], "test_channel1", True)
    server_create_channel(user1['token'], "test_channel2", False)

    # user2 joins channel1
    server_channel_join(user2, channel1)

    # user2 calls channels_list
    response = urllib.request.urlopen(f"{get_url()}/channels/list?token={user2['token']}")
    payload = json.load(response)

    assert len(payload['channels']) == 1
    assert payload['channels'][0]['channel_id'] == channel1['channel_id']
    assert payload['channels'][0]['name'] == "test_channel1"

def test_channels_listall():
    """ Http testing for channels_listall. """

    user = server_create_user("email@email.com", "password", "Toby", "Lerone")
    response = urllib.request.urlopen(f"{get_url()}/channels/listall?token={user['token']}")
    payload = json.load(response)

    assert payload['channels'] == []

    channel1 = server_create_channel(user['token'], "test_channel1", True)
    channel2 = server_create_channel(user['token'], "test_channel2", False)

    response = urllib.request.urlopen(f"{get_url()}/channels/listall?token={user['token']}")
    payload = json.load(response)

    assert len(payload['channels']) == 2
    assert payload['channels'][0]['channel_id'] == channel1['channel_id']
    assert payload['channels'][0]['name'] == 'test_channel1'
    assert payload['channels'][1]['channel_id'] == channel2['channel_id']
    assert payload['channels'][1]['name'] == 'test_channel2'
