"""
The file contain the route function
"""
import sys

from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError

import user
import channels
import standup
import message
import auth
import channel
import other
import admin
import database
import passwordreset

URL = "http://127.0.0.1:8080"

def get_url():
    """ Returns URL GLOBAL_VAR """
    return URL

def default_handler(err):
    """
    Default_handler
    """
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, default_handler)

database.retrieve_data_from_files()

database.start_db_backup_scheduler()


@APP.route("/echo", methods=['GET'])
def echo():
    """
    Echo function
    """
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/auth/login", methods=['POST'])
def auth_login():
    """
    Function auth_login route
    """
    login_details = request.get_json()

    user_infor = auth.auth_login(login_details['email'], login_details['password'])
    return dumps(user_infor)


@APP.route("/auth/register", methods=['POST'])
def auth_register():
    """
    Function auth_register route
    """
    register_details = request.get_json()

    user_infor = auth.auth_register(
        register_details['email'], register_details['password'],
        register_details['name_first'], register_details['name_last'])

    return dumps(user_infor)


@APP.route("/auth/logout", methods=['POST'])
def auth_logout():
    """
    Function auth_logout route
    """
    user_token = request.get_json()

    is_success = auth.auth_logout(user_token['token'])

    return dumps(is_success)

@APP.route("/channel/invite", methods=['POST'])
def channel_invite():
    """
    Function channel_invite route
    """
    invite_details = request.get_json()

    channel.channel_invite(
        invite_details["token"], int(invite_details["channel_id"]), int(invite_details["u_id"])
        )

    return dumps({})

@APP.route("/channel/details", methods=['GET'])
def channel_details():
    """
    Function channel_details route
    """
    user_channel_id = {"token": request.args.get('token'),
                       "channel_id": int(request.args.get('channel_id'))}
                        # have to convert channel_id into an int as request.args.get gives a string
    details = channel.channel_details(user_channel_id["token"], user_channel_id["channel_id"])

    return dumps(details)

@APP.route("/channel/messages", methods=['GET'])
def channel_messages():
    """
    Function channel message route
    """
    user_channel_id = {"token": request.args.get('token'),
                       "channel_id": int(request.args.get('channel_id')),
                       "start": int(request.args.get('start'))}
    messages = channel.channel_messages(
        user_channel_id["token"], user_channel_id["channel_id"], user_channel_id["start"])

    return dumps(messages)

@APP.route("/channel/leave", methods=['POST'])
def channel_leave():
    """
    Function channel leave route
    """
    user_channel_id = request.get_json()

    channel.channel_leave(user_channel_id["token"], int(user_channel_id["channel_id"]))

    return dumps({})

@APP.route("/channel/join", methods=['POST'])
def channel_join():
    """
    Function channel join route
    """
    user_channel_id = request.get_json()

    channel.channel_join(user_channel_id["token"], int(user_channel_id["channel_id"]))

    return dumps({})

@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner():
    """
    Function channel addowner route
    """
    add_details = request.get_json()

    channel.channel_addowner(
        add_details["token"], int(add_details["channel_id"]), int(add_details["u_id"]))

    return dumps({})

@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner():
    """
    Function channel removeowner route
    """
    remove_details = request.get_json()

    channel.channel_removeowner(
        remove_details["token"], int(remove_details["channel_id"]), int(remove_details["u_id"]))
    return dumps({})

@APP.route("/user/profile", methods=['GET'])
def user_profile():
    """
    Function user profile route
    """
    user_data = {'token': request.args.get(
        'token'), 'u_id': int(request.args.get('u_id'))}

    user_profile_dict = user.user_profile(
        user_data['token'], user_data['u_id'])

    return dumps(user_profile_dict)


@APP.route("/user/profile/setname", methods=['PUT'])
def user_profile_setname():
    """
    Function user profile setname route
    """
    input_data = request.get_json()

    user.user_profile_setname(
        input_data['token'], input_data['name_first'], input_data['name_last'])

    return dumps({})


@APP.route("/user/profile/setemail", methods=['PUT'])
def user_profile_setemail():
    """
    Function user profile setemail route
    """
    input_data = request.get_json()

    user.user_profile_setemail(input_data['token'], input_data['email'])

    return dumps({})


@APP.route("/user/profile/sethandle", methods=['PUT'])
def user_profile_sethandle():
    """
    Function user profile sethandle route
    """
    input_data = request.get_json()

    user.user_profile_sethandle(input_data['token'], input_data['handle_str'])

    return dumps({})

@APP.route("/user/profile/uploadphoto", methods=['POST'])
def user_profile_uploadphoto():
    """
    Route for user_profile_uploadphoto
    """
    info = request.get_json()
    user.user_profile_uploadphoto(info['token'], info['img_url'],
                                  int(info['x_start']), int(info['y_start']),
                                  int(info['x_end']), int(info['y_end']))
    return dumps({})

@APP.route("/static/<filename>", methods=['GET'])
def serve_image(filename):
    """
    Route that serves profile images
    """

    return send_from_directory('static', filename)

@APP.route("/users/all", methods=['GET'])
def users_all():
    """
    Function users all route
    """
    input_data = request.args.get('token')

    users_list = other.users_all(input_data)

    return dumps(users_list)


