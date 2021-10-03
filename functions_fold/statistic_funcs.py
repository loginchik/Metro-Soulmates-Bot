import sqlite3 as sq
from datetime import datetime

import error_funcs
from consts import bot


# Func leads all the statistic collecting and saving process
def admin_stats(message):
    try:
        # Save user's message data
        chat_id = message.chat.id

        # Send notification
        bot.send_message(chat_id, 'Started')

        # Connect to db
        con = sq.connect('db/users.db')
        cur = con.cursor()

        # Collect data
        cur.execute('SELECT count(user_id) FROM users')
        users_num = cur.fetchone()[0]

        # Close connection
        con.close()

        # Get confirmations statistic
        conf_list = main_conf_stats()

        # Introduce exact variables
        all_conf_num = conf_list[0]
        today_conf_num = conf_list[1]

        # # Collect stats from db
        # with sq.connect('db/users.db') as con:
        #     cur = con.cursor()
        #
        #     cur.execute('SELECT all_usages, today_usages FROM statistics WHERE func_name = ?', ('/soulssearch',))
        #     soulssearch_stats_pack = cur.fetchone()
        #
        #     cur.execute('SELECT all_usages, today_usages FROM statistics WHERE func_name = ?', ('/register',))
        #     register_stats_pack = cur.fetchone()
        #
        #     cur.execute('SELECT all_usages, today_usages FROM statistics WHERE func_name = ?', ('/deleteaccount',))
        #     deleteaccount_stats_pack = cur.fetchone()
        #
        # # Unpack collected statistics
        # soulssearch_all = soulssearch_stats_pack[0]
        # soulsearch_today = soulssearch_stats_pack[1]
        #
        # register_all = register_stats_pack[0]
        # register_today = register_stats_pack[1]
        #
        # deleteaccount_all = deleteaccount_stats_pack[0]
        # deleteaccount_today = deleteaccount_stats_pack[1]
        #
        # # Generate text
        # text = 'Users: {0}\n\nConfirms: {1}\nToday: {2}' \
        #        '\n\nCommands statistics' \
        #        '\n\nregister' \
        #        '\nall: {3}' \
        #        '\ntoday: {4}' \
        #        '\n\nsoulssearch' \
        #        '\nall: {5}' \
        #        '\ntoday: {6}' \
        #        '\n\ndeleteaccount' \
        #        '\nall: {7}' \
        #        '\ntoday: {8}'.format(str(users_num),
        #                              str(all_conf_num),
        #                              str(today_conf_num),
        #                              str(register_all),
        #                              str(register_today),
        #                              str(soulssearch_all),
        #                              str(soulsearch_today),
        #                              str(deleteaccount_all),
        #                              str(deleteaccount_today))

        text = 'Users: {0}\n\nConfirms: {1}\nToday: {2}'.format(str(users_num), str(all_conf_num), str(today_conf_num))

        # Send statistics to admin
        bot.send_message(chat_id, text)

    except:
        error_funcs.other_error(message)


# Func collects all confirms from db
def get_all_confs_date():
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('SELECT date FROM confirms')
        all_confirms_list = cur.fetchall()

    return all_confirms_list


# Func returns a list of dates of all confirms
def get_dates_from_all_confs(all_confirms_list):
    # Create empty list to store dates
    confs_dates = []

    for complex_date in all_confirms_list:
        # Split data into date and time
        complex_date_split = complex_date.split()

        # Identify date
        date = complex_date_split[0]

        # Append date into list
        confs_dates.append(date)

    return confs_dates


# Func returns a number of today's confirmations
def find_todays(confs_dates_list, today):
    # Create a variable to return number
    today_num = 0

    # Find today's confirmations
    for date in confs_dates_list:
        if date == today:
            today_num = today_num + 1
        else:
            pass

    # Return number
    return today_num


# Func leads the process of collecting confirmation statistic
def main_conf_stats():
    # Get all confirms from db
    all_confirms_list = get_all_confs_date()

    # Count the number of all confirms
    all_confirms_num = len(all_confirms_list)

    if all_confirms_num > 0:

        # Collect all confirmations' dates from db
        confs_dates = get_dates_from_all_confs(all_confirms_list)

        # Get today's date
        today = datetime.today().date()

        # Find today's confirmations
        today_conf_num = find_todays(confs_dates_list=confs_dates, today=today)

        # Return variables
        return [all_confirms_num, today_conf_num]

    elif all_confirms_list == 0:

        today_conf_num = 0

        # Return variables
        return [all_confirms_num, today_conf_num]


# Func writes new stats
def write_stats(func_name):
    current_datetime = str(datetime.now())

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('SELECT count(*) FROM statistics WHERE func_name=?', (func_name,))
        exists = cur.fetchone()[0]
        if exists == 0:
            # Create new record
            cur.execute('INSERT INTO statistics (func_name, all_usages, today_usages, last_update) VALUES '
                        '(?, 1, 1, ?)', (str(func_name), current_datetime))
        if exists > 0:

            # Update all usages
            cur.execute('UPDATE statistics SET all_usages = all_usages + 1 WHERE func_name=?', func_name)
            con.commit()

            # Get last update
            cur.execute('SELECT last_update FROM statistics WHERE func_name = ?', (func_name,))
            last_update_complex = str(cur.fetchone()[0])

            # Get date from last update
            last_update_complex_split = last_update_complex.split()
            last_update_date = last_update_complex_split[0]

            # Check if it's today
            today = datetime.now().date()
            if last_update_date == today:
                cur.execute('UPDATE statistics SET today_usages = today_usages + 1 WHERE func_name = ?', (func_name,))
                con.commit()

            elif last_update_date != today:
                cur.execute('UPDATE statistics SET today_usages=1 WHERE func_name = ?', (func_name,))
                con.commit()

            # Update last update
            cur.execute('UPDATE statistics SET last_update = ? WHERE func_name = ?', (current_datetime, func_name))
            con.commit()
