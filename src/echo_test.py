"""
Test for the example echo route in server.py
"""

import json
import urllib.request
from urllib.error import HTTPError
import pytest

def test_echo_success():
    """
    Situation when echo prints correctly
    """
    response = urllib.request.urlopen('http://127.0.0.1:8080/echo?data=hi')
    payload = json.load(response)
    assert payload['data'] == 'hi'

def test_echo_failure():
    """
    Situation when echo prints incorrectly
    """
    with pytest.raises(HTTPError):
        urllib.request.urlopen('http://127.0.0.1:8080/echo?data=echo')
