"""
Testing file for admin route
"""
import json
import urllib.request

from server import get_url
from server_test_helpers import (server_create_user, server_create_channel, server_channel_invite,
                                 server_users_all)

def test_server_change_perms():
    """
    Test owner 1 is Global Owner by checking he gains owner privileges to someone else's channel
    when he joins it.
    """
    #1st is owner, second is member.
    user_dict = server_create_user("email@email.com", "password7", "Will", "Williamson")
    user_dict_2 = server_create_user("email2@email.com", "password7", "Bill", "William")

    # Server member (2) creates channel, invites server owner.
    c_id_dict = server_create_channel(user_dict_2['token'], "test_channel", True)

    server_channel_invite(user_dict, user_dict_2, c_id_dict)

    response = urllib.request.urlopen(f"{get_url()}/channel/details?token={user_dict['token']}"
                                      +f"&channel_id={c_id_dict['channel_id']}")
    details_decoded = json.load(response)

    print(details_decoded['owner_members'])

    assert details_decoded['owner_members'] == [{"u_id": 2, "name_first": "Bill",
                                                 "name_last": "William",
                                                 "profile_img_url":
                                                 "http://127.0.0.1:8080/static/bean.jpg"},
                                                {"u_id": 1, "name_first": "Will",
                                                 "name_last": "Williamson",
                                                 "profile_img_url":
                                                 "http://127.0.0.1:8080/static/bean.jpg"}]

def test_server_remove_user():
    """
    testing for user remove route.
    """
    # Create users
    user = server_create_user("email@email.com", "password", "Donald", "Trump")
    user2 = server_create_user("email2@email.com", "password", "Donald", "Duck")
    # get list of all users assert that there are two users
    payload = server_users_all(user)
    assert payload['users'] == [{'u_id': 1,
                                 'email': 'email@email.com',
                                 'name_first': 'Donald',
                                 'name_last': 'Trump',
                                 'handle_str': 'donaldtrump',
                                 'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg'
                                },
                                {'u_id': 2,
                                 'email': 'email2@email.com',
                                 'name_first': 'Donald',
                                 'name_last': 'Duck',
                                 'handle_str': 'donaldduck',
                                 'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg'
                                }]
    # Create a channel and invite the second user
    c_id_dict = server_create_channel(user['token'], "test_channel", True)
    data = json.dumps({'token': user['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'u_id': user2['u_id']}).encode('utf-8')
    server_request_invite = urllib.request.Request(f"{get_url()}/channel/invite",
                                                   data=data,
                                                   headers={"Content-Type": "application/json"},
                                                   method="POST")
    urllib.request.urlopen(server_request_invite)
    # send a message as the second user
    data = json.dumps({'token': user2['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "This is a test message"}).encode('utf-8')
    server_message_send = urllib.request.Request(f"{get_url()}/message/send",
                                                 data=data,
                                                 headers={"Content-Type": "application/json"},
                                                 method="POST")
    response = urllib.request.urlopen(server_message_send)
    send_response = json.load(response)
    # remove the second user from slakr
    data = json.dumps({'token': user['token'], 'u_id': user2['u_id']}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/admin/user/remove",
                                 data=data,
                                 headers={"Content-Type": "application/json"},
                                 method="DELETE")
    urllib.request.urlopen(req)
    # get list of all users and assert that there is only one user left in data.
    payload = json.load(urllib.request.urlopen(f"{get_url()}/users/all?token={user['token']}"))
    assert payload['users'] == [{'u_id': 1,
                                 'email': 'email@email.com',
                                 'name_first': 'Donald',
                                 'name_last': 'Trump',
                                 'handle_str': 'donaldtrump',
                                 'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg'
                                }]
    # assert that the second user has been removed from channel members list
    req = urllib.request.urlopen(f"{get_url()}/channel/details?token={user['token']}"
                                 +f"&channel_id={c_id_dict['channel_id']}")
    payload = json.load(req)
    assert payload['all_members'] == [{"u_id": 1,
                                       "name_first": "Donald",
                                       "name_last": "Trump",
                                       "profile_img_url": "http://127.0.0.1:8080/static/bean.jpg"}]
    # assert removed user's messages still remain
    response = urllib.request.urlopen(f"{get_url()}/channel/messages?token={user['token']}"
                                      +f"&channel_id={c_id_dict['channel_id']}&start={0}")
    payload = json.load(response)
    assert payload['messages'][0]['message'] == "This is a test message"
    assert payload['messages'][0]['message_id'] == send_response['message_id']
