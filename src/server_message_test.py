"""
Testing file for message route
"""
import json
import urllib.request
import threading
from datetime import datetime, timedelta


from server import get_url

from server_test_helpers import server_create_user, server_create_channel


def test_send_messsage():
    """
    Tesing the send message by route
    """
    user_infor = server_create_user(
        "337992611@qq.com", "password", "li", "minxin")
    channel_infor = server_create_channel(
        user_infor['token'], 'test_channel', True)
    token = user_infor['token']
    channel_id = channel_infor['channel_id']

    message = "Testing Testing"
    data_add = json.dumps({
        'token': token,
        'channel_id': channel_id,
        'message': message
    }).encode("utf-8")

    req = urllib.request.Request(f'{get_url()}/message/send', data=data_add, headers={
        "Content-Type": "application/json"}, method='POST')
    response = urllib.request.urlopen(req)
    time_create_date = datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    payload = json.loads(response.read().decode('utf8'))

    response_details = urllib.request.urlopen(f"{get_url()}/channel/messages?token={token}"
                                              + f"&channel_id={channel_id}&start={0}")
    details_decoded = json.load(response_details)

    assert details_decoded['messages'] == [{'message_id': payload['message_id'],
                                            'u_id': user_infor['u_id'],
                                            'message': message,
                                            'time_created': time_create,
                                            'reacts': [{'react_id': 1,
                                                        'u_ids': [],
                                                        'is_this_user_reacted': False}],
                                            'is_pinned': False}]


def test_message_sendlater():
    """ Http testing for message/sendlater. """
    def helper_func(token):
        """ Check that there are no messages in channel """
        url = (f"{get_url()}/channel/messages?token={token}"
               f"&channel_id={channel['channel_id']}&start=0")
        response = urllib.request.urlopen(url)
        payload = json.load(response)

        assert payload['messages'] == []

    user = server_create_user("email@email.com", "password", "Prince", "Ali")
    channel = server_create_channel(user['token'], "test_channel", True)

    # Run test check empty a second after message_sendlater has been
    # called (but hasn't finished executing)
    new_thread = threading.Timer(1.5, helper_func, args=(user['token']))
    new_thread.start()

    # Send a message later
    time_sent = datetime.now() + timedelta(seconds=2)
    time_sent = int(time_sent.timestamp())
    data = json.dumps({'token': user['token'],
                       'channel_id': channel['channel_id'],
                       'message': "omegalul",
                       'time_sent': time_sent}).encode('utf-8')
    req = urllib.request.Request(f"{get_url()}/message/sendlater",
                                 data=data,
                                 headers={'Content-Type': 'application/json'},
                                 method='POST')
    response = urllib.request.urlopen(req)
    json.load(response)

    url = (f"{get_url()}/channel/messages?token={user['token']}"
           f"&channel_id={channel['channel_id']}&start=0")
    response = urllib.request.urlopen(url)
    payload = json.load(response)

    assert len(payload['messages']) == 1
    assert payload['messages'][0]['message'] == "omegalul"
    assert payload['messages'][0]['time_created'] == time_sent


def test_message_pin():
    """
    Testing message pin route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"
    message_payload = json.dumps(
        {'token': user_data['token'],
         'channel_id': channel_data['channel_id'],
         'message': message_str}).encode('utf-8')
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)

    pin_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id']}).encode('utf-8')
    pin_msg_req = urllib.request.Request(f"{get_url()}/message/pin",
                                         data=pin_payload,
                                         headers={
                                             "Content-Type": "application/json"},
                                         method='POST')
    urllib.request.urlopen(pin_msg_req)

    response_details = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded = json.load(response_details)

    assert details_decoded['messages'][0].get('is_pinned') is True


def test_message_unpin():
    """
    Testing message unpin route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"

    message_payload = json.dumps({'token': user_data['token'],
                                  'channel_id': channel_data['channel_id'],
                                  'message': message_str}).encode('utf-8')
    #send a message by route
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)
    #pin the message above
    pin_payload = json.dumps({'token': user_data['token'],
                              'message_id': decoded_send_response['message_id']}).encode('utf-8')
    pin_msg_req = urllib.request.Request(f"{get_url()}/message/pin",
                                         data=pin_payload,
                                         headers={
                                             "Content-Type": "application/json"},
                                         method='POST')
    urllib.request.urlopen(pin_msg_req)

    response_details = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded = json.load(response_details)

    assert details_decoded['messages'][0].get('is_pinned') is True

    unpin_msg_req = urllib.request.Request(f"{get_url()}/message/unpin",
                                           data=pin_payload,
                                           headers={
                                               "Content-Type": "application/json"},
                                           method='POST')
    urllib.request.urlopen(unpin_msg_req)

    response_details = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded = json.load(response_details)

    assert details_decoded['messages'][0].get('is_pinned') is False


