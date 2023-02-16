""" Helper functions used across most server-side tests """

import json
import urllib.request

from server import get_url

URL = get_url()

def server_create_user(email, password, name_first, name_last):
    """
    HTTP request for create user.
    """
    payload = json.dumps({"email": email, "password": password, "name_first": name_first,
                          "name_last": name_last}).encode('utf-8')

    server_request = urllib.request.Request(f"{URL}/auth/register",
                                            data=payload,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")

    response = urllib.request.urlopen(server_request)

    return json.load(response)

def server_create_channel(token, name, is_public):
    """
    HTTP request for channel_create
    """
    payload = json.dumps({"token": token, "name": name, "is_public": is_public}).encode('utf-8')

    server_request = urllib.request.Request(f"{URL}/channels/create",
                                            data=payload,
                                            headers={"Content-Type": "application/json"},
                                            method="POST")

    response = urllib.request.urlopen(server_request)
    return json.load(response)

def server_channel_invite(invited, inviter, c_id_dict):
    """ HTTP request for channel invite """
    payload = json.dumps({"token": inviter['token'], "channel_id": c_id_dict['channel_id'],
                          "u_id": invited['u_id']}).encode('utf-8')
    server_request_invite = urllib.request.Request(f"{URL}/channel/invite",
                                                   data=payload,
                                                   headers={"Content-Type": "application/json"},
                                                   method="POST")
    urllib.request.urlopen(server_request_invite)

def server_channel_join(user, channel):
    """ HTTP request for channel join """

    data = json.dumps({'token': user['token'],
                       'channel_id':
                       channel['channel_id']}).encode('utf-8')
    req = urllib.request.Request(f"{URL}/channel/join",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)

def server_auth_login(email, password):
    """ HTTP request for auth login """
    data = json.dumps({'email': email, 'password': password}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/auth/login",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    response = urllib.request.urlopen(req)

    return response

def server_auth_logout(user):
    """ HTTP request for auth login """
    data = json.dumps({'token': user['token']}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/auth/logout",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    response = urllib.request.urlopen(req)

    return response

def server_user_profile(user, base_url):
    """ HTTP request for user profile """
    url = f"{base_url}/user/profile?token={user['token']}&u_id={user['u_id']}"
    response = urllib.request.urlopen(url)

    payload = json.load(response)

    return payload

def server_users_all(user):
    """ HTTP request for users all """
    payload = json.load(urllib.request.urlopen(f"{get_url()}/users/all?token={user['token']}"))

    return payload
