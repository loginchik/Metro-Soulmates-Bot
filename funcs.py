import sqlite3 as sq
import telebot
import random

# import globals
from consts import token
from consts import registration_status

# bot identify
bot = telebot.TeleBot(token)

# globals
reg_status = registration_status


def write_new_user(user_id, first_name, nickname, metro_dep, metro_arr):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('INSERT INTO users (user_id, first_name, nickname, metro_dep, metro_arr)'
                    'VALUES (?, ?, ?, ?, ?)', (user_id, first_name, nickname, metro_dep, metro_arr))


def check_reg(user_id):
    global reg_status
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT count(user_id) FROM users WHERE user_id=?", (user_id,))
        users_exist = cur.fetchall()
        # Get number of existing users with this user_id
        l = users_exist[0]
        m = ''.join(str(x) for x in l)
        m = int(m)
        if m > 0:
            reg_status = True
        if m == 0:
            reg_status = False


def prof_info(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user_info = cur.fetchall()

        # Unpack dict
        for key in user_info:
            us_f_name = key[2]
            us_nick = key[3]
            us_m_dep_code = key[4]
            us_m_arr_code = key[5]

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (us_m_dep_code,))
        for name in cur.fetchall():
            us_way_dep = name[0]
            us_m_dep = name[1]

        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (us_m_arr_code,))
        for name in cur.fetchall():
            us_way_arr = name[0]
            us_m_arr = name[1]

    text = "Имя — " + str(us_f_name).title() + '\n' + "Ник в телеграме — @" + str(us_nick) + \
           '\n\n' + "Метро отправленя: \n" + str(us_m_dep).title() + " (" + str(us_way_dep) + \
           " линия метро)\n" + '\n' + "Метро прибытия: \n" + str(us_m_arr).title() + " (" + str(us_way_arr) + \
           " линия метро)"
    return text


def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))


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

    l = list(range(0, souls_len))
    random.shuffle(l)
    m = []
    for item in l:
        if l.index(item) < 5:
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
        for i in soul_dep_pack:
            soul = int(i[0])
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
        if not soul in souls_arr:
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
    for soul in current_souls_package:
        soul_id = soul
        with sq.connect('db/users.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr FROM beta_users WHERE user_id=?''',
                        (soul_id,))
            soul_info = cur.fetchall()
        for i in soul_info:
            name = i[0]
            nick = i[1]
            dep = i[2]
            arr = i[3]

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()
            cur.execute('''SELECT way, name FROM stations_coo WHERE code=?''', (dep,))
            dep_pack = cur.fetchall()
            for i in dep_pack:
                dep_way = i[0]
                dep_st = i[1]
            cur.execute('''SELECT way, name FROM stations_coo WHERE code=?''', (arr,))
            arr_pack = cur.fetchall()
            for i in arr_pack:
                arr_way = i[0]
                arr_st = i[1]

        info = 'Имя вашего соула: ' + str(name).capitalize() + '\n' + \
               'Вы можете написать ему: @' + nick + '\n\n' + \
               'В своей анкете ' + str(name).capitalize() + \
               ' указывает, что отправляется со станции "' + str(dep_st).title() + '" (' + str(dep_way) + ' линия)' + \
               ' и ездит на станцию "' + str(arr_st).title() + '"' + ' (' + str(arr_way) + ' линия)'
        return info

# ------- the end of souls search funcs block -------
