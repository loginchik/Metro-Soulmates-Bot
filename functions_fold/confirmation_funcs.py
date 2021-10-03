import shutil
import sqlite3 as sq
from datetime import datetime
from functions_fold import error_funcs
import classes
import consts

bot = consts.bot


# Func saves voice confirmations
def voice_processing(message, file_name):
    # Get file from message
    file_info = bot.get_file(message.voice.file_id)

    # Download file
    downloaded_file = bot.download_file(file_info.file_path)

    # Save file to server
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Move file to confirms folder
    shutil.move(file_name, 'confirms')


# Func saves photo confirmations
def photo_processing(message, file_name):
    # Get file from message
    file_info = bot.get_file(message.photo[-1].file_id)

    # Download file
    downloaded_file = bot.download_file(file_info.file_path)

    # Save file to server
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Move file to confirms folder
    shutil.move(file_name, 'confirms')


# Func saves video confirmations
def video_note_processing(message, file_name):
    # Get file from message
    file_info = bot.get_file(message.video_note.file_id)

    # Download file
    downloaded_file = bot.download_file(file_info.file_path)

    # Save file to server
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Move file to confirms folder
    shutil.move(file_name, 'confirms')


# Func loads confirmation info from the first user into db
def write_conf(confirmation_class):
    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Write new data
    cur.execute('''INSERT INTO confirms (user_id, soul_id, date, file) VALUES (?, ?, ?, ?)''',
                (confirmation_class.user_id,
                 confirmation_class.soul_id,
                 confirmation_class.date,
                 confirmation_class.file_name)
                )

    # Close connection
    con.commit()
    con.close()


# ----- Get confirm from first user -----

# Gets soul's nick from message
def get_soul_nick(message):
    # Save message text
    got_soul_nick = str(message.text).lower()

    # Split potential nick into letters
    list_soul_nick = []
    for i in got_soul_nick:
        list_soul_nick.append(i.lower())

    # Check if it starts with @
    if list_soul_nick[0] == '@':

        # Delete @ from nick
        del list_soul_nick[0]

        # Merge letters into variable
        soul_nick = ''.join(list_soul_nick)
    else:
        soul_nick = 'error'

    return soul_nick


# Get soul's id from db using nickname
def get_soul_id_from_nick(soul_nick):
    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Get soul's id from db
    cur.execute('SELECT user_id FROM users WHERE nickname=?', (soul_nick,))
    soul_id_pack = cur.fetchall()

    # Close connection
    con.close()

    # Get soul's id from package
    if len(soul_id_pack) == 0:
        # Means that soul is not found in db
        soul_id = 'not found'
        return soul_id

    elif len(soul_id_pack) == 1:
        # Means that user is found

        # Get id from package
        for i in soul_id_pack:
            soul_id = i[0]
            return soul_id

    else:
        # IDK that's the error that can happen
        soul_id = 'error'
        return soul_id


# Func saves user's id and forwards to the next step (soul id)
def start_conf_process(message):
    # Save user's message data
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Create confirmation class to store information
    confirmation_class = classes.Confirmation()
    confirmation_class.user_id = int(user_id)

    # Send message asking for soul nickname
    msg = bot.send_message(chat_id, consts.ask_for_soul_nick)

    # Follow next step of confirmation process - save soul's id
    bot.register_next_step_handler(msg, get_soul_id, confirmation_class)


# Func saves soul's id and forwards to the next step
def get_soul_id(message, confirmation_class):
    try:
        # Save user's message data
        chat_id = message.chat.id

        # Check if message is text
        if message.content_type == 'text':

            # Save
            soul_nick = get_soul_nick(message)
            if soul_nick == 'error':
                error_funcs.not_nick_sent(message)
            else:
                soul_id = get_soul_id_from_nick(soul_nick)

                # Work with errors
                if soul_id == 'not found':
                    error_funcs.soul_not_registered(message)
                elif soul_id == 'error':
                    error_funcs.other_error(message)

                # Continue process if it's possible
                else:
                    # Save soul's id into confirmation class
                    confirmation_class.soul_id = soul_id

                    # Ask for confirmation file
                    msg = bot.send_message(chat_id, consts.ask_for_conf_text)

                    # Follow next step (save confirmation file)
                    bot.register_next_step_handler(msg, get_conf, confirmation_class)
        else:
            error_funcs.not_text_error(message)

    except:
        error_funcs.other_error(message)


