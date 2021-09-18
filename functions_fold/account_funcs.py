import consts
import sqlite3 as sq
import classes
import functions_fold.error_funcs

user_1 = consts.user
bot = consts.bot


# write information about new user into db
def write_new_user(user_id, first_name, nickname, metro_dep, metro_arr):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('INSERT INTO users (user_id, first_name, nickname, metro_dep, metro_arr)'
                    'VALUES (?, ?, ?, ?, ?)', (user_id, first_name, nickname, metro_dep, metro_arr))
        con.commit()


def prof_info(user_id):
    user = classes.User(user_id)

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("SELECT * FROM users WHERE user_id=?", (user.user_id,))
        user_info = cur.fetchall()

        # Unpack dict
        for key in user_info:
            user.name = key[2]
            user.nickname = key[3]
            user.dep_code = key[4]
            user.arr_code = key[5]

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (user.dep_code,))
        for name in cur.fetchall():
            user.dep_way = name[0]
            user.dep_name = name[1]

        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (user.arr_code,))
        for name in cur.fetchall():
            user.arr_way = name[0]
            user.arr_name = name[1]
    text = "Имя — " + str(user.name).title() + '\n' + "Ник в телеграме — @" + str(user.nickname) + \
           '\n\n' + "Метро отправленя: \n" + str(user.dep_name).title() + " (" + str(user.dep_way) + \
           " линия метро)\n" + '\n' + "Метро прибытия: \n" + str(user.arr_name).title() + \
           " (" + str(user.arr_way) + " линия метро)"
    return text


def check_reg_status(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("SELECT count(user_id) FROM users WHERE user_id=?", (user_id,))
        users_exist = cur.fetchall()

        # Get number of existing users with this user_id
        k = users_exist[0]
        m = ''.join(str(x) for x in k)
        m = int(m)
        if m > 0:
            reg_status = True
        if m == 0:
            reg_status = False

    return reg_status


# Registration
def checking_registration(message):
    global user_1
    chat_id = message.chat.id
    user_id = message.from_user.id

    user_1.reg_status = check_reg_status(user_id)

    if user_1.reg_status:
        bot.send_message(chat_id, text=consts.acc_exists_text)
        prof_info(user_1.user_id)
    else:
        user_1.user_id = int(message.from_user.id)
        user_1.name = str(message.from_user.first_name).lower()
        user_1.nickname = str(message.from_user.username).lower()

        # follow next step
        send = bot.send_message(message.chat.id, text=consts.mdep_ask_text)
        bot.register_next_step_handler(send, get_dep)


def get_dep(message):
    global user_1

    # saving metro dep
    user_1.dep_name = str(message.text).lower()

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (user_1.dep_name,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

        if stats_num_cur == 0:
            bot.send_message(message.chat.id, text=consts.no_station_error_text)
        if stats_num_cur == 1:
            cur.execute('''SELECT code FROM stations_coo WHERE name=?''', (user_1.dep_name,))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_dep = str(''.join(code)).lower()
            user_1.dep_code = code_dep

            # follow next step
            send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
            bot.register_next_step_handler(send, get_arr)

    if stats_num_cur > 1:
        way_num = bot.send_message(message.chat.id, text=consts.way_ask_text)
        bot.register_next_step_handler(way_num, few_ways_st_dep)


def few_ways_st_dep(message):
    global user_1

    way = int(message.text)

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, user_1.dep_name))
        got = cur.fetchone()
        for i in got:
            print(i)
            if i > 0:
                exists = True
            else:
                exists = False

    if exists:
        user_1.dep_way = way

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()

            cur.execute("SELECT code FROM stations_coo WHERE name=? AND way=?", (user_1.dep_name, user_1.dep_way))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_dep = str(''.join(code)).lower()
        user_1.dep_code = code_dep

        # follow next step
        send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
        bot.register_next_step_handler(send, get_arr)

    if not exists:
        bot.send_message(message.chat.id, text=consts.few_ways_no_station_text)


def get_arr(message):
    global user_1

    # save metro arr
    user_1.arr_name = str(message.text).lower()

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (user_1.arr_name,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

    if stats_num_cur == 0:
        bot.send_message(message.chat.id, text=consts.no_station_error_text)
    if stats_num_cur == 1:
        cur.execute("SELECT code FROM stations_coo WHERE name=?", (user_1.arr_name,))
        code_pack = cur.fetchall()
        for code in code_pack:
            code_arr = str(''.join(code)).lower()
            user_1.arr_code = code_arr
        write_new_user(user_id=user_1.user_id,
                       first_name=user_1.name,
                       nickname=user_1.nickname,
                       metro_dep=user_1.dep_code,
                       metro_arr=user_1.arr_code
                       )
    if stats_num_cur > 1:
        way_num = bot.send_message(message.chat.id, text=consts.way_ask_text)
        bot.register_next_step_handler(way_num, few_ways_st_arr)


def few_ways_st_arr(message):
    global user_1

    way = int(message.text)

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, user_1.arr_name))
        got = cur.fetchone()
        for i in got:
            if i > 0:
                exists = True
            else:
                exists = False

    if exists:
        user_1.arr_way = way

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT code FROM stations_coo WHERE name=? AND way=?''', (user_1.arr_name, user_1.arr_way))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_arr = str(''.join(code)).lower()
        user_1.arr_code = code_arr
        write_new_user(user_id=user_1.user_id,
                       first_name=user_1.name,
                       nickname=user_1.nickname,
                       metro_dep=user_1.dep_code,
                       metro_arr=user_1.arr_code
                       )
        user_1.reg_status = True
        bot.send_message(message.chat.id, text=consts.acc_create_conf_text)

    if not exists:
        bot.send_message(message.chat.id, text=consts.few_ways_no_station_text)


# Delete account
def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        con.commit()


def delete_account(message):
    global user_1
    chat_id = message.chat.id
    user_id = message.from_user.id

    if user_1.reg_status is None:
        user_1.reg_status = check_reg_status(user_id)

    if not user_1.reg_status:
        bot.send_message(chat_id, text=consts.no_registration_error_text)
    elif user_1.reg_status:
        remove_user(user_id)
        bot.send_message(chat_id, consts.acc_del_conf_text)
        user_1.delete_account()
    else:
        functions_fold.error_funcs.other_error(message)


# View account
def view_acc_func(message):
    global user_1

    if user_1.reg_status:
        text = prof_info(message.from_user.id)
        bot.send_message(message.chat.id, text=text)
    if not user_1.reg_status:
        bot.send_message(message.chat.id, text=consts.no_registration_error_text)
