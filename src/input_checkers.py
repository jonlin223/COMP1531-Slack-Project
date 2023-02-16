"""
File to handle all the decorators to be used to error check.
"""

from functools import wraps
from inspect import getfullargspec, signature

from email_helper import email_check
import database
import error

def validate_token(func):
    """
    Runs a check if the token of an input is valid.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            token_arg_index = argspec.args.index("token")
            # Check the token is valid.
            if database.get_current_user(args[token_arg_index]) is None:
                # Token is invalid
                raise error.AccessError(description="Current token is not valid.")
            else:
                return func(*args, **kwargs)
        except ValueError:
            print("\033[93m" + "WARNING: Token arg not found - running function "
                  + f"{func.__name__} without token check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func

def validate_u_id(func):
    """
    Runs a check if the user_id input is valid.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            uid_arg_index = argspec.args.index("u_id")
            target_user = database.get_user_data(args[uid_arg_index])
            # Check the u_id is valid.
            if target_user is None:
                # u_id is invalid
                raise error.InputError(description="u_id does not refer to a valid user")
            else:
                return func(*args, **kwargs)
        except ValueError:
            print("\033[93m" + "WARNING: u_id arg not found - running function "
                  + f"{func.__name__} without u_id check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func

def validate_c_id(func):
    """
    Runs a check if the channel_id input is valid.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            cidarg_index = argspec.args.index("channel_id")
            target_channel = database.get_channel_data(args[cidarg_index])
            # Check the u_id is valid.
            if target_channel is None:
                # u_id is invalid
                raise error.InputError(description="Channel ID is not a valid channel")
            else:
                return func(*args, **kwargs)
        except ValueError:
            print("\033[93m" + "WARNING: c_id arg not found - running function "
                  + f"{func.__name__} without c_id check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func

def validate_msg_id(func):
    """
    Runs a check if the message_id exists anywhere in the database.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            msg_arg_index = argspec.args.index("message_id")
            target_message = database.get_message(args[msg_arg_index])
            # Check the u_id is valid.
            if target_message is None:
                # u_id is invalid
                raise error.InputError(description="Message based on ID does not exist")
            else:
                return func(*args, **kwargs)
        except ValueError:
            print("\033[93m" + "WARNING: msg_id arg not found - running function "
                  + f"{func.__name__} without msg_id check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func

def validate_email_format(func):
    """
    Runs a check if the email parameter is not a valid email format.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            email_arg_index = argspec.args.index("email")
            email = args[email_arg_index]
            # Check the email is valid
            if email_check(email) is False:
                raise error.InputError(description="The email you entered is not valid")
            else:
                return func(*args, **kwargs)
        except ValueError:
            print("\033[93m" + "WARNING: email arg not found - running function "
                  + f"{func.__name__} without email check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func

def validate_login_perms(func):
    """
    Runs a check if the email being logged in with has been previously
    removed from the slackr.
    """
    argspec = getfullargspec(func)
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        """ Wrapper function """
        try:
            email_arg_index = argspec.args.index("email")
            email = args[email_arg_index]

            # Try to grab this users ID. If the user doesnt exist, create a warning
            # and run the function without checking the permission_id.
            try:
                target_u_id = next(u['u_id'] for u in database.get_users() if u['email'] == email)
                target_perm_id = database.get_permission_dict(target_u_id).get('permission_id')
                if target_perm_id == 66:
                    raise error.AccessError(description="The account registered to this email has" +
                                            " been removed from the slakr. " +
                                            "[I'm sorry Dave, I'm afraid I can't do that]")
                else:
                    return func(*args, **kwargs)
            except StopIteration:
                print("\033[93m" + "WARNING: This email was not found  - running function "
                      + f"{func.__name__} without permission_id check." + "\033[0m")
                return func(*args, **kwargs)

        except ValueError:
            print("\033[93m" + "WARNING: email arg not found - running function "
                  + f"{func.__name__} without email check." + "\033[0m")
            return func(*args, **kwargs)
    wrapper_func.__signature__ = signature(func)
    return wrapper_func
