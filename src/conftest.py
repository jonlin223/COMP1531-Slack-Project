"""
File for handling pytest session fixtures
"""
import urllib.request
import pytest
import database

URL = "http://127.0.0.1:8080"


# Rquest parameter parses in the context the fixture
# is run in.
@pytest.fixture(autouse=True, scope="function")
def clean_database(request):
    """ Clears database between each test """
    # Clears the local instance of the database.
    database.clear_database()

    # Clears the flask instance of the database if this
    # is a server test.
    module_prefix = str(request.module.__name__).split('_')
    if module_prefix[0] == "server":
        clear_request = urllib.request.Request(f"{URL}/workspace/reset", method="POST")
        urllib.request.urlopen(clear_request)
