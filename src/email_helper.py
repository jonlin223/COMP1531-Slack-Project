""" contains helper function to check if email is valid. """

# pylint: disable = anomalous-backslash-in-string

import re

def email_check(email):
    """ ################ Helper Functions ###############
    function to check validity of email. Obtained from GeeksForGeeks
    https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
    as referenced from the project outline. """

    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'

    if re.search(regex, email):
        return True

    return False
