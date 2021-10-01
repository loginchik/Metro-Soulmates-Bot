import sqlite3 as sq
from functions_fold import error_funcs
import classes
import consts

user_1 = consts.user
bot = consts.bot


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

    text = str(user.name).title() + \
           '\n@' + str(user.nickname) + \
           '\n\n⭐: ' + str(user.stars) + \
           '\n\n🚇 Метро отправления:\n' + str(user.dep_name).title() + " (" + str(user.dep_way) + \
           " линия)" + \
           '\n\n🚇 Метро прибытия:\n' + str(user.arr_name).title() + \
           " (" + str(user.arr_way) + " линия)"
    return text


# Registration
def get_basic_step(message):
    try:
        user_id = int(message.from_user.id)
        name = str(message.from_user.first_name).lower()
        nickname = str(message.from_user.username).lower()

        with sq.connect('db/users.db') as con:
            cur = con.cursor()
            cur.execute('''INSERT INTO users (user_id, first_name, nickname) VALUES (?, ?, ?)''',
                        (user_id, name, nickname))
            con.commit()

        # follow next step
        send = bot.send_message(message.chat.id, text=consts.mdep_ask_text)
        bot.register_next_step_handler(send, get_dep_step)
    except:
        error_funcs.other_error(message)


def get_dep_step(message):
    try:
        dep_name = str(message.text).lower()
        user_id = message.from_user.id

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (dep_name,))
            stats_here = cur.fetchone()
            stats_num_cur = stats_here[0]

            if stats_num_cur == 0:
                error_funcs.no_station_found(message)
            if stats_num_cur == 1:
                cur.execute('''SELECT code FROM stations_coo WHERE name=?''', (dep_name,))
                code_pack = cur.fetchall()
                for code in code_pack:
                    code_dep = str(''.join(code)).lower()
                con.close()

                with sq.connect('db/users.db') as con:
                    cur = con.cursor()
                    cur.execute('''UPDATE users SET metro_dep=? WHERE user_id=?''', (code_dep, user_id))
                    con.commit()

                # follow next step
                send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
                bot.register_next_step_handler(send, get_arr)

        if stats_num_cur > 1:
            with open('metroways.png', 'rb') as img:
                way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_dep, dep_name)
    except:
        error_funcs.other_error(message)


def few_ways_st_dep(message, dep_name):
    try:
        way = int(message.text)
        user_id = message.from_user.id

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, dep_name))
            got = cur.fetchone()
            for i in got:
                if i > 0:
                    exists = True
                else:
                    exists = False

        if exists:
            dep_way = way

            with sq.connect('db/metro.db') as con:
                cur = con.cursor()

                cur.execute("SELECT code FROM stations_coo WHERE name=? AND way=?", (dep_name, dep_way))
                code_pack = cur.fetchall()
                for code in code_pack:
                    code_dep = str(''.join(code)).lower()
                con.close()

                with sq.connect('db/users.db') as con:
                    cur = con.cursor()
                    cur.execute('''UPDATE users SET metro_dep=? WHERE user_id=?''', (code_dep, user_id))
                    con.commit()

            # follow next step
            send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
            bot.register_next_step_handler(send, get_arr)

        if not exists:
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


def get_arr(message):
    try:
        # save metro arr
        arr_name = str(message.text).lower()
        user_id = message.from_user.id

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (arr_name,))
            stats_here = cur.fetchone()
            stats_num_cur = stats_here[0]

            if stats_num_cur == 0:
                error_funcs.no_station_found(message)

            if stats_num_cur == 1:
                cur.execute("SELECT code FROM stations_coo WHERE name=?", (arr_name,))
                code_pack = cur.fetchall()
                for code in code_pack:
                    code_arr = str(''.join(code)).lower()

                con.close()

                with sq.connect('db/users.db') as con:
                    cur = con.cursor()
                    cur.execute('''UPDATE users SET metro_arr=? WHERE user_id=?''', (code_arr, user_id))
                    con.commit()

            bot.send_message(chat_id=message.chat.id, text=consts.acc_create_conf_text)

        if stats_num_cur > 1:
            with open('metroways.png', 'rb') as img:
                way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_arr, arr_name)
    except:
        error_funcs.other_error(message)


def few_ways_st_arr(message, arr_name):
    try:
        way = int(message.text)
        user_id = message.from_user.id

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, arr_name))
            got = cur.fetchone()
            for i in got:
                if i > 0:
                    exists = True
                else:
                    exists = False

        if exists:
            with sq.connect('db/metro.db') as con:
                cur = con.cursor()
                cur.execute('''SELECT code FROM stations_coo WHERE name=? AND way=?''',
                            (arr_name, way))
                code_pack = cur.fetchall()
                for code in code_pack:
                    code_arr = str(''.join(code)).lower()
                con.close()

                with sq.connect('db/users.db') as con:
                    cur = con.cursor()
                    cur.execute('''UPDATE users SET metro_arr=? WHERE user_id=?''', (code_arr, user_id))
                    con.commit()

            bot.send_message(message.chat.id, text=consts.acc_create_conf_text)

        if not exists:
            error_funcs.no_station_on_way_found(message)
    except:
        error_funcs.other_error(message)


