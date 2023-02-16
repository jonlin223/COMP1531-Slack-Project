""" Http testing for auth routes. """

import json

from server import get_url
from server_test_helpers import (server_create_user, server_auth_login,
                                 server_auth_logout, server_user_profile)

def test_auth():
    """
    testing for auth routes.
    """
    # register the user
    user = server_create_user("email@email.com", "password", "Dennis", "Reynolds")

    # Check that user details are logged
    payload = server_user_profile(user, get_url())

    assert payload['user']['u_id'] == user['u_id']
    assert payload['user']['email'] == "email@email.com"

    # Logout the user
    response = server_auth_logout(user)
    payload = json.load(response)

    assert payload['is_success'] is True

    # Log the user back in
    response = server_auth_login("email@email.com", "password")
    payload = json.load(response)

    # Check that user details are logged
    payload = server_user_profile(user, get_url())

    assert payload['user']['u_id'] == user['u_id']
    assert payload['user']['email'] == "email@email.com"
