""" File contains functions for auth. """

import hashlib
import jwt
import error
import database
import input_checkers

DEFAULT_USER_IMG = "http://127.0.0.1:8080/static/bean.jpg"

def create_handle_str(handle_str):
    """ Given a handle_str, look through database to see if it is already taken.
    Modify appropriately if taken. """

    number = 0
    handle_str_cpy = handle_str
    for user in database.get_users():
        if handle_str_cpy == user['handle_str']:
            if len(handle_str) < 20:
                handle_str_cpy = handle_str + str(number)
            else:
                handle_str = handle_str[:19]
                handle_str_cpy = handle_str + str(number)
            number += 1

    return handle_str_cpy

@input_checkers.validate_email_format
@input_checkers.validate_login_perms
def auth_login(email, password):
    """ Login user with given email and password. """

    # Check if email entered belongs to a user
    password_data = database.get_password_data(email)
    if password_data is None:
        raise error.InputError(description="The email you entered is incorrect")

    # Hash the password and see if it matches the hashed passowrd in the database
    passcode = hashlib.sha256(password.encode()).hexdigest()

    # Check if password matches email
    if password_data['password'] != passcode:
        raise error.InputError(description="The password you entered is incorrect")

    # find user's u_id from email given
    u_id = 0
    for user in database.get_users():
        if user['email'] == email:
            u_id = user['u_id']

    # Check if already logged in.
    if database.get_token_from_user(u_id) is not None:
        raise error.AccessError(description="Cannot login when already logged in!")

    # Generate a token
    payload = {'u_id': u_id}
    token = str(jwt.encode(payload, 'jwt_secret', algorithm='HS256'))

    dictionary = {'u_id': u_id, 'token': token}
    database.set_current_user(u_id, token)
    return dictionary

@input_checkers.validate_token
def auth_logout(token):
    """ Given a token, removes user who owns this token from CURRENT_USERS.
    Used to logout individuals.
    Returns True is user could be logged out, False otherwise.
    Implemented in database.py for direct access to database. """

    return {'is_success': database.remove_current_user(token)}

@input_checkers.validate_email_format
def auth_register(email, password, name_first, name_last):
    """ Register a user into the database given details in parameters. """

    # Check if email is already being used by another user
    for user in database.get_users():
        if user['email'] == email:
            raise error.InputError(description="The email you entered is already being used")

    # Check if password is less than 6 characters long
    if len(password) < 6:
        raise error.InputError(description="""The password you entered is less than 6 characters
                                           long""")

    # Check if name_first is between 1 and 50 characters inclusive in length
    if len(name_first) < 1 or len(name_first) > 50:
        raise error.InputError(description="""The first name you entered is not between 1 and 50
                                           characters in length inclusive""")

    # Check if name_last is between 1 and 50 characters inclusive in length
    if len(name_last) < 1 or len(name_last) > 50:
        raise error.InputError(description="""The last name you entered is not between 1 and 50
                                           characters in length inclusive""")

    # First we need to create a handle_str
    handle_str = name_first.lower() + name_last.lower()

    # If len(handle_str) > 20 then we need to cut the handle_str to an appropriate length
    if len(handle_str) > 20:
        handle_str = handle_str[:20]

    # Check if handle_str is already taken and modify appropriately
    handle_str = create_handle_str(handle_str)

    # Now we need to assign a u_id
    # u_id generated in order of registration
    # Add 1 to u_id of most recent user
    u_id = database.generate_u_id()

    # Now we add user to the list of dictionaries
    user = {'u_id': u_id,
            'email': email,
            'name_first': name_first,
            'name_last': name_last,
            'handle_str': handle_str,
            'profile_img_url': DEFAULT_USER_IMG}

    # Now check if this is the first person to join the slackr
    if database.get_users() == []:
        database.set_permissions(u_id, 1)
    else:
        database.set_permissions(u_id, 2)

    database.set_user_data(user)

    # Encode the password
    passcode = hashlib.sha256(password.encode()).hexdigest()

    # Associate email to password in PASSWORD_DATA
    database.set_password(email, passcode)

    # We now login the user using auth_login
    return auth_login(email, password)
