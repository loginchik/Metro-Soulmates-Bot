import random
import sqlite3 as sq
import telebot
from consts import token

from funcs import get_way, get_num

bot = telebot.TeleBot(token)

station_code = '5_20'

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

    stat_count = len(stat_pack)
    print(stat_count)

    if stat_count == 0:
        print('no')
    else:
        print('found')
