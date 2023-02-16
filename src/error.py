"""
Errors used accross the files
"""

from werkzeug.exceptions import HTTPException

class AccessError(HTTPException):
    """
    HTTP error if there is invalid access.
    """
    code = 400
    message = 'No message specified'

class InputError(HTTPException):
    """
    HTTP error if there is invalid input.
    """
    code = 400
    message = 'No message specified'
