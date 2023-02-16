""" Functions for hangman. """

import random
import error
import hangmanbot
import message_parser

# Global list of hangman games
# list contains dictionaries of format
# {channel_id, word, state, num_guesses, guesses}
# state is string, remove characters when guessed correctly
# max number of guesses is 10
# guesses is list containing guessed characters
# List not in database.py as we have decided to not make hangman games persistent
HANGMANS = []

def find_game(channel_id):
    """ Helper function used to return game of hangman,
    returns None if game not found. """

    for game in HANGMANS:
        if game['channel_id'] == channel_id:
            return game
    return None

def hangman_start(channel_id):
    """ Given channel_id, start a game of hangman. """

    # If hangman game already active in this channel, raise InputError.
    for game in HANGMANS:
        if game['channel_id'] == channel_id:
            raise error.InputError(description="""There is already a game of hangman active
                                                  in this channel""")

    # Bot is called
    bot_id = hangmanbot.call_bot(channel_id)

    # Bot sends a message notifying channel that hangman game has started
    msg = "A game of hangman has been started in this channel"
    message_parser.parse_message(bot_id['bot_id'], channel_id, msg)

    # Generate a word that should be used
    words = []
    with open("/usr/share/dict/words") as wordfile:
        words = wordfile.readlines()
    word = random.choice(words).strip()

    # Add the hangman game to the list HANGMANS
    new_game = {"channel_id": channel_id,
                "word": word,
                "state": word,
                "num_guesses": 0,
                "guesses": []}
    HANGMANS.append(new_game)

def hangman_guess(character, channel_id):
    """ Guess the hangman word given a character. """

    # Find the game in HANGMANS, if game does not exist in channel
    # then nothing happens
    game = find_game(channel_id)
    if game is None:
        return

    # Check if character exists in state
    # Change game state appropriately
    if character in game['state']:
        game['guesses'].append(character)
        game['state'] = game['state'].replace(character, '')
    else:
        game['num_guesses'] += 1
        if character not in game['guesses']:
            game['guesses'].append(character)

    hangman_print_state(game)

def hangman_end(game):
    """ End the game of hangman in the given channel. """

    HANGMANS.remove(game)

def hangman_print_state(game):
    """ Print the state of the given hangman game.
    Bot is called in this function. """

    bot_id = hangmanbot.call_bot(game['channel_id'])

    # If game won
    if game['state'] == '':
        msg = f"Congratultions! You correctly guessed that the word was {game['word']}"
        message_parser.parse_message(bot_id['bot_id'], game['channel_id'], msg)
        hangman_end(game)

    # If game lost
    elif game['num_guesses'] == 10:
        msg = f"Game Lost! The correct word was {game['word']}"
        message_parser.parse_message(bot_id['bot_id'], game['channel_id'], msg)
        hangman_end(game)

    # If game is to continue
    # Print the appropriate details of the game
    else:
        state = ''
        for char in game['word']:
            if char in game['guesses']:
                state += char
            else:
                state += '_'
        state += '\n'

        num_guesses = f"You have {9 - game['num_guesses']} incorrect guesses left\n"
        guesses = "Guessed Characters: " + str(game['guesses'])

        msg = state + num_guesses + guesses
        message_parser.parse_message(bot_id['bot_id'], game['channel_id'], msg)

###############################################################
#
#                   hangman_for_testing_purpose
#
###############################################################

def hangman_evil_answer(channel_id):
    """
    For testing purpose to return the game answer of given channel.
    """
    for game in HANGMANS:
        if game['channel_id'] == channel_id:
            return game
    return None

def hangman_clear_game_data():
    """
    Clear the game data for testing purpose
    """
    HANGMANS.clear()
