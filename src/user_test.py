"""
testing for user/ functions
"""
import json
import urllib.request
import os

import pytest
from PIL import Image, ImageChops

from user import (user_profile, user_profile_setname,
                  user_profile_setemail, user_profile_sethandle, user_profile_uploadphoto
                 )
from server import get_url
from server_test_helpers import server_create_user
from error import InputError, AccessError
from auth import auth_register

#####################################################################
#                                                                   #
#                        Testing user_profile                       #
#                                                                   #
#####################################################################
# Checks user's profile and returns InputError if user
# with u_id is not a valid user.
# Returns AccessError if the user's token is invalid
def test_user_profile_ivt():
    """
    testing with invalid token, should raise an error
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(AccessError):
        user_profile('THISISNOTATOKEN', user['u_id'])

def test_valid_user():
    """
    testing with valid user token, should return user's profile
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    user_profile(user['token'], user['u_id'])

def test_invalid_user():
    """
    testing with a user not in database should raise an error
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile(user['token'], 123)

#####################################################################
#                                                                   #
#                   Testing user_profile_setname                    #
#                                                                   #
#####################################################################
# Checks user's input for first name
# Returns InputError if character length is not with 1 - 50
# Returns AccessError if the user's token is invalid
def test_profile_setname_ivt():
    """
    testing setname invalid token
    """
    auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = "Donald"
    with pytest.raises(AccessError):
        user_profile_setname('THISISNOTATOKEN', first_name, "Trump")

def test_name_first_too_long():
    """
    testing setname first name too long
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = "arealllyreallyreallyreallyreallyreallyreallyreallyreallylongname"
    with pytest.raises(InputError):
        user_profile_setname(user['token'], first_name, "Trump")

def test_name_first_too_short():
    """
    testing first name too short
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = ""
    with pytest.raises(InputError):
        user_profile_setname(user['token'], first_name, "Trump")

def test_valid_name_first():
    """
    testing first name valid
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = "Ronald"
    user_profile_setname(user['token'], first_name, "Trump")

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_first'] == "Ronald"

def test_valid_name_first_1():
    """
    testing first name valid
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = "D"
    user_profile_setname(user['token'], first_name, "Trump")

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_first'] == "D"

def test_valid_name_first_50():
    """
    testing edge case with name 50 chars long
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    first_name = "arealllyreallyreallyreallyreallyreallyreallongname" #here name is 50 chars long
    user_profile_setname(user['token'], first_name, "Trump")

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_first'] == "arealllyreallyreallyreallyreallyreallyreallongname"

# Checks user's input for last name
# Returns InputError if character length is not with 1 - 50
def test_name_last_too_long():
    """
    test with last name too long
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    last_name = "arealllyreallyreallyreallyreallyreallyreallyreallyreallylongname"
    with pytest.raises(InputError):
        user_profile_setname(user['token'], "Donald", last_name)

def test_name_last_too_short():
    """
    test last name too short
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    last_name = ""
    with pytest.raises(InputError):
        user_profile_setname(user['token'], "Donald", last_name)

def test_valid_name_last():
    """
    test with valid lastname
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    last_name = "Dump"
    user_profile_setname(user['token'], "Donald", last_name)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_last'] == "Dump"

def test_valid_name_last_1():
    """
    test with valid lastname
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    last_name = "T"
    user_profile_setname(user['token'], "Donald", last_name)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_last'] == "T"

def test_valid_name_last_50():
    """
    test edge case with last name 50 chars
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    last_name = "arealllyreallyreallyreallyreallyreallyreallongname" #here name is 50 chars long
    user_profile_setname(user['token'], "Donald", last_name)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['name_last'] == "arealllyreallyreallyreallyreallyreallyreallongname"

#####################################################################
#                                                                   #
#                   Testing user_profile_setemail                   #
#                                                                   #
#####################################################################
# Tests whether the inputed email is valid
# Returns InputError if the email provided is invalid
# Returns AccessError if the user's token is invalid
def test_setemail_ivt():
    """
    test with set email invalid token
    """
    auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(AccessError):
        user_profile_setemail('THISISNOTATOKEN', "nguyenh@gmail.com")

def test_invalid_email_1():
    """
    test setemail with invalid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], "nguyen.com")

def test_invalid_email_2():
    """
    test setemail with invalid token
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], "nguyen")

def test_invalid_email_3():
    """
    test setemail with invalid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], "123456")

def test_invalid_email_4():
    """
    test setemail with invalid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], "nguyen@nguyen")

def test_invalid_email_5():
    """
    test setemail with invalid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], "!@#$%^&*()_")

def test_valid_email_1():
    """
    test setemail with valid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    user_profile_setemail(user['token'], "nguyenh@gmail.com")

def test_valid_email_2():
    """
    test setemail with valid email
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    user_profile_setemail(user['token'], "z5257125@ad.unsw.edu.au")

