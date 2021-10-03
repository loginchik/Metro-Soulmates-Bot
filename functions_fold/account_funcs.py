import sqlite3 as sq
import classes
import consts
from functions_fold import error_funcs

bot = consts.bot


# ----- Register new user -----

# Func identifies number of a way given by user
def identify_way(message):
    try:
        # If it's a metro way, it'll work
        way = int(message.text)
        return way
    except:
        # If it's a MCD way, this will work
        if str(message.text) in ['МЦД 1', 'мцд 1']:
            way = 21
            return way
        elif str(message.text) in ['МЦД 2', 'мцд 2']:
            way = 22
            return way


# Func gets the number of stations with a name given by user
def check_stat_exists_by_name(station_name):
    # Connect to db
    con = sq.connect('db/metro.db')
    cur = con.cursor()

    # Collect data
    cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (station_name,))
    stats_num_cur = cur.fetchone()[0]

    # Close connection
    con.close()

    return stats_num_cur


# Func gets the number of stations with a name and way's number given by user
def check_stat_exists_by_way_name(way, name):
    # Connect to db
    con = sq.connect('db/metro.db')
    cur = con.cursor()

    # Collect data from db
    cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, name))
    got = cur.fetchone()[0]

    # Close connection
    con.close()

    # Check if exists
    if got > 0:
        exists = True
    else:
        exists = False

    # Return bool
    return exists


# Func sends warning about the fact that few stations with same name exist and asks for an exact way number
def send_few_stations_warning(chat_id):
    # Send warning
    bot.send_message(chat_id, consts.few_stations_warning_first_text)
    with open('metroways.png', 'rb') as img:
        way_num = bot.send_photo(chat_id, photo=img)
    bot.send_message(chat_id, consts.few_stations_warning_second_text)

    # Returns a message for next steps
    return way_num


# Func gets unique code
# Suitable if station's name is unique
def get_code_by_name(station_name):
    # Connect to db
    con = sq.connect('db/metro.db')
    cur = con.cursor()

    # Get code
    cur.execute('''SELECT code FROM stations_coo WHERE name=?''', (station_name,))
    code = cur.fetchone()[0]

    # Close connection
    con.close()

    # Return code as a variable
    return code


# Func gets unique code
# Suitable if there are few stations with the same name
def get_code_by_way_name(station_way, station_name):
    # Connect to db
    con = sq.connect('db/metro.db')
    cur = con.cursor()

    # Get unique code
    cur.execute("SELECT code FROM stations_coo WHERE name=? AND way=?", (station_name, station_way))
    code = cur.fetchone()[0]

    # Close connection
    con.close()

    # Return code as a variable
    return code


# Func creates a record and inserts there user id, first name and nickname given by TG
def get_basic_step(message):
    try:
        # Save current user message data
        chat_id = message.from_user.id

        # Save data for loading to db
        user_id = int(message.from_user.id)
        name = str(message.from_user.first_name).lower()
        nickname = str(message.from_user.username).lower()

        # Load data to db
        with sq.connect('db/users.db') as con:
            cur = con.cursor()
            cur.execute('''INSERT INTO users (user_id, first_name, nickname) VALUES (?, ?, ?)''',
                        (user_id, name, nickname))
            con.commit()

        # Follow next step of registration (get departure station)
        send = bot.send_message(chat_id, text=consts.dep_ask_text)
        bot.register_next_step_handler(send, get_dep_step)
    except:
        error_funcs.other_error(message)


