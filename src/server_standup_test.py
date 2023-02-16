""" System testing for standup routes. """

import json
import urllib.request
import time

from server import get_url
from server_test_helpers import server_create_user, server_create_channel, server_channel_join

def send_standup_message(token, channel_id, message):
    """ Use standup/send route. """

    data = json.dumps({'token': token,
                       'channel_id': channel_id,
                       'message': message}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/standup/send",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)

def test_standup():
    """ Http testing for standup functions.
    coverage ensured by calling each function. """

    user1 = server_create_user("email@email.com", "password", "Lich", "King")
    user2 = server_create_user("email2@email.com", "password", "Gold", "Tooth")
    channel = server_create_channel(user1['token'], "test_channel", True)

    # user2 joins channel
    server_channel_join(user2, channel)

    # call standup_start
    data = json.dumps({'token': user1['token'],
                       'channel_id': channel['channel_id'],
                       'length': 3}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/standup/start",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    response = urllib.request.urlopen(req)
    standup = json.load(response)

    # call standup_active
    url = f"{get_url()}/standup/active?token={user1['token']}&channel_id={channel['channel_id']}"
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    # assert that standup is active
    assert payload['is_active'] is True
    assert payload['time_finish'] == standup['time_finish']

    # call standup_send
    send_standup_message(user1['token'], channel['channel_id'], "hello")
    send_standup_message(user2['token'], channel['channel_id'], "there")

    # wait out the rest of the standup and check messages
    time.sleep(3)
    url = (f"{get_url()}/channel/messages?token={user1['token']}" +
           f"&channel_id={channel['channel_id']}&start=0")
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    assert len(payload['messages']) == 1
    assert payload['messages'][0]['message'] == "lichking: hello\ngoldtooth: there"
