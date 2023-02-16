""" System testing for user routes """

import json
import urllib.request

from server import get_url
from server_test_helpers import server_create_user


URL = get_url()

def test_user_profile():
    """ Http testing for user/profile. """
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")
    payload = json.load(urllib.request.urlopen(
        f"{get_url()}/user/profile?token={user['token']}&u_id=1"))
    # assert user profile is what we set it to be
    assert payload['user']['name_first'] == "Donald"
    assert payload['user']['name_last'] == "Trump"
    assert payload['user']['email'] == "email@email.com"
    assert payload['user']['handle_str'] == "donaldtrump"

def test_user_profile_setname():
    """ Http testing for user/profile/setname."""
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")

    # try to change name
    data = json.dumps({'token': user['token'],
                       'name_first': 'Much',
                       'name_last': 'Bettername'}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/user/profile/setname",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='PUT')
    response = urllib.request.urlopen(req)

    # Use user/profile to check details
    response = urllib.request.urlopen(f"{get_url()}/user/profile?token={user['token']}&u_id=1")
    payload = json.load(response)

    assert payload['user']['name_first'] == "Much"
    assert payload['user']['name_last'] == "Bettername"

def test_user_profile_setemail():
    """ Http testing for user/profile/setemail """
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")

    # try to change email
    data = json.dumps({'token': user['token'],
                       'email' : 'email123@email.com'}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/user/profile/setemail",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='PUT')
    response = urllib.request.urlopen(req)

    # use user/profile to check emails
    response = urllib.request.urlopen(f"{get_url()}/user/profile?token={user['token']}&u_id=1")
    payload = json.load(response)

    assert payload['user']['email'] == "email123@email.com"

def test_user_profile_set_handle():
    """ Http testing for user/profile/sethandle """
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")

    # try to change handle
    data = json.dumps({'token': user['token'],
                       'handle_str' : 'abetterhandle'}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/user/profile/sethandle",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='PUT')
    response = urllib.request.urlopen(req)

    # use user/profile to check handle str
    response = urllib.request.urlopen(f"{get_url()}/user/profile?token={user['token']}&u_id=1")
    payload = json.load(response)

    assert payload['user']['handle_str'] == "abetterhandle"