# Func gets departure information
def get_dep_step(message):
    try:
        # Save current user message data
        chat_id = message.from_user.id
        user_id = message.from_user.id

        # Save departure station name into variable
        dep_name = str(message.text).lower()

        # Count stations with the same name
        stats_num_cur = check_stat_exists_by_name(dep_name)

        if stats_num_cur == 0:
            # Means that user gave a wrong name or the station is not in db
            error_funcs.no_station_found(message)

        if stats_num_cur == 1:
            # Means that this station is the only one

            # Get departure station's unique code
            code_dep = get_code_by_name(dep_name)

            # Connect to db to add data to user profile
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE users SET metro_dep=? WHERE user_id=?''', (code_dep, user_id))
                con.commit()

            # Follow next step of registration (get arrival station)
            send = bot.send_message(message.chat.id, text=consts.arr_ask_text)
            bot.register_next_step_handler(send, get_arr)

        if stats_num_cur > 1:
            # Means that there are few stations with same name

            # Send warning about the issue and ask for a way number
            way_num = send_few_stations_warning(chat_id)

            # Follow next step of registration (get the current departure station)
            bot.register_next_step_handler(way_num, few_ways_st_dep, dep_name)

    except:
        error_funcs.other_error(message)


# Funcs gets departure information if few stations with the same name exist
def few_ways_st_dep(message, dep_name):
    # Func gets exact station if few with same name exist

    try:
        # Save current user message data
        chat_id = message.from_user.id
        user_id = message.from_user.id

        # Get exact way number
        way = identify_way(message)

        # Check if station with given name and way exists
        exists = check_stat_exists_by_way_name(way, dep_name)

        if exists:
            dep_way = way

            # Get the station unique code
            code_dep = get_code_by_way_name(dep_way, dep_name)

            # Write data to user profile in db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE users SET metro_dep=? WHERE user_id=?''', (code_dep, user_id))
                con.commit()

            # Follow next step of registration (get arrival station)
            send = bot.send_message(chat_id, text=consts.arr_ask_text)
            bot.register_next_step_handler(send, get_arr)

        if not exists:
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


# Func gets arrival information
def get_arr(message):
    try:
        # Save current user info
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Save the name of arrival station
        arr_name = str(message.text).lower()

        # Count stations with the same name
        stats_num_cur = check_stat_exists_by_name(arr_name)

        if stats_num_cur == 0:
            # Means that user gave a wrong name or stations isn't in db

            # Send error warning
            error_funcs.no_station_found(message)

        if stats_num_cur == 1:
            # Means that there is the only one station with this name

            # Get the unique code of the station
            code_arr = get_code_by_name(arr_name)

            # Load data to user profile in db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE users SET metro_arr=? WHERE user_id=?''', (code_arr, user_id))
                con.commit()

            # Send account created confirmation message
            bot.send_message(chat_id=message.chat.id, text=consts.acc_create_conf_text)

        if stats_num_cur > 1:
            # Means that there are few stations with this name

            # Send a warning about this issue
            way_num = send_few_stations_warning(chat_id)

            # Follow next step of registration (get exact arrival station)
            bot.register_next_step_handler(way_num, few_ways_st_arr, arr_name)
    except:
        error_funcs.other_error(message)


# Funcs gets arrival information if few stations with the same name exist
def few_ways_st_arr(message, arr_name):
    try:
        # Save current user message data
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Get exact way number
        way = identify_way(message)

        # Check if station with this way's number and name is in db
        exists = check_stat_exists_by_way_name(way, arr_name)

        if exists:
            arr_way = way

            # Get unique code of the station
            code_arr = get_code_by_way_name(arr_way, arr_name)

            # Load data to user's profile in db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('''UPDATE users SET metro_arr=? WHERE user_id=?''', (code_arr, user_id))
                con.commit()

            # Send account confirmation message
            bot.send_message(chat_id, text=consts.acc_create_conf_text)

        if not exists:
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


# ----- Delete account -----

# Func gets confirmation and, if positive, deletes account
def del_confirm(message, user_id):
    # Save user's message data
    chat_id = message.chat.id

    # Check if the answer is text
    if message.content_type == 'text':

        # Save decision
        decision = str(message.text).lower()

        # Decision is positive
        if decision == 'да':
            try:
                # Delete user from db
                remove_user(user_id)

                # Send account deleted confirmation messages
                bot.send_message(chat_id, text=consts.acc_del_conf_text)
                bot.send_message(chat_id, text=consts.goodbye_text)
            except:
                error_funcs.other_error(message)

        # Decision is negative
        elif decision == 'нет':

            # Send account not deleted confirmation message
            bot.send_message(chat_id=message.chat.id, text=consts.do_not_delete_acc_text)

        else:
            error_funcs.other_error(message)

    else:
        # Send warning that not text was given
        error_funcs.not_text_error(message)


# Func removes user's data from db
def remove_user(user_id):
    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Delete data
    cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    # Close connection
    con.commit()
    con.close()


# Func starts account delete process
def delete_account(message):
    try:
        # Save user's message data
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Ask for account delete confirmation
        decision = bot.send_message(chat_id, text=consts.delete_acc_confirm_ask_text)
        bot.register_next_step_handler(decision, del_confirm, user_id)

    except:
        error_funcs.other_error(message)