# Last step of first user confirmation process
# Saves confirmation info and file
def get_conf(message, confirmation_class):
    # Save user's message data
    chat_id = message.chat.id

    if message.content_type == 'voice' or 'photo' or 'video_note':
        try:
            # Get current date and time
            confirmation_class.date = datetime.now()

            # Voice confirmation
            if message.content_type == 'voice':

                # Generate a file name
                file_name = str(confirmation_class.user_id) + '_' + str(confirmation_class.date) + '.ogg'
                confirmation_class.file_name = file_name

                # Save confirmation file to server
                voice_processing(message, file_name)

                # Write confirmation info into db
                write_conf(confirmation_class)

                # Send confirmation successful notification
                bot.send_message(chat_id, text=consts.conf_success_text)

            # Photo confirmation
            elif message.content_type == 'photo':

                # Generate a file name
                file_name = str(confirmation_class.user_id) + '_' + str(confirmation_class.date) + '.png'
                confirmation_class.file_name = file_name

                # Save confirmation file to server
                photo_processing(message, file_name)

                # Write confirmation info into db
                write_conf(confirmation_class)

                # Send confirmation is successful notification
                bot.send_message(chat_id, text=consts.conf_success_text)

            # Video confirmation
            elif message.content_type == 'video_note':

                # Generate a file name
                file_name = str(confirmation_class.user_id) + '_' + str(confirmation_class.date) + '.mp4'
                confirmation_class.file_name = file_name

                # Save confirmation file to server
                video_note_processing(message, file_name)

                # Write confirmation info into db
                write_conf(confirmation_class)

                # Send confirmation is successful notification
                bot.send_message(chat_id, text=consts.conf_success_text)

            # Not suitable format
            else:
                error_funcs.not_suitable_conf_format(message)

        except:
            error_funcs.other_error(message)


# ----- Get confirmation from second user (soul) -----

# Func returns a list from date info
def datetime_list(meet_date):
    date_list = meet_date.split()
    date_date = date_list[0]
    date_time = date_list[1]

    date_date_list = date_date.split('-')
    year = date_date_list[0]
    month = date_date_list[1]
    day = date_date_list[2]

    date_time_list = date_time.split(':')
    hour = date_time_list[0]
    minute = date_time_list[1]

    return [year, month, day, hour, minute]


# Func updates data in db depending on approval
def get_approval(message, confirmation_class):
    # Check if new message is text
    if message.content_type == 'text':

        # Save approval into variable
        approval = str(message.text).lower()

        # Positive approval
        if approval == 'да':

            # Update data in db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE confirms SET authorized=1 WHERE user_id=? AND soul_id=? AND file=?''',
                            (confirmation_class.user_id, confirmation_class.soul_id, confirmation_class.file_name))
                con.commit()

                # Add stars to both user and soul
                cur.execute('''UPDATE users SET stars=stars+1 WHERE user_id=? OR user_id=?''',
                            (confirmation_class.user_id, confirmation_class.soul_id))
                con.commit()

            # Send the number of unapproved meetings left
            send_unapproved_num(message)

        # Negative approval
        elif approval == 'нет':

            # Update data in db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE confirms SET authorized=-1 WHERE user_id=? AND soul_id=? AND file=?''',
                            (confirmation_class.user_id, confirmation_class.soul_id, confirmation_class.file_name))

            # Send the number of unapproved meetings left
            send_unapproved_num(message)

        else:
            error_funcs.ununderstandable_text(message)

    else:
        error_funcs.not_text_error(message)


