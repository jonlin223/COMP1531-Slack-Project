"""
The tesing file for hangman function
"""
import datetime
import string
import pytest
import database
from error import InputError
from channels import channels_create
from auth import auth_register, auth_logout
from message import message_send
from message_test import set_reacts
from other import search
from hangman import hangman_evil_answer, hangman_clear_game_data
BOT_TOKEN = "thisisthetokenforthebot"


@pytest.fixture(autouse=True)
def clear_hangman():
    """
    clear game data when we run test.
    """
    hangman_clear_game_data()


###############################################################
#
#                   hangman_start_testing
#
###############################################################


def test_hangmne_normal():
    """
    Test if hangman can start with correct input
    """
    user_infor = auth_register(
        "337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    message_id = message_send(
        user_infor['token'], channel_infor['channel_id'], "/hangman")
    assert search(BOT_TOKEN, "A game of hangman has been started in this channel") == {
        "messages": [{
            'message_id': message_id["message_id"] + 1,
            'u_id': -1,
            'message': "A game of hangman has been started in this channel",
            'time_created': time_create,
            'reacts': [set_reacts()],
            'is_pinned': False
        }]
    }

    auth_logout(BOT_TOKEN)
    message_id = message_send(
        user_infor['token'], channel_infor['channel_id'], "/guess e")

    assert database.get_current_user(BOT_TOKEN) == -1


def test_hangmne_two_game():
    """
    If current channel has ongoing hangman game, user cannot start a new game
    """
    user_infor = auth_register(
        "337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    message_send(user_infor['token'], channel_infor['channel_id'], "/hangman")
    with pytest.raises(InputError):
        message_send(user_infor['token'],
                     channel_infor['channel_id'], "/hangman")

###############################################################
#
#                   hangman_guess_testing
#
###############################################################

# add a additional function to return the answer of the hangman

def test_hangman_no_game():
    """
    Test whether the user can send message "/guess X"
    X is any letter in chat when there is no hangman game
    """
    user_infor = auth_register(
        "337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    message_id = message_send(user_infor['token'], channel_infor['channel_id'], "/guess a")
    time_create_date = datetime.datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
    assert search(user_infor['token'], "/guess a") == {"messages": [{
        'message_id': message_id["message_id"],
        'u_id': user_infor["u_id"],
        'message': "/guess a",
        'time_created': time_create,
        'reacts': [set_reacts()],
        'is_pinned': False
    }]}

def test_hangmne_guess_noraml():
    """
    Test if guess can start with correct input and success
    """
    user_infor = auth_register(
        "337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    message_send(user_infor['token'], channel_infor['channel_id'], "/hangman")
    current_game = hangman_evil_answer(channel_infor['channel_id'])
    #print(f"Answer is {answer}")
    has_guessed = []
    game_answer = current_game['word']
    for letter in game_answer:
        if current_game is not None and letter not in current_game['guesses']:
            has_guessed.append(letter)
            time_create_date = datetime.datetime.now().replace(microsecond=0)
            time_create = time_create_date.timestamp()
            message_id = message_send(
                user_infor['token'], channel_infor['channel_id'], f"/guess {letter}")
            current_game = hangman_evil_answer(channel_infor['channel_id'])
            if current_game is not None:
                state = ''
                for char in current_game['word']:
                    if char in current_game['guesses']:
                        state += char
                    else:
                        state += '_'
                state += '\n'
                bot_msg = state + \
                    f"You have {9 - current_game['num_guesses']} incorrect guesses left\n" + \
                    "Guessed Characters: " + str(has_guessed)
                assert search(BOT_TOKEN, bot_msg) == {
                    "messages": [{
                        'message_id': message_id["message_id"] + 1,
                        'u_id': -1,
                        'message': bot_msg,
                        'time_created': time_create,
                        'reacts': [set_reacts()],
                        'is_pinned': False
                    }]}
    bot_win = f'Congratultions! You correctly guessed that the word was {game_answer}'
    assert search(BOT_TOKEN, bot_win) == {
        "messages": [{
            'message_id': message_id["message_id"] + 1,
            'u_id': -1,
            'message': bot_win,
            'time_created': time_create,
            'reacts': [set_reacts()],
            'is_pinned': False
        }]
    }


def test_hangmne_guess_fail():
    # if __name__ == "__main__":
    """
    Test if guess can start with incorrect input and fail
    """
    user_infor = auth_register(
        "337992611@gamil.com", "ccc337992611", "Min", "Li")
    channel_infor = channels_create(user_infor['token'], 'test_one', True)
    message_send(user_infor['token'], channel_infor['channel_id'], "/hangman")
    current_game = hangman_evil_answer(channel_infor['channel_id'])
    #print(f"Answer is {answer}")
    has_guessed = []
    game_answer = current_game['word']
    for letter in string.ascii_lowercase:
        if current_game is not None and letter not in game_answer:
            has_guessed.append(letter)
            message_id = message_send(
                user_infor['token'], channel_infor['channel_id'], f"/guess {letter}")
            time_create_date = datetime.datetime.now().replace(microsecond=0)
            time_create = time_create_date.timestamp()
            current_game = hangman_evil_answer(channel_infor['channel_id'])
            if current_game is not None:
                state = ''
                for char in current_game['word']:
                    if char in current_game['guesses']:
                        state += char
                    else:
                        state += '_'
                state += '\n'
                bot_msg = state + \
                    f"You have {9 - current_game['num_guesses']} incorrect guesses left\n" + \
                    "Guessed Characters: " + str(has_guessed)
                assert search(BOT_TOKEN, bot_msg) == {
                    "messages": [{
                        'message_id': message_id["message_id"] + 1,
                        'u_id': -1,
                        'message': bot_msg,
                        'time_created': time_create,
                        'reacts': [set_reacts()],
                        'is_pinned': False
                    }]}
    bot_loss = f"Game Lost! The correct word was {game_answer}"
    assert search(BOT_TOKEN, bot_loss) == {
        "messages": [{
            'message_id': message_id["message_id"] + 1,
            'u_id': -1,
            'message': bot_loss,
            'time_created': time_create,
            'reacts': [set_reacts()],
            'is_pinned': False
        }]
    }
