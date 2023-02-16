""" Http testing for workspace. """

import json
import urllib.request
from urllib.error import HTTPError
import pytest

from server import get_url
from server_test_helpers import server_create_user, server_create_channel


def test_workspace_reset():
    """ Test if workspace successfully reset. """
    user_dict = server_create_user("email@email.com", "password7", "Will", "Williamson")
    c_id_dict = server_create_channel(user_dict['token'], "test_channel", True)

    response_details = urllib.request.urlopen(f"{get_url()}/users/all?token={user_dict['token']}")
    details_decoded = json.load(response_details)
    assert details_decoded['users'] == [{"u_id": 1, "email": "email@email.com",
                                         'profile_img_url': 'http://127.0.0.1:8080/static/bean.jpg',
                                         "name_first": "Will", "name_last": "Williamson",
                                         "handle_str": "willwilliamson"}]

    url = (f"{get_url()}/channel/details?token={user_dict['token']}" +
           f"&channel_id={c_id_dict['channel_id']}")
    response_details = urllib.request.urlopen(url)
    details_decoded = json.load(response_details)
    assert details_decoded['all_members'] == [{"u_id": 1, "name_first": "Will",
                                               "name_last": "Williamson",
                                               "profile_img_url":
                                                   "http://127.0.0.1:8080/static/bean.jpg"}]

    clear_request = urllib.request.Request(f"{get_url()}/workspace/reset", method="POST")
    urllib.request.urlopen(clear_request)

    # We expect an error, because the user is no longer registered and so their token is invalid
    with pytest.raises(HTTPError):
        urllib.request.urlopen(f"{get_url()}/users/all?token={user_dict['token']}")
