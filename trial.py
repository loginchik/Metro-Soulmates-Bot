import sqlite3 as sq

import telebot

from consts import token

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

m_dep = '2_20'
m_arr = '5_6'

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


with sq.connect('db/metro.db') as con:
    cur = con.cursor()

    cur.execute('''SELECT way, number FROM stations_coo WHERE code=?''', (m_dep,))
    pack = cur.fetchall()
    way = get_way(pack)
    number = get_num(pack)

    cur.execute('''SELECT code FROM stations_coo WHERE way=? AND 
                                                (number BETWEEN ?-2 AND ?+2)''', (way, number, number))
    stat_pack = cur.fetchall()

souls = []
for i in stat_pack:
    station_num = i[0]
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT user_id FROM beta_users WHERE metro_dep=?''', (station_num,))
        soul_pack = cur.fetchmany(1)
        for i in soul_pack:
            soul = int(i[0])
            souls.append(soul)

soul_info = []

with sq.connect('db/users.db') as con:
    cur = con.cursor()

    for soul in souls:
        cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr FROM beta_users WHERE user_id=?''', (soul,))
        soul_info_pack = cur.fetchall()
        for i in soul_info_pack:
            name = i[0]
            nick = i[1]
            dep = i[2]
            arr = i[3]

        soul_info.append(name)
        soul_info.append(nick)
        soul_info.append(dep)
        soul_info.append(arr)

print(souls)
print(soul_info)
