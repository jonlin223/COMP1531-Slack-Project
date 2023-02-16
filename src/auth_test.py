""" integration testing for auth functions """

import pytest

from user import user_profile
import auth
import error

####################################################################
#
#                      Testing auth_login
#
#####################################################################

def test_login_already_logged():
    """ Test that auth_login raises exception id user already logged in. """
    auth.auth_register("test@email.com", "password", "Barry", "Benson")

    with pytest.raises(error.AccessError):
        auth.auth_login("test@email.com", "password")

def test_login_invalid_email():
    """ Check InputError is thrown when an incorrect email format is entered. """
    with pytest.raises(error.InputError):
        auth.auth_login("not_a_proper_email.com", "password")


def test_login_incorrect_password():
    """ Check InputError is thrown when an incorrect password is entered. """
    user_session = auth.auth_register("test@email.com", "password", "Sheev", "Palpatine")
    auth.auth_logout(user_session.get('token'))

    with pytest.raises(error.InputError):
        auth.auth_login("test@email.com", "wrong_password")

def test_login_email_unregistered():
    """ Email logging in with is valid but doesn't belong to an account. """
    with pytest.raises(error.InputError):
        auth.auth_login("unreg_email@email.com", "password")

def test_login_valid():
    """ Check that a valid login attempt throws no error. """
    # Check for valid token and valid uID.
    user_session = auth.auth_register("test@email.com", "password", "Mr", "Creosote")
    print(user_session)
    user_p = user_profile(user_session['token'], user_session['u_id'])
    assert user_p.get('user').get('email') == "test@email.com"
    assert user_p.get('user').get('name_first') == "Mr"
    assert user_p.get('user').get('name_last') == "Creosote"
    assert user_p.get('user').get('handle_str') == "mrcreosote"

    auth.auth_logout(user_session['token'])

    user_session2 = auth.auth_login("test@email.com", "password")
    assert user_session2['u_id'] == user_p.get('user').get('u_id')

def test_login_already_logged_in():
    """ Check that an AccessError is thrown if a logged-in user
    tries to login again. """
    auth.auth_register("test@email.com", "password", "Perry", "The Platypus")

    with pytest.raises(error.AccessError):
        auth.auth_login("test@email.com", "password")

####################################################################
#
#                      Testing auth_logout
#
####################################################################

def test_logout_valid_token():
    """ User attempts to logout with a valid token and logout returns True.
    Then make sure that the token has been invalidated. """
    user_session = auth.auth_register("testEmail@email.com", "password", "Frank", "Reynolds")

    # False return is not useful when the token is actually invalid - it will
    # throw an error in this case. Rather, it is useful for flagging this first
    # assert.
    assert auth.auth_logout(user_session.get('token')).get('is_success') is True
    with pytest.raises(error.AccessError):
        auth.auth_logout(user_session.get('token')).get('is_success')

def test_logout_invalid_token():
    """ Check returns AccessError with completely random false token. """
    with pytest.raises(error.AccessError):
        auth.auth_logout('12345').get('is_success')


####################################################################
#
#                      Testing auth_register
#
####################################################################

def test_register_email_invalid():
    """ Check for InputError when an incorrect email format is entered. """
    with pytest.raises(error.InputError):
        auth.auth_register("invalid_email.com", "password", "Golden", "God")

def test_register_email_taken():
    """ Check for InputError when email given is already in use. """
    auth.auth_register("testemail@email.com", "password", "Sterling", "Archer")

    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "password", "Mallory", "Archer")

def test_register_pass_too_short():
    """ Check for InputError when password given is < 6 chars. """
    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "M", "Mancy", "Nato")

def test_register_name_first_long():
    """ Check for InputError when first name given is > 50 chars. """
    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "password",
                           "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Bob")

def test_register_name_first_short():
    """ Check for InputError when first name given is < 1 char. """
    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "password", "", "Bob")

def test_register_name_last_long():
    """ Check for InputError when the last name given is > 50 chars. """
    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "password", "Bob",
                           "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

def test_register_name_last_short():
    """ Check for InputError when the last name is < 1 char. """
    with pytest.raises(error.InputError):
        auth.auth_register("testemail@email.com", "password", "Bob", "")

def test_register_valid():
    """ Registring with all correct inputs. """
    user_session = auth.auth_register("valid_email@email.com", "pa55w0rd", "Kate", "Young")

    user_p = user_profile(user_session['token'], user_session['u_id'])
    assert user_p.get('user').get('email') == "valid_email@email.com"
    assert user_p.get('user').get('name_first') == "Kate"
    assert user_p.get('user').get('name_last') == "Young"
    assert user_p.get('user').get('handle_str') == "kateyoung"

def test_registeer_handle_short():
    """ Check handle is created properly, char < 20. """
    user_session = auth.auth_register("valid_email@email.com", "pa55w0rd", "John", "Smith")

    user_p = user_profile(user_session['token'], user_session['u_id'])
    assert user_p.get('user').get('handle_str') == "johnsmith"

def test_register_handle_long():
    """ Check handle is shortened to 20 if the name is > 20 chars. """
    user_session = auth.auth_register("valid_email@email.com", "pa55w0rd",
                                      "Bartholomew", "Montgomery")

    user_p = user_profile(user_session['token'], user_session['u_id'])
    assert user_p.get('user').get('handle_str') == "bartholomewmontgomer"

def test_register_handle_taken():
    """ Check if the user handle is already taken, the last character is replaced with '1',
    and the number increments if that is taken. """
    user1 = auth.auth_register("valid_email@email.com", "pa55w0rd", "Kate", "Young")
    user2 = auth.auth_register("valid_email2@email.com", "pa55w0rd", "Kate", "Young")

    user_p1 = user_profile(user1['token'], user1['u_id'])
    user_p2 = user_profile(user2['token'], user2['u_id'])

    assert user_p1.get('user').get('handle_str') == "kateyoung"
    assert user_p2.get('user').get('handle_str') == "kateyoung0"

def test_register_handle_taken_long():
    """ Test if handle_str modified correctly when handle_str is 20 characters long. """
    user1 = auth.auth_register("valid_email@email.com", "pa55w0rd", "a"*10, "a"*10)
    user2 = auth.auth_register("valid_email2@email.com", "pa55w0rd", "a"*10, "a"*10)

    user_p1 = user_profile(user1['token'], user1['u_id'])
    user_p2 = user_profile(user2['token'], user2['u_id'])

    assert user_p1.get('user').get('handle_str') == "a"*20
    assert user_p2.get('user').get('handle_str') == "a"*19 + "0"