# Delete account
def del_confirm(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if message.content_type == 'text':
        decision = str(message.text).lower()
        if decision == 'да':
            try:
                remove_user(user_id)
                bot.send_message(chat_id, text=consts.acc_del_conf_text)
            except:
                error_funcs.other_error(message)
        elif decision == 'нет':
            bot.send_message(chat_id=message.chat.id, text=consts.do_not_delete_acc_text)
        else:
            error_funcs.other_error(message)
    else:
        error_funcs.not_text_error(message)


def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        con.commit()


def delete_account(message):
    try:
        chat_id = message.chat.id

        decision = bot.send_message(chat_id, text=consts.delete_acc_confirm_ask_text)
        bot.register_next_step_handler(decision, del_confirm)
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


# Edit account
def change_name(message):
    try:
        user_id = message.from_user.id
        new_name = str(message.text).lower()

        with sq.connect('db/users.db') as con:
            cur = con.cursor()
            cur.execute('''UPDATE users SET first_name=? WHERE user_id=?''', (new_name, user_id))
            con.commit()

        view_acc_func(message)
    except:
        error_funcs.other_error(message)


def change_mdep(message):
    try:
        new_dep_name = str(message.text).lower()
        user_id = message.from_user.id

        result = None

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT count(*) FROM stations_coo WHERE name=?''', (new_dep_name,))
            stats_num = cur.fetchone()[0]
            if stats_num == 0:
                error_funcs.no_station_found(message)
            elif stats_num == 1:
                cur.execute('SELECT code FROM stations_coo WHERE name=?', (new_dep_name,))
                new_dep_code = cur.fetchone()[0]
                result = True
            elif stats_num > 1:
                with open('metroways.png', 'rb') as img:
                    way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
                bot.register_next_step_handler(way_num, change_dep_few_stations, new_dep_name, user_id, message)

        if result:
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_dep=? WHERE user_id=?', (new_dep_code, user_id))
                con.commit()
            view_acc_func(message)
    except:
        error_funcs.other_error(message)


def change_dep_few_stations(way_num, stat_name, user_id, message):
    try:
        way = int(way_num.text)
        name = stat_name
        result = None

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('SELECT code FROM stations_coo WHERE way=? AND name=?', (way, name))
            new_dep_code = cur.fetchone()[0]
            result = True

        if result:
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_dep=? WHERE user_id=?', (new_dep_code, user_id))
                con.commit()
            view_acc_func(message)
    except:
        error_funcs.other_error(message)


def change_marr(message):
    try:
        new_arr_name = str(message.text).lower()
        user_id = message.from_user.id

        result = None

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT count(*) FROM stations_coo WHERE name=?''', (new_arr_name,))
            stats_num = cur.fetchone()[0]
            if stats_num == 0:
                error_funcs.no_station_found(message)
            elif stats_num == 1:
                cur.execute('SELECT code FROM stations_coo WHERE name=?', (new_arr_name,))
                new_arr_code = cur.fetchone()[0]
                result = True
            elif stats_num > 1:
                with open('metroways.png', 'rb') as img:
                    way_num = bot.send_photo(message.chat.id, photo=img, caption=consts.way_ask_text)
                bot.register_next_step_handler(way_num, change_arr_few_stations, new_arr_name, user_id, message)

        if result:
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_arr=? WHERE user_id=?', (new_arr_code, user_id))
                con.commit()
            view_acc_func(message)
    except:
        error_funcs.other_error(message)


def change_arr_few_stations(way_num, stat_name, user_id, message):
    try:
        way = int(way_num.text)
        name = stat_name

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('SELECT code FROM stations_coo WHERE way=? AND name=?', (way, name))
            new_arr_code = cur.fetchone()[0]
            result = True

        if result:
            with sq.connect('db/users.db') as con:
                cur = con.cursor()
                cur.execute('UPDATE users SET metro_arr=? WHERE user_id=?', (new_arr_code, user_id))
                con.commit()
            view_acc_func(message)
    except:
        error_funcs.other_error(message)


def ask_what_to_edit_step(message):
    chat_id = message.chat.id
    try:
        msg = bot.send_message(chat_id, 'Что вы хотите изменить? '
                                        '\n\nВозможные варианты ответа (без кавычек): "имя", "никнейм", "станция '
                                        'отправления", "станция прибытия"')
        bot.register_next_step_handler(msg, forward_to_func_step)
    except:
        error_funcs.other_error(message)


def forward_to_func_step(message):
    chat_id = message.chat.id

    try:
        if message.content_type == 'text':
            msg = str(message.text).lower()
            if msg == 'имя':
                new_name = bot.send_message(chat_id, text='Пришлите новое имя, которое нужно установить')
                bot.register_next_step_handler(new_name, change_name)

            elif msg == 'никнейм':
                bot.send_message(chat_id, text='Сейчас обновлю ваш ник из данных телеграма')
                new_nick = message.from_user.username
                user_id = message.from_user.id
                with sq.connect('db/users.db') as con:
                    cur = con.cursor()
                    cur.execute('''UPDATE users SET nickname=? WHERE user_id=?''', (new_nick, user_id))
                    con.commit()
                view_acc_func(message)

            elif msg == 'станция отправления':
                new_dep = bot.send_message(chat_id, 'Введите название новой станции отправления')
                bot.register_next_step_handler(new_dep, change_mdep)

            elif msg == 'станция прибытия':
                new_arr = bot.send_message(chat_id, 'Введите название новой станции прибытия')
                bot.register_next_step_handler(new_arr, change_marr)

        else:
            error_funcs.not_text_error(message)
    except:
        error_funcs.other_error(message)