def test_message_react():
    """
    Testing message react route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"

    message_payload = json.dumps(
        {'token': user_data['token'],
         'channel_id': channel_data['channel_id'],
         'message': message_str}).encode('utf-8')
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)

    react_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id'],
         'react_id': 1}).encode('utf-8')
    react_msg_req = urllib.request.Request(f"{get_url()}/message/react",
                                           data=react_payload,
                                           headers={
                                               "Content-Type": "application/json"},
                                           method='POST')
    urllib.request.urlopen(react_msg_req)

    response_details = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded = json.load(response_details)

    assert details_decoded['messages'][0].get(
        'reacts')[0]['u_ids'][0] == user_data['u_id']


def test_message_unreact():
    """
    Testing message unreact route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"

    message_payload = json.dumps(
        {'token': user_data['token'],
         'channel_id': channel_data['channel_id'],
         'message': message_str}).encode('utf-8')
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)

    react_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id'],
         'react_id': 1}).encode('utf-8')
    react_msg_req = urllib.request.Request(f"{get_url()}/message/react",
                                           data=react_payload,
                                           headers={
                                               "Content-Type": "application/json"},
                                           method='POST')
    urllib.request.urlopen(react_msg_req)

    response_details1 = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded1 = json.load(response_details1)

    assert details_decoded1['messages'][0].get(
        'reacts')[0]['u_ids'][0] == user_data['u_id']

    unreact_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id'],
         'react_id': 1}).encode('utf-8')
    unreact_msg_req = urllib.request.Request(f"{get_url()}/message/unreact",
                                             data=unreact_payload,
                                             headers={
                                                 "Content-Type": "application/json"},
                                             method='POST')
    urllib.request.urlopen(unreact_msg_req)

    response_details2 = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded2 = json.load(response_details2)

    assert details_decoded2['messages'][0].get('reacts')[0]['u_ids'] == []


def test_message_remove():
    """
    Tesing message remove route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"
    message_payload = json.dumps(
        {'token': user_data['token'],
         'channel_id': channel_data['channel_id'],
         'message': message_str}).encode('utf-8')
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)

    remove_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id']}).encode('utf-8')
    remove_msg_req = urllib.request.Request(f"{get_url()}/message/remove",
                                            data=remove_payload,
                                            headers={
                                                "Content-Type": "application/json"},
                                            method='DELETE')
    urllib.request.urlopen(remove_msg_req)

    response_details2 = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded2 = json.load(response_details2)

    assert details_decoded2['messages'] == []

def test_message_edit():
    """
    Testing message edit route
    """
    user_data = server_create_user(
        "email@email.com", "password", "Billy", "Batson")
    channel_data = server_create_channel(
        user_data['token'], 'test_channel', True)
    message_str = "This is a test message!"

    message_payload = json.dumps(
        {'token': user_data['token'],
         'channel_id': channel_data['channel_id'],
         'message': message_str}).encode('utf-8')
    send_msg_req = urllib.request.Request(f"{get_url()}/message/send",
                                          data=message_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='POST')
    response = urllib.request.urlopen(send_msg_req)
    decoded_send_response = json.load(response)

    edit_payload = json.dumps(
        {'token': user_data['token'],
         'message_id': decoded_send_response['message_id'],
         'message': "Test edit"}).encode('utf-8')
    edit_msg_req = urllib.request.Request(f"{get_url()}/message/edit",
                                          data=edit_payload,
                                          headers={
                                              "Content-Type": "application/json"},
                                          method='PUT')
    urllib.request.urlopen(edit_msg_req)

    response_details2 = urllib.request.urlopen(
        f"{get_url()}/channel/messages?token={user_data['token']}"
        + f"&channel_id={channel_data['channel_id']}&start={0}")
    details_decoded2 = json.load(response_details2)

    assert details_decoded2['messages'][0].get('message') == "Test edit"
