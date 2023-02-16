""" Tests for passwordreset functions.
Note that it is impossible to test that email containing code has been sent.
Therefore, testing will directly access the database. """

import pytest
import passwordreset
from error import InputError
import auth

def test_request_invalid_email():
    """ Test that nothing happens when invalid email given. """

    passwordreset.passwordreset_request("email@email.com")
    assert passwordreset.RESETS == []

def test_reset_invalid_code():
    """ Test that InputError raised if invalid code given. """

    with pytest.raises(InputError):
        passwordreset.passwordreset_reset("hello", "password")

def test_reset_invalid_password():
    """ Test that InputError raised if password is too short. """

    auth.auth_register("email@email.com", "password", "General", "Kenobi")
    passwordreset.passwordreset_request("email@email.com")

    reset_code = passwordreset.RESETS[0]['reset_code']

    with pytest.raises(InputError):
        passwordreset.passwordreset_reset(reset_code, "bad")

def test_request_reset():
    """ Test that process of requesting and reseting works. """

    user = auth.auth_register("email@email.com", "password", "Kool-Aid", "Man")
    u_id = user['u_id']
    auth.auth_logout(user['token'])
    passwordreset.passwordreset_request("email@email.com")

    reset_code = passwordreset.RESETS[0]['reset_code']
    passwordreset.passwordreset_reset(reset_code, "betterpassword")

    with pytest.raises(InputError):
        auth.auth_login("email@email.com", "password")

    user1 = auth.auth_login("email@email.com", "betterpassword")
    assert u_id == user1['u_id']
