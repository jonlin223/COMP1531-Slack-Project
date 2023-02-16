"""
Tests the HTTP implementation of all channel/* routes.
"""

import json
import urllib.request

from server import get_url
from server_test_helpers import (server_create_user, server_create_channel,
                                 server_channel_join, server_channel_invite)


def test_server_channel_invite():
    """ Http testing for channel/invite. """
    user_dict = server_create_user("email@email.com", "password7", "Will", "Williamson")
    user_dict_2 = server_create_user("email2@email.com", "password7", "Bill", "William")
    c_id_dict = server_create_channel(user_dict['token'], "test_channel", True)

    server_channel_invite(user_dict_2, user_dict, c_id_dict)

    response = urllib.request.urlopen(f"{get_url()}/channel/details?token={user_dict['token']}"
                                      +f"&channel_id={c_id_dict['channel_id']}")
    details_decoded = json.load(response)

    assert details_decoded['all_members'] == [{"u_id": 1,
                                               "name_first": "Will",
                                               "name_last": "Williamson",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"},
                                              {"u_id": 2,
                                               "name_first": "Bill",
                                               "name_last": "William",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"}]

def test_server_channel_owner():
    """ Http testing for channel/addowner and channel/removeowner. """

    user1 = server_create_user("email@email.com", "password", "Robbie", "Rotten")
    user2 = server_create_user("email2@email.com", "password", "Sport", "Acus")
    channel = server_create_channel(user1['token'], "test_channel", True)

    # user2 joins channel
    server_channel_join(user2, channel)

    # user1 adds user2 as an owner
    data = json.dumps({'token': user1['token'],
                       'channel_id': channel['channel_id'],
                       'u_id': user2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/channel/addowner",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)

    # Check that user2 is an owner using channel/details
    url = f"{get_url()}/channel/details?token={user1['token']}&channel_id={channel['channel_id']}"
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    assert len(payload['owner_members']) == 2
    assert payload['owner_members'][0]['u_id'] == user1['u_id']
    assert payload['owner_members'][1]['u_id'] == user2['u_id']

    # user1 removes user2 as an owner
    data = json.dumps({'token': user1['token'],
                       'channel_id': channel['channel_id'],
                       'u_id': user2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/channel/removeowner",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)

    # Check that user2 is no longer an owner using channel/details
    url = f"{get_url()}/channel/details?token={user1['token']}&channel_id={channel['channel_id']}"
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    assert len(payload['owner_members']) == 1
    assert payload['owner_members'][0]['u_id'] == user1['u_id']
    assert payload['all_members'] == [{"u_id": 1, "name_first": "Robbie", "name_last": "Rotten",
                                       "profile_img_url": "http://127.0.0.1:8080/static/bean.jpg"},
                                      {"u_id": 2, "name_first": "Sport", "name_last": "Acus",
                                       "profile_img_url": "http://127.0.0.1:8080/static/bean.jpg"}]

def test_server_channel_details():
    """ Http testing for channel/details. """
    user_dict = server_create_user("email@email.com", "password1", "Bob", "Ross")

    test_channel = server_create_channel(user_dict['token'], "Test Rum Ham", True)

    response = urllib.request.urlopen(f"{get_url()}/channel/details?token={user_dict['token']}"
                                      +f"&channel_id={test_channel['channel_id']}")

    payload = json.load(response)

    assert payload["name"] == "Test Rum Ham"
    assert payload["all_members"] == [{"u_id": user_dict["u_id"],
                                       "name_first": "Bob",
                                       "name_last": "Ross",
                                       "profile_img_url":
                                           "http://127.0.0.1:8080/static/bean.jpg"}]
    assert payload["owner_members"] == [{"u_id": user_dict["u_id"],
                                         "name_first": "Bob",
                                         "name_last": "Ross",
                                         "profile_img_url":
                                             "http://127.0.0.1:8080/static/bean.jpg"}]

def test_server_channel_messages():
    """ Http testing for channel/messages. """
    user_dict = server_create_user("email@email.com", "password1", "Bob", "Ross")

    test_channel = server_create_channel(user_dict['token'], "Test Rum Ham", True)

    payload = json.dumps({"token": user_dict['token'],
                          "channel_id": test_channel['channel_id'],
                          "message": "This is a test message"}).encode('utf-8')

    server_message_send = urllib.request.Request(f"{get_url()}/message/send",
                                                 data=payload,
                                                 headers={"Content-Type": "application/json"},
                                                 method="POST")

    send_response = urllib.request.urlopen(server_message_send)
    decoded_send_response = json.load(send_response)

    response = urllib.request.urlopen(f"{get_url()}/channel/messages?token={user_dict['token']}"
                                      +f"&channel_id={test_channel['channel_id']}&start={0}")

    payload = json.load(response)

    assert payload['messages'][0]['message'] == "This is a test message"
    assert payload['messages'][0]['message_id'] == decoded_send_response['message_id']
    assert payload['start'] == 0
    assert payload['end'] == -1

def test_server_channel_join_leave():
    """ Http testing for channel/leave. """
    user_dict = server_create_user("email@email.com", "password1", "Bob", "Ross")
    user_dict_2 = server_create_user("email2@email.com", "password7", "Bill", "William")

    test_channel = server_create_channel(user_dict['token'], "Test Rum Ham", True)

    payload = json.dumps({"token": user_dict_2['token'],
                          "channel_id": test_channel['channel_id']}).encode('utf-8')

    server_channel_join(user_dict_2, test_channel)

    response = urllib.request.urlopen(f"{get_url()}/channel/details?token={user_dict['token']}"
                                      +f"&channel_id={test_channel['channel_id']}")
    details_decoded = json.load(response)

    assert details_decoded['all_members'] == [{"u_id": 1,
                                               "name_first": "Bob",
                                               "name_last": "Ross",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"},
                                              {"u_id": 2,
                                               "name_first": "Bill",
                                               "name_last": "William",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"}]

    assert details_decoded['owner_members'] == [{"u_id": 1,
                                                 "name_first": "Bob",
                                                 "name_last": "Ross",
                                                 "profile_img_url":
                                                     "http://127.0.0.1:8080/static/bean.jpg"}]

    payload = json.dumps({"token": user_dict_2['token'],
                          "channel_id": test_channel['channel_id']}).encode('utf-8')

    server_channel_leave = urllib.request.Request(f"{get_url()}/channel/leave",
                                                  data=payload,
                                                  headers={"Content-Type": "application/json"},
                                                  method="POST")
    urllib.request.urlopen(server_channel_leave)

    response = urllib.request.urlopen(f"{get_url()}/channel/details?token={user_dict['token']}"
                                      +f"&channel_id={test_channel['channel_id']}")
    details_decoded = json.load(response)

    assert details_decoded['all_members'] == [{"u_id": 1, "name_first": "Bob",
                                               "name_last": "Ross",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"}]
    assert len(details_decoded['all_members']) == 1
