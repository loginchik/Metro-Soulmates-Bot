import random
import sqlite3 as sq
import telebot
from consts import token
import classes

from funcs import get_way, get_num

bot = telebot.TeleBot(token)

station_code = '5_20'


def prof_info(user_id):
    user = classes.User(user_id)
    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute("SELECT * FROM beta_users WHERE user_id=?", (user_id,))
        user_info = cur.fetchall()
        print(user_info)

        # Unpack dict
        for key in user_info:
            # us_f_name = key[2]
            us_nick = key[3]
            us_m_dep_code = key[4]
            us_m_arr_code = key[5]

            user.name = key[2]

            # user.add_name(key[2])

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('SELECT way, name FROM stations_coo WHERE code=?', (user.dep_code,))
        for name in cur.fetchall():
            user.dep_way = name[0]
            user.dep_name = name[1]

            # us_way_dep = name[0]
            # us_m_dep = name[1]

        con.cursor().execute('SELECT way, name FROM stations_coo WHERE code=?', (user.arr_code,))
        for name in con.cursor().fetchall():
            user.arr_way = name[0]
            user.arr_name = name[1]

            # us_way_arr = name[0]
            # us_m_arr = name[1]
    text = "Имя — " + str(user.name).title() + '\n' + "Ник в телеграме — @" + str(user.nickname) + \
           '\n\n' + "Метро отправленя: \n" + str(user.dep_name).title() + " (" + str(user.dep_way) + \
           " линия метро)\n" + '\n' + "Метро прибытия: \n" + str(user.arr_name).title() + \
           " (" + str(user.arr_way) + \
           " линия метро)"
    return text


inf = prof_info(972)
print(inf)