# ----- View account ----

# Func returns MDC name or metro way num if it's a metro
def get_way_name(way_number):
    if way_number < 20:
        way_name = way_number
        return way_name

    elif way_number == 21:
        way_name = 'МДЦ 1'
        return way_name

    elif way_number == 22:
        way_name = 'МДЦ 2'
        return way_name

    else:
        pass


# Func collects data about the user and makes a text for message
def prof_info(user_id):
    # Create user class to save data
    user = classes.User(user_id)

    # Connect to users db to collect data
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user.user_id,))
        user_info = cur.fetchone()
        user.name = user_info[2]
        user.nickname = user_info[3]
        user.dep_code = user_info[4]
        user.arr_code = user_info[5]
        user.stars = user_info[6]

    # Connect to metro db to get stations' names and ways
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        # Departure station
        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (user.dep_code,))
        for name in cur.fetchall():
            user.dep_way = name[0]
            user.dep_name = name[1]

        # Arrival station
        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (user.arr_code,))
        for name in cur.fetchall():
            user.arr_way = name[0]
            user.arr_name = name[1]

    # Create a text to send to user

    dep_way_name = get_way_name(user.dep_way)
    arr_way_name = get_way_name(user.arr_way)

    text = '{0}\n@{1}\n\n⭐: {2}\n\n🚇 Метро отправления:\n{3} ({4} линия)\n\n🚇 Метро прибытия:\n{5} ({6} линия)'.format(
        str(user.name).title(),
        str(user.nickname),
        str(user.stars),
        str(user.dep_name).title(),
        str(dep_way_name),
        str(user.arr_name).title(),
        str(arr_way_name)
    )
    return text


# Func starts account info sending process
def view_acc_func(message):
    try:
        # Save user's message data
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Get text for message
        text = prof_info(user_id)

        # Send user's profile information
        bot.send_message(chat_id, text=text)

    except:
        error_funcs.other_error(message)


# ----- Edit account -----

# Func changes user's name in db
def change_name(message):
    try:
        # Save user's message data
        user_id = message.from_user.id

        # Save new name into variable
        new_name = str(message.text).lower()

        # Load new data to db
        with sq.connect('db/users.db') as con:
            cur = con.cursor()
            cur.execute('''UPDATE users SET first_name=? WHERE user_id=?''', (new_name, user_id))
            con.commit()

        # Send account information as a result
        view_acc_func(message)

    except:
        error_funcs.other_error(message)


# Func updates nickname in db
def update_nickname(message, user_id):
    # Get new nick from TG data
    new_nick = message.from_user.username

    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Load new data to db
    cur.execute('''UPDATE users SET nickname=? WHERE user_id=?''', (new_nick, user_id))

    # Close connection
    con.commit()
    con.close()

    # Send account info as a result
    view_acc_func(message)


# Func changes departure station in db of forwards to the next step
def change_dep(message):
    try:
        # Save user's message data
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Save new departure station's name
        new_dep_name = str(message.text).lower()

        # Get the number if station with this name
        stats_num = check_stat_exists_by_name(new_dep_name)

        if stats_num == 0:
            # Means that the name is wrong or station is not in db
            error_funcs.no_station_found(message)

        elif stats_num == 1:
            # Means that there is the only one station with this name

            # Get new departure station's unique code
            new_dep_code = get_code_by_name(new_dep_name)

            # Connect to users db
            con = sq.connect('db/users.db')
            cur = con.cursor()

            # Load new data to db
            cur.execute('UPDATE users SET metro_dep=? WHERE user_id=?', (new_dep_code, user_id))

            # Close connection
            con.commit()
            con.close()

            # Send account information as a result
            view_acc_func(message)

        elif stats_num > 1:
            # Means that there are few stations with the same name

            # Send warning about the issue and ask for way number
            way_num = send_few_stations_warning(chat_id)

            # Follow next step (get exact new departure station)
            bot.register_next_step_handler(way_num, change_dep_few_stations, new_dep_name)

    except:
        error_funcs.other_error(message)


