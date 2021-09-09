import random
import sqlite3 as sq

import telebot

import classes
import consts

# bot identify
bot = telebot.TeleBot(consts.token)

soul_1 = classes.User(None)


def func_error(chat_id):
    bot.send_message(chat_id, text=consts.any_error_text)


def write_new_user(user_id, first_name, nickname, metro_dep, metro_arr):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('INSERT INTO users (user_id, first_name, nickname, metro_dep, metro_arr)'
                    'VALUES (?, ?, ?, ?, ?)', (user_id, first_name, nickname, metro_dep, metro_arr))
        con.commit()


def check_reg(user_id):
    reg_status = None
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


def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        con.commit()


# ------- souls search funcs block -------
# 2 funcs for station identification
def get_way(package):
    for i in package:
        w = i[0]
        return w


def get_num(package):
    for i in package:
        n = i[1]
        return n


# technical funcs
def get_random_for_souls(souls_all_package):
    souls_len = len(souls_all_package)

    k = list(range(0, souls_len))
    random.shuffle(k)
    m = []
    for item in k:
        if k.index(item) < 5:
            m.append(item)
    return m


# поиск станций отправления, которые войдут в обработку
def find_stats(station_code):
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        # получает код станции и определяет ее путь и номер
        cur.execute('''SELECT way, number FROM stations_coo WHERE code=?''', (station_code,))
        pack = cur.fetchall()
        way = get_way(pack)
        number = get_num(pack)

        # определяет и запаковывает в список перечень подходящих станций
        cur.execute('''SELECT code FROM stations_coo WHERE way=? AND 
                                                    (number BETWEEN ?-2 AND ?+2)''', (way, number, number))
        stat_pack = cur.fetchall()

    return stat_pack


def check_souls_exist(stat_pack):
    exists = None
    stat_count = len(stat_pack)
    if stat_count == 0:
        exists = False
    if stat_count > 0:
        exists = True
    return exists


def find_all_souls(stations_pack, code_arr, user_id):
    stat_pack = stations_pack
    souls_all = []
    souls_arr = []

    # поиск подходящих по станции отправления
    for i in stat_pack:
        station_num = i[0]
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT user_id FROM beta_users WHERE metro_dep=?''', (station_num,))
            soul_dep_pack = cur.fetchall()
        # упаковка подходящих по станции отправления в словарь souls_all
        for m in soul_dep_pack:
            soul = int(m[0])
            souls_all.append(soul)

    # исключение самого пользователя из списка соулов
    for i in souls_all:
        if i == user_id:
            del souls_all[souls_all.index(i)]
        else:
            pass

    # поиск подходящих по станции прибытия
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT user_id FROM beta_users WHERE metro_arr=?''', (code_arr,))
        soul_arr_pack = cur.fetchall()
    # упаковка подходящих по станции прибытия в словарь souls_arr
    for i in soul_arr_pack:
        soul = int(i[0])
        souls_arr.append(soul)

    # исключение не совпадающих по станции прибытия пользователей из словаря souls_all
    for soul in souls_all:
        if soul in souls_arr:
            pass
        if soul not in souls_arr:
            del souls_all[souls_all.index(soul)]
    return souls_all


def find_current_souls(souls_all_package):
    random_nums = get_random_for_souls(souls_all_package)
    cur_souls = []
    for soul in souls_all_package:
        if souls_all_package.index(soul) in random_nums:
            cur_souls.append(soul)
    return cur_souls


def get_soul_info(current_souls_package):
    global soul_1

    for soul in current_souls_package:
        soul_id = soul
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute(
                '''SELECT first_name, nickname, metro_dep, metro_arr FROM beta_users WHERE user_id=?''',
                (soul_id,))
            soul_info = con.cursor().fetchall()
        for i in soul_info:
            soul_1.name = i[0]
            soul_1.nickname = i[1]
            soul_1.dep_code = i[2]
            soul_1.arr_code = i[3]

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT way, name FROM stations_coo WHERE code=?''', (soul_1.dep_code,))
        dep_pack = cur.fetchall()
        for i in dep_pack:
            soul_1.dep_way = i[0]
            soul_1.dep_name = i[1]
        cur.execute('''SELECT way, name FROM stations_coo WHERE code=?''', (soul_1.arr_code,))
        arr_pack = cur.fetchall()
        for i in arr_pack:
            soul_1.arr_way = i[0]
            soul_1.arr_name = i[1]

    info = 'Имя вашего соула: ' + str(soul_1.name).capitalize() + '\n' + \
           'Вы можете написать ему: @' + str(soul_1.nickname) + '\n\n' + \
           'В своей анкете ' + str(soul_1.name).capitalize() + \
           ' указывает, что отправляется со станции "' + str(soul_1.dep_name).title() + '" (' + str(soul_1.dep_way) + \
           ' линия)' + \
           ' и ездит на станцию "' + str(soul_1.arr_name).title() + '"' + ' (' + str(soul_1.arr_way) + ' линия)'
    return info

# ------- the end of souls search funcs block -------
