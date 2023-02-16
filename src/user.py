"""
implementation of user data
"""

import urllib.request
import os
from PIL import Image
from flask import url_for
import error
import database
import input_checkers

@input_checkers.validate_token
@input_checkers.validate_u_id
def user_profile(token, u_id):
    """
    Given a token and u_id return a dictionary containing the user's data
    """
    # pylint: disable=unused-argument
    # NB: Supressed this warning because token is in fact used in
    # the decorator, however pylint doesn't check for this.
    user = database.get_user_data(u_id)
    return {"user": user}

@input_checkers.validate_token
def user_profile_setname(token, name_first, name_last):
    """
    Given input for first and last name sets user's firtname and lastname if within character limit
    """
    if (len(name_first) > 50 or name_first == ""):
        raise error.InputError(description="First name is not within 1-50 characters")

    if (len(name_last) > 50 or name_last == ""):
        raise error.InputError(description="Last name is not within 1-50 characters")

    u_id = database.get_current_user(token)
    user = database.get_user_data(u_id)
    user['name_first'] = name_first
    user['name_last'] = name_last
    database.set_user_data(user)

@input_checkers.validate_token
@input_checkers.validate_email_format
def user_profile_setemail(token, email):
    """
    Given input for email sets user's email if valid and not taken
    """
    users = database.get_users()
    for user in users:
        if user['email'] is email:
            raise error.InputError(description="This email is already taken")
    u_id = database.get_current_user(token)
    user = database.get_user_data(u_id)
    user['email'] = email
    database.set_user_data(user)

@input_checkers.validate_token
def user_profile_sethandle(token, handle_str):
    """
    given input for a handle name set user's handle
    """
    if (len(handle_str) > 20 or len(handle_str) < 2):
        raise error.InputError(description="Handle is not within 2-20 characters")
    users = database.get_users()
    for user in users:
        if user['handle_str'] is handle_str:
            raise error.InputError(description="Handle is already taken")
    u_id = database.get_current_user(token)
    user = database.get_user_data(u_id)
    user['handle_str'] = handle_str
    database.set_user_data(user)

@input_checkers.validate_token
def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """
    given url of image on the internet, crops it within bounds.
    """
    # pylint: disable=too-many-arguments
    # This pylint warning is supressed because the function requires 6 arguments

    # Get the image from img_url and check if HTTP status of 200 returned
    try:
        req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
    except:
        raise error.InputError(description="The image could not be opened from the given url")

    # Open the image, check if x and y are within dimensions of the image
    img = Image.open(response)
    width, height = img.size
    if x_start < 0 or y_start < 0 or x_end > width or y_end > height:
        raise error.InputError(description="Bounds given exceed the dimensions of the image")

    # Check if image type if a JPG
    if img.format != "JPEG":
        raise error.InputError(description="Image given is not of JPG type")

    # Crop the image to the correct dimensions
    img = img.crop((x_start, y_start, x_end, y_end))

    # Get u_id from token
    u_id = database.get_current_user(token)
    img_path = os.path.join(os.path.dirname(__file__), f"static/{u_id}.jpg")

    # Save the image in the static directory
    # image saved as {u_id}.jpg
    img.save(img_path)

    # serve image from file

    profile_img_url = url_for('static', filename=f"{u_id}.jpg", _external=True)

    # Add profile_img_url to database
    user = database.get_user_data(u_id)
    user['profile_img_url'] = profile_img_url
    database.set_user_data(user)

    return {}
