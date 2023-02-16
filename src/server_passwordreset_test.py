""" System testing for passwordreset routes """

import json
import urllib.request

from server import get_url
from server_test_helpers import server_create_user, server_auth_login, server_auth_logout

def test_password_reset():
    """ Testing for password reset routes """
    # Register user
    user = server_create_user("email@email.com", "password", "Donald", "Trump")
    # log user out
    response = server_auth_logout(user)
    payload = json.load(response)
    assert payload['is_success'] is True
    # request password reset
    data = json.dumps({'email': 'email@email.com'}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/auth/passwordreset/request",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)
    req = urllib.request.Request(f"{get_url()}/auth/passwordreset/reset_code",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    response = urllib.request.urlopen(req)
    reset_code = json.load(response)
    # try reset password
    data = json.dumps({'reset_code': reset_code, 'new_password': 'a1b2c3d4e5'}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/auth/passwordreset/reset",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)
    # log the user back in
    response = server_auth_login("email@email.com", "a1b2c3d4e5")
    payload = json.load(response)
    # check user profile is the same user
    url = f"{get_url()}/user/profile?token={user['token']}&u_id={user['u_id']}"
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    assert payload['user']['u_id'] == user['u_id']
    assert payload['user']['email'] == "email@email.com"