# Func changes departure station in db if there are few with the same name
def change_dep_few_stations(message, station_name):
    try:
        # Save user's message data
        user_id = message.from_user.id

        # Get way number
        new_dep_way = identify_way(message)
        new_dep_name = station_name

        # Check if exists
        exists = check_stat_exists_by_way_name(way=new_dep_way, name=new_dep_name)

        if exists:
            # Get new departure station's unique code
            new_dep_code = get_code_by_way_name(station_way=new_dep_way, station_name=new_dep_name)

            # Load data to db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_dep=? WHERE user_id=?', (new_dep_code, user_id))
                con.commit()

            # Send account info as a result
            view_acc_func(message)

        elif not exists:
            error_funcs.no_station_found(message)

    except:
        error_funcs.other_error(message)


# Func changes arrival station in db of forwards to the next step
def change_arr(message):
    try:
        # Save user's message info
        user_id = message.from_user.id
        chat_id = message.chat.id

        # Save new arrival station's name
        new_arr_name = str(message.text).lower()

        # Get the number of stations with this name
        stats_num = check_stat_exists_by_name(station_name=new_arr_name)

        if stats_num == 0:
            # Means that the name is wrong of station is not in db
            error_funcs.no_station_found(message)

        elif stats_num == 1:
            # Means that there is the only station with this name

            # Get unique code of new arrival station
            new_arr_code = get_code_by_name(new_arr_name)

            # Load new data to db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_arr=? WHERE user_id=?', (new_arr_code, user_id))
                con.commit()

            # Send account info as a result
            view_acc_func(message)

        elif stats_num > 1:
            # Means that there are few stations with this name

            # Send warning about the issue and ask for an exact way number
            way_num = send_few_stations_warning(chat_id)

            # Follow next step (get an exact new arrival station)
            bot.register_next_step_handler(way_num, change_arr_few_stations, new_arr_name)

    except:
        error_funcs.other_error(message)


# Func changes arrival station in db if there are few stations with the same name
def change_arr_few_stations(message, station_name):
    try:
        # Save user's message data
        user_id = message.from_user.id

        # Save new arrival station's info
        new_arr_way = identify_way(message)
        new_arr_name = station_name

        # Check if station exists
        exists = check_stat_exists_by_way_name(way=new_arr_name, name=new_arr_name)

        if exists:

            # Get new arrival station's unique code
            new_arr_code = get_code_by_way_name(station_way=new_arr_way, station_name=new_arr_name)

            # Load new data to db
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_arr=? WHERE user_id=?', (new_arr_code, user_id))
                con.commit()

            # Send account info as a result
            view_acc_func(message)

        elif not exists:
            error_funcs.no_station_found(message)

    except:
        error_funcs.other_error(message)


# Func sends a message asking what to edit
# Func starts account editing process
def ask_what_to_edit_step(message):
    try:
        # Save user's message data
        chat_id = message.chat.id

        # Send message asking what to change
        msg = bot.send_message(chat_id, text=consts.what_to_change_text)

        # Follow next step (work with a decision)
        bot.register_next_step_handler(msg, forward_to_func_step)

    except:
        error_funcs.other_error(message)


# Func forwards to next step of account editing process
def forward_to_func_step(message):
    try:
        # Save user's message data
        chat_id = message.chat.id
        user_id = message.from_user.id

        # Check if the message is text
        if message.content_type == 'text':

            # Save decision
            msg = str(message.text).lower()

            # Change name
            if msg == 'имя':

                # Ask for new name
                new_name = bot.send_message(chat_id, text=consts.new_name_text)

                # Follow next step (change data in db and send confirmation)
                bot.register_next_step_handler(new_name, change_name)

            # Update nickname
            elif msg == 'никнейм':

                # Send warning what is going on
                bot.send_message(chat_id, text=consts.nick_update_text)

                # Follow next step (update nickname and send confirmation
                update_nickname(message, user_id)

            # Change departure station
            elif msg == 'станция отправления':

                # Ask for new departure station's name
                new_dep = bot.send_message(chat_id, text=consts.new_dep_text)

                # Follow next step (change departure station in db and send confirmation)
                bot.register_next_step_handler(new_dep, change_dep)

            # Change arrival station
            elif msg == 'станция прибытия':

                # Ask for new arrival station's name
                new_arr = bot.send_message(chat_id, text=consts.new_arr_text)

                # Follow next step (change arrival station in db and send confirmation)
                bot.register_next_step_handler(new_arr, change_arr)

        else:
            error_funcs.not_text_error(message)

    except:
        error_funcs.other_error(message)