@APP.route("/search", methods=['GET'])
def search():
    """
    Function search route
    """
    input_data = {'token': request.args.get(
        'token'), 'query_str': request.args.get('query_str')}

    message_list = other.search(input_data['token'], input_data['query_str'])

    return dumps(message_list)


@APP.route("/channels/list", methods=['GET'])
def channels_list():
    """
    Function channels list route
    """
    token = request.args.get('token')
    channels_dict = channels.channels_list(token)
    return dumps(channels_dict)


@APP.route("/channels/listall", methods=['GET'])
def channels_listall():
    """
    Function channels listall route
    """
    token = request.args.get('token')
    channels_dict = channels.channels_listall(token)
    return dumps(channels_dict)


@APP.route("/channels/create", methods=['POST'])
def channels_create():
    """
    Function channels create route
    """
    channel_info = request.get_json()
    channel_id = channels.channels_create(channel_info['token'], channel_info['name'],
                                          channel_info['is_public'])
    return dumps(channel_id)


@APP.route("/standup/start", methods=['POST'])
def standup_start():
    """
    Function standup start  route
    """
    standup_info = request.get_json()
    time_finish = standup.standup_start(standup_info['token'], int(standup_info['channel_id']),
                                        int(standup_info['length']))
    return dumps(time_finish)


@APP.route("/standup/active", methods=['GET'])
def standup_active():
    """
    Function standup active  route
    """
    details = {"token": request.args.get('token'),
               "channel_id": int(request.args.get('channel_id'))}
    standup_info = standup.standup_active(
        details['token'], details['channel_id'])
    return dumps(standup_info)


@APP.route("/standup/send", methods=['POST'])
def standup_send():
    """
    Function standup send  route
    """
    message_info = request.get_json()
    standup.standup_send(message_info['token'], int(message_info['channel_id']),
                         message_info['message'])
    return dumps({})


@APP.route("/message/send", methods=['POST'])
def message_send():
    """
    Function message send  route
    """
    message_info = request.get_json()
    message_id = message.message_send(message_info['token'], int(message_info['channel_id']),
                                      message_info['message'])
    return dumps(message_id)


@APP.route("/message/sendlater", methods=['POST'])
def message_sendlater():
    """
    Function message sendlater  route
    """
    message_info = request.get_json()
    message_id = message.message_sendlater(message_info['token'], int(message_info['channel_id']),
                                           message_info['message'], int(message_info['time_sent']))
    return dumps(message_id)


@APP.route("/message/react", methods=['POST'])
def message_react():
    """
    Function message react route
    """
    message_info = request.get_json()
    message.message_react(
        message_info['token'], int(message_info['message_id']), int(message_info['react_id']))
    return dumps({})

@APP.route("/message/unreact", methods=['POST'])
def message_unreact():
    """
    Function message unreact route
    """
    message_info = request.get_json()
    message.message_unreact(
        message_info['token'], int(message_info['message_id']), int(message_info['react_id']))
    return dumps({})

@APP.route("/message/pin", methods=['POST'])
def message_pin():
    """
    Function message pin route
    """
    message_info = request.get_json()
    message.message_pin(
        message_info['token'], int(message_info['message_id']))
    return dumps({})

@APP.route("/message/unpin", methods=['POST'])
def message_unpin():
    """
    Function message unpin route
    """
    message_info = request.get_json()
    message.message_unpin(
        message_info['token'], int(message_info['message_id']))
    return dumps({})

@APP.route("/message/remove", methods=['DELETE'])
def message_remove():
    """
    Function message remove route
    """
    message_info = request.get_json()
    message.message_remove(
        message_info['token'], int(message_info['message_id']))
    return dumps({})


@APP.route("/message/edit", methods=['PUT'])
def message_edit():
    """
    Function message edit route
    """
    message_info = request.get_json()
    message.message_edit(
        message_info['token'], int(message_info['message_id']), message_info['message'])
    return dumps({})

@APP.route("/admin/userpermission/change", methods=['POST'])
def admin_userperms_change():
    """
    Function admin userperms change route
    """
    input_data = request.get_json()

    admin.change_user_permission(
        input_data['token'], int(input_data['u_id']), int(input_data['permission_id'])
        )

    return dumps({})

@APP.route("/admin/user/remove", methods=['DELETE'])
def admin_user_remove():
    """
    Function admin remove_user route
    """
    input_data = request.get_json()
    admin.remove_user(
        input_data['token'], int(input_data['u_id']))
    return dumps({})

@APP.route("/auth/passwordreset/request", methods=['POST'])
def password_reset_request():
    """
    Function passwordreset_request route
    """
    email = request.get_json()
    passwordreset.passwordreset_request(email['email'])
    return dumps({})

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def password_reset():
    """
    Function passwordreset_reset
    """
    reset_data = request.get_json()
    passwordreset.passwordreset_reset(
        reset_data['reset_code'], reset_data['new_password'])
    return dumps({})

@APP.route("/auth/passwordreset/reset_code", methods=['POST'])
def passwordreset_get_reset_code():
    """
    Helper function to get reset code for testing purposes
    """
    email = request.get_json()
    reset_code = passwordreset.get_reset_code(email['email'])
    return dumps(reset_code)

@APP.route("/workspace/reset", methods=['POST'])
def workspace_reset():
    """
    Reset the database
    """
    database.clear_database()
    return dumps({})



if __name__ == "__main__":
    APP.run(port=(int(sys.argv[1]) if len(sys.argv) == 2 else 8080))