# Func count the number of unapproved meetings where the user is soul
def get_unapproved_num(message):
    # Save user's message data
    user_id = message.from_user.id

    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Collect data from db
    cur.execute('''SELECT * FROM confirms WHERE soul_id=? AND authorized=0''', (user_id,))
    unapproved_pack = cur.fetchall()

    # Close connection
    con.close()

    # Count unapproved
    unapproved_num = len(unapproved_pack)

    # Return the number
    return unapproved_num


# Func generates text for send_unapproved_num func depending on the number of unapproved meetings
def generate_unapproved_num_text(unapproved_num):
    if unapproved_num == 1:
        text = 'У Вас {0} неподтвержденная встреча.\n\n{1}'.format(str(unapproved_num), ('/trustme'))

    elif unapproved_num in range(2, 4):
        text = 'У Вас {0} неподтвержденных встречи.\n\n{1}'.format(str(unapproved_num), '/trustme')

    elif unapproved_num > 4:
        text = 'У Вас {0} неподтвержденных встреч.\n\n{1}'.format(str(unapproved_num), '/trustme')

    else:
        text = 'error'

    return text


# Func sends information about unapproved meetings to soul
def send_unapproved_num(message):
    try:
        # Save user's message data
        chat_id = message.chat.id

        # Get the number of unapproved meetings
        unapproved_num = get_unapproved_num(message)

        if unapproved_num == 0:
            # Means that user hasn't met anyone or has approved all the meetings

            # Send result
            bot.send_message(chat_id, text=consts.no_unapproved_text)

        else:
            # If unapproved_num != 0

            # Generate a text
            text = generate_unapproved_num_text(unapproved_num)

            # Work with errors
            if text == 'error':
                error_funcs.other_error(message)

            # Send text
            else:
                bot.send_message(chat_id, text)

    except:
        error_funcs.other_error(message)


# Func starts confirmation for soul process
# Func gets information about unapproved meeting (first in db) and asks for approval
def approve_conf(message):
    try:
        # Save user's message data
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Get the number of unapproved meetings
        unapproved_num = get_unapproved_num(message)

        if unapproved_num > 0:
            # Means that soul hasn't approved all  the meetings

            # Create a confirmation class to store data
            confirmation_class = classes.Confirmation()

            # Connect to db
            con = sq.connect('db/users.db')
            cur = con.cursor()

            # Collect data about the first unapproved meeting in a db
            cur.execute('''SELECT * FROM confirms WHERE authorized=0 AND soul_id=?''', (user_id,))
            meet_info = cur.fetchone()

            # Close connection
            con.close()

            confirmation_class.user_id = meet_info[0]
            confirmation_class.soul_id = meet_info[1]
            confirmation_class.date = meet_info[2]
            confirmation_class.file_name = meet_info[3]

            # Create user class to store data about the soul
            soul = classes.User(user_id)

            # Connect to db
            con = sq.connect('db/users.db')
            cur = con.cursor()

            # Collect name and nickname of soul (user in db)
            cur.execute('''SELECT first_name, nickname FROM users WHERE user_id=?''', (confirmation_class.user_id,))
            soul_info_pack = cur.fetchone()

            # Close connection
            con.close()

            # Save data into class
            soul.name = soul_info_pack[0]
            soul.nickname = soul_info_pack[1]

            # Get meeting's data information for message
            date_list = datetime_list(confirmation_class.date)

            # Generate text for message
            text = '{0}.{1} Вы встрчались с {2} (@{3}). ' \
                   '\n\nЕсли это так, пришлите "да" в ответ. ' \
                   '\nЕсли это не так, пришлите в ответ "нет".'.format(str(date_list[3]),
                                                                       str(date_list[2]),
                                                                       str(soul.name).title(),
                                                                       str(soul.nickname).lower(),
                                                                       )

            # Send message asking for approval
            approval = bot.send_message(chat_id, text=text)

            # Follow next step (work with approval)
            bot.register_next_step_handler(approval, get_approval, confirmation_class)

    except:
        error_funcs.other_error(message)
