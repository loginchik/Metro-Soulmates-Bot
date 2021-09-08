import sqlite3 as sq
import telebot
from consts import token
import random

bot = telebot.TeleBot(token)

with sq.connect('db/users.db') as con:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS beta_users (
                reg_number INTEGER PRIMARY KEY AUTOINCREMENT,      
                user_id INTEGER,
                first_name TEXT, 
                nickname TEXT, 
                metro_dep TEXT, 
                metro_arr TEXT
              )''')

"""
1. Получить базу станций отправления для поиска соулов
2. Получить базу пользователей, которые приезжают на ту же станцию
3. Получить базу пользователей, которые ездят с +-1 станции
4. Получить из базы их first_name, nickname, metro_dep, metro_arr
"""


def get_way(package):
    for i in package:
        w = i[0]
        return w


def get_num(package):
    for i in package:
        n = i[1]
        return n


# поиск станций, которые войдут в обработку
def find_stats(station_code):
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT way, number FROM stations_coo WHERE code=?''', (m_dep,))
        pack = cur.fetchall()
        way = get_way(pack)
        number = get_num(pack)

        cur.execute('''SELECT code FROM stations_coo WHERE way=? AND 
                                                    (number BETWEEN ?-2 AND ?+2)''', (way, number, number))
        stat_pack = cur.fetchall()
    return stat_pack


def get_random_for_souls(souls_all_package):
    souls_len = len(souls_all_package)

    l = list(range(0, souls_len))
    random.shuffle(l)
    m = []
    for item in l:
        if l.index(item) < 5:
            m.append(item)
    return m


def find_all_souls(stations_pack):
    stat_pack = stations_pack
    souls_all = []

    for i in stat_pack:
        station_num = i[0]
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT user_id FROM beta_users WHERE metro_dep=?''', (station_num,))
            soul_pack = cur.fetchall()

        for i in soul_pack:
            soul = int(i[0])
            souls_all.append(soul)

        return souls_all


def find_current_souls(souls_all_package):
    random_nums = get_random_for_souls(souls_all_package)
    cur_souls = []
    for soul in souls_all_package:
        if souls_all_package.index(soul) in random_nums:
            cur_souls.append(soul)
    return cur_souls


def get_soul_info(souls_package, number_one_to_five):
    soul_info = []

    if number_one_to_five == 1:
        num = 0
    elif number_one_to_five == 2:
        num = 1
    elif number_one_to_five == 3:
        num = 2
    elif number_one_to_five == 4:
        num = 3
    elif number_one_to_five == 5:
        num = 4
    else:
        print('error')

    print(num)

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        for soul in souls_package:
            cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr FROM beta_users WHERE user_id=?''',
                        (soul,))
            soul_info_pack = cur.fetchall()
            print(soul_info_pack)
            # for i in soul_info_pack:
            #     name = i[0]
            #     nick = i[1]
            #     dep = i[2]
            #     arr = i[3]
            #
            # soul_info.append(name)
            # soul_info.append(nick)
            # soul_info.append(dep)
            # soul_info.append(arr)

    return soul_info


m_dep = '2_20'

stats = find_stats(m_dep)
print('stats', stats)

all_souls = find_all_souls(stats)
print('all souls', all_souls)

cur_souls = find_current_souls(all_souls)
print('cur souls', cur_souls)
