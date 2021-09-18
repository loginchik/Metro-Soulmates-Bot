import sqlite3 as sq
from functions_fold import error_funcs
import classes
import consts

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
        user_info = cur.fetchone()
        user.name = user_info[2]
        user.nickname = user_info[3]
        user.dep_code = user_info[4]
        user.arr_code = user_info[5]
        user.stars = user_info[6]

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
    text = "Имя — " + str(user.name).title() + \
           '\n' + "Ник в телеграме — @" + str(user.nickname) + \
           '\n\n' + "Метро отправленя: \n" + str(user.dep_name).title() + " (" + str(user.dep_way) + \
           " линия метро)" + \
           '\n\n' + "Метро прибытия: \n" + str(user.arr_name).title() + \
           " (" + str(user.arr_way) + " линия метро)" + \
           '\n\n' + 'Звезд: ' + str(user.stars)
    return text


# Registration
def get_basic_step(message):
    try:
        global user_1
        user_1.user_id = int(message.from_user.id)
        user_1.name = str(message.from_user.first_name).lower()
        user_1.nickname = str(message.from_user.username).lower()

        # follow next step
        send = bot.send_message(message.chat.id, text=consts.mdep_ask_text)
        bot.register_next_step_handler(send, get_dep_step)
    except:
        error_funcs.other_error(message)


def get_dep_step(message):
    try:
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
                error_funcs.no_station_found(message)
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
            with open('metroways.png', 'rb') as img:
                way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_dep)
    except:
        error_funcs.other_error(message)


def few_ways_st_dep(message):
    try:
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
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


def get_arr(message):
    try:
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
            error_funcs.no_station_found(message)
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
            with open('metroways.png', 'rb') as img:
                way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_arr)
    except:
        error_funcs.other_error(message)


def few_ways_st_arr(message):
    try:
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

                cur.execute('''SELECT code FROM stations_coo WHERE name=? AND way=?''',
                            (user_1.arr_name, user_1.arr_way))
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
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


# Delete account
def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        con.commit()


def delete_account(message):
    try:
        global user_1
        chat_id = message.chat.id
        user_id = message.from_user.id

        remove_user(user_id)
        bot.send_message(chat_id, text=consts.acc_del_conf_text)
        user_1.delete_account()
    except:
        error_funcs.other_error(message)


# View account
def view_acc_func(message):
    try:
        global user_1
        text = prof_info(message.from_user.id)
        bot.send_message(message.chat.id, text=text)
    except:
        error_funcs.other_error(message)
