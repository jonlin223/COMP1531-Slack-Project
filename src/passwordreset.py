""" Functions for passwordreset routes to call. """

import hashlib
import random
import string
import smtplib
from error import InputError
import database

# Global list which holds reset details
# contains dictionaries of form
# {email, reset_code}
RESETS = []

def get_reset_details(reset_code):
    """ Given a reset_code, returns reset_details if they exist. """

    for info in RESETS:
        if info['reset_code'] == reset_code:
            return info
    return None

def get_reset_code(email):
    """ Given a reset_code, returns reset_details if they exist. """

    for info in RESETS:
        if info['email'] == email:
            return info['reset_code']
    return None

def passwordreset_request(email):
    """ Given an email string, if user is a registered user,
    send them an email containing code which can be used to reset the email. """

    # If email given does not belong to a registered user, does nothing
    if database.get_password_data(email) is None:
        return {}

    # Generate a reset_code
    # reset_code will be a random 6 character string consisting of both
    # upper and lower case letters and numbers
    characters = string.digits + string.ascii_letters
    reset_code = ''.join(random.choice(characters) for i in range(6))

    # Add reset_details to RESET
    reset_details = {'email': email, 'reset_code': reset_code}
    RESETS.append(reset_details)
    # Set up email details
    msg = f"\nYour reset code is: {reset_code}"

    # Send the email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.connect("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("email@email.com", "password")
    server.sendmail("email@email.com", email, msg)
    server.quit()

    return {}

def passwordreset_reset(reset_code, new_password):
    """ Given a string reset_code and a string new_password,
    if these two parameters are valid, change the user's password. """

    # Check if reset_code is valid, raise InputError if not
    reset_details = get_reset_details(reset_code)
    if reset_details is None:
        raise InputError(description="The reset_code you entered is invalid.")

    # Check if password is valid, raise InputError if not
    if len(new_password) < 6:
        raise InputError(description="The password you entered is less than 6 characters long.")

    # Hash new_password
    passcode = hashlib.sha256(new_password.encode()).hexdigest()

    # Get password data from the database and change the password associated with the email
    database.get_password_data(reset_details['email'])
    database.set_password(reset_details['email'], passcode)

    # remove reset_details from RESETS
    RESETS.remove(reset_details)

    return {}
