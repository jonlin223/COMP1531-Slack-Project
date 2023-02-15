# Assumptions

## Iteration 1

### General

* We assume that the tests run offline to the database where official user login info is stored.
* we assume that the 'admin' referred to in tests is the owner of the slackr- the first person registered

### channels_test.py

* We assume that the any function called in the test function apart from the one we are testing 
* Assume that for all functions there will be no empty parameter inputs
* Assume that creating a channel makes you the owner of it
* Assume that creating a public channel only adds the creator of the channel to it, other Slackr members must manually join
* Assume that the "name" parameter for channels_create will never be an empty string
* Assume that in channels_list and channels_listall, channels are listed in the order that they were created
* Assume that channels_listall shows even channels that user is not a member of

### channel_test.py

* We always assume that the parameters given to the fuctions are valid
* Assume that for all functions there will be no empty parameter input
* Assume that creating a channel makes you the owner of it
* Assume that when channel_messages prints from start to start + 50 it returns 50 messages including start and does not return [start+50]
* Assume that creating a public channel only adds the creator of the channel to it, other Slackr members must manually join
* Assume that channel_details stores members/owners of a channel in the order that they were added
* Assume that trying to use channel_addowner to make a non channel member an owner does nothing
* Assume that trying to use channel_removeowener to remove a non channel member as an owner gives an InputError (since not owner condition satisfied)
* INTERPRETATION OF ACCESS ERROR OF CHANNEL_ADDOWNER AND CHANNEL_REMOVEOWNER
    ** you need to be a slackr owner or channel owner to perfrom these functions
    ** only if you are not a slackr owner or channel owner does the error come up

### auth_test.py

* We assume that this test is run offline and so no one has registered with the email being checked.
* Assume that requirement that names be between 1-50 is inclusive.
* Assume that InputError is raised if a user that is already logged in tries to login with the same credentials.
* If we try to login while we still have a valid login token, we will receive an AccessError
* If handle_str is already taken, take the last character and convert it into a number, starting with 1 and incrementing.
* If we try to logout with an invalid token, raise AccessError.

### user_test.py

* Assume that the token parameter provided to the functions are valid.
* Assume that invalid users will have a non-matching u_id and token.
* Assume that user_profile will not return a dictionary of the user's profile if it is an invalid user.
* Assume that requirement for names to be between 1-50 is inclusive of 1 and 50.
* Assume that requirement for "handle" to be be between 3-20 is inclusive of 3 and 20.
* Assume that special characters and numbers will be accepted for names and handles for now.
* Assume invalid users are unregistered users.
* Assume that 'THISISNOTATOKEN' is not a valid token.

### message_test.py

* We assume that when when the message_edit is used and the new message should less than 1000 char otherwise it should have a InputError.
* Assume that message_send and message_edit wwill not accepted empty string search. It will raises InputError

### other_test.py

* We assume that the search function will  return message that contain query string.
* For example, query = 'AAs' the message 'AAs' will be returned and message 'AAs s' will also be returned.
* Assume that the search function will return empty dictionary. eg 
* Assume that search wwill not accepted empty string search. It will raises InputError

## Iteration 2

### Database.py

* Raise InputError if someone tries to setChannelData without first creating a channel with that ID.

### Admin.py

* Raise AccessError if an owner tries to change their permissions and they are the only owner.

### Channel.py

* Channel_invite will raise InputError if you invite a user who is already a member of the channel.
* Channel_message does not raise an error that start is past oldest message if the channel is empty. Instead, it just returns an empty list, with end = -1.

### Other.py

* Assume search feature is case sensitive and as such if searching for "HI", "hi" will not be included in search results.

## Iteration 3

### Channel.py

* Channel_removeowner will not remove channel ownership from the owner of the slackr

### hangman.py

* If the user try to start another hangman when there is one exit in current channel, The InputError will be raised.
* the functions hangman_evil_answer and hangman_clear_game_data is used to test the hangman_start and hangman_guess. It does not have any actual functionality for the hangman game.

### user.py

* The test of user_profile_upload function, does not have full coverage, because to generate the img_url the function need to be run though the rotate.

## message.py

* Additional InputError added, exception is raised when /guess for a hangman game tries to guess more than one chracter.
