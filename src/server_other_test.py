""" System testing for other routes """

import json
import urllib.request
from datetime import datetime

from server import get_url
from server_test_helpers import (server_create_user, server_create_channel, server_channel_invite,
                                 server_users_all)

def test_users_all():
    """ Http testing for user/profile. """
    # Register user
    user = server_create_user("email3@email.com", "password", "Donald", "Trump!")
    server_create_user("email4@email.com", "password", "Donald", "Duck!")
    payload = server_users_all(user)
    # assert that all users are in the list
    assert payload['users'] == [{'u_id': 1,
                                 'email': 'email3@email.com',
                                 'name_first': 'Donald',
                                 'name_last': 'Trump!',
                                 'handle_str': 'donaldtrump!',
                                 'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg'
                                },
                                {'u_id': 2,
                                 'email': 'email4@email.com',
                                 'name_first': 'Donald',
                                 'name_last': 'Duck!',
                                 'handle_str': 'donaldduck!',
                                 'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg'
                                }]

def test_search():
    """ Http testing for users/all. """
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")
    user2 = server_create_user("email2@email.com", "password", "Donald", "Duck")

    # create channel join and invite second user to join
    c_id_dict = server_create_channel(user['token'], "test_channel", True)

    server_channel_invite(user2, user, c_id_dict)

    # send some messages
    data = json.dumps({'token': user['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "HI IM NGUYEN"}).encode('utf-8')
    server_request = urllib.request.Request(f"{get_url()}/message/send",
                                            data=data,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")
    urllib.request.urlopen(server_request)
    time_create_date = datetime.now().replace(microsecond=0)
    time_create_1 = time_create_date.timestamp()

    data = json.dumps({'token': user2['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "HI it's nguyen"}).encode('utf-8')
    server_request = urllib.request.Request(f"{get_url()}/message/send",
                                            data=data,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")
    urllib.request.urlopen(server_request)
    time_create_date = datetime.now().replace(microsecond=0)
    time_create_2 = time_create_date.timestamp()

    data = json.dumps({'token': user['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "hi im nguyen"}).encode('utf-8')
    server_request = urllib.request.Request(f"{get_url()}/message/send",
                                            data=data,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")
    urllib.request.urlopen(server_request)

    data = json.dumps({'token': user2['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "hi im nguyen"}).encode('utf-8')
    server_request = urllib.request.Request(f"{get_url()}/message/send",
                                            data=data,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")
    urllib.request.urlopen(server_request)

    data = json.dumps({'token': user2['token'],
                       'channel_id': c_id_dict['channel_id'],
                       'message': "hello"}).encode('utf-8')
    server_request = urllib.request.Request(f"{get_url()}/message/send",
                                            data=data,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")
    urllib.request.urlopen(server_request)

    # search for message
    payload = json.load(urllib.request.urlopen(
        f"{get_url()}/search?token={user['token']}&query_str=HI"))

    assert payload['messages'] == [{'message_id': 1,
                                    'u_id': 2,
                                    'message': "HI it's nguyen",
                                    'time_created': time_create_2,
                                    'reacts': [{'react_id': 1,
                                                'u_ids': [],
                                                'is_this_user_reacted': False}],
                                    'is_pinned': False
                                   },
                                   {'message_id': 0,
                                    'u_id': 1,
                                    'message': "HI IM NGUYEN",
                                    'time_created': time_create_1,
                                    'reacts': [{'react_id': 1,
                                                'u_ids': [],
                                                'is_this_user_reacted': False}],
                                    'is_pinned': False
                                   }]