# Tests if the email provided is already taken
# Returns Inputerror if the email is already taken
def test_email_already_taken():
    """
    test setemail email already taken
    """
    auth_register("email@email.com", "password", "Donald", "Trump")
    user2 = auth_register("email2@email.com", "password2", "Donald2", "Trump2")
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], "email@email.com")

def test_email_not_taken():
    """
    test setemail email not taken
    """
    auth_register("email@email.com", "password", "Donald", "Trump")
    user2 = auth_register("email2@email.com", "password2", "Donald2", "Trump2")
    user_profile_setemail(user2['token'], "nguyenh@email.com")

#####################################################################
#                                                                   #
#                   Testing user_profile_sethandle                  #
#                                                                   #
#####################################################################
# Tests if the inputed handle name is with 3 - 20 characters
# Returns InputError if the user's input is invalid
# Returns AccessError if the user's token is invalid
def test_sethandle_ivt():
    """
    test set handle with invalid token
    """
    auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "Handle"
    with pytest.raises(AccessError):
        user_profile_sethandle('THISISNOTATOKEN', handle_str)

def test_handle_length_too_long():
    """
    test set handle with a handle string too long
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "arealllyreallyreallyreallyreallyreallyreallyreallyreallylongname"
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], handle_str)

def test_handle_length_too_short():
    """
    test set handle with handle string too short
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "h"
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], handle_str)

def test_valid_handle_length():
    """
    test set handle with valid handle string
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "Agoodhandle"
    user_profile_sethandle(user['token'], handle_str)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['handle_str'] == "Agoodhandle"

def test_valid_handle_length_3():
    """
    test edge case of handle string length of 3
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "one" # testing for 3 chars, function should work
    user_profile_sethandle(user['token'], handle_str)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['handle_str'] == "one"

def test_valid_handle_length_20():
    """
    test edge case with handle string length of 20
    """
    user = auth_register("email@email.com", "password", "Donald", "Trump")
    handle_str = "ahandlewith20charsss"
    user_profile_sethandle(user['token'], handle_str)

    user_p = user_profile(user['token'], user['u_id'])

    assert user_p['user']['handle_str'] == "ahandlewith20charsss"

# Tests if the inputed handle hs already been taken
# Returns InputError if the handle name is taken
def test_handle_already_taken():
    """
    testing set handle if handle string is already taken
    """
    user1 = auth_register("email@email.com", "password", "Donald", "Trump")
    user2 = auth_register("email2@email.com", "password2", "Donald2", "Trump2")
    handle_str = "handle"
    user_profile_sethandle(user1['token'], handle_str)
    with pytest.raises(InputError):
        user_profile_sethandle(user2['token'], handle_str)

#####################################################################
#                                                                   #
#                   Testing user_profile_uploadphoto                #
#                                                                   #
#####################################################################


def test_uploadphoto_normal():
    """
    Test the profile_upload is working with correct input
    """
    req = urllib.request.Request(f"{get_url()}/workspace/reset", method='POST')
    urllib.request.urlopen(req)
    user = server_create_user("email@email.com", "password", "Donald", "Trump")
    img_url = 'http://personal.psu.edu/rrk5146/art3/jpegsystems-home.jpg'
    # try to change email
    data = json.dumps({'token': user['token'],
                       'img_url' : img_url,
                       'x_start' : 0,
                       'y_start' : 0,
                       'x_end' : 690,
                       'y_end' : 323
                      }).encode('utf-8')
    #the giving x_end and y_end should save the whole picture.
    req = urllib.request.Request(f"{get_url()}/user/profile/uploadphoto",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    urllib.request.urlopen(req)
    req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    img_file = Image.open(response)

    img_path = os.path.join(os.path.dirname(__file__), "static/1.jpg")

    profile_img = Image.open(img_path)
    diff = ImageChops.difference(img_file, profile_img)
    assert diff.show() is None
    img_file.close()
    profile_img.close()

def test_uploadphoto_png():
    """
    Test whether the PNG formate file raise InputError
    """
    user1 = auth_register("email@email.com", "password", "Donald", "Trump")
    test_url = "https://external-content.duckduckgo.com" + (
        "/iu/?u=http%3A%2F%2Fd.ibtimes.co.uk%2Fen%2Ffull%2F1555403%2F4"+
        "chan-closure-pepe-frog.png&f=1&nofb=1"
    )
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], test_url, 0, 0, 1, 1)

def test_uploadphoto_beyond_bord():
    """
    Test whether having x and y outside image dimensions raises InputError
    """
    user1 = auth_register("email@email.com", "password", "Donald", "Trump")
    test_url = "http://personal.psu.edu/rrk5146/art3/jpegsystems-home.jpg"
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], test_url, 0, 0, 1000, 1000)

def test_uploadphoto_invalid_url():
    """
    Test whether the incorrect url will raise InputError
    """
    user1 = auth_register("email@email.com", "password", "Donald", "Trump")
    with pytest.raises(InputError):
        user_profile_uploadphoto(user1['token'], "bad_url", 0, 0, 1, 1)
        