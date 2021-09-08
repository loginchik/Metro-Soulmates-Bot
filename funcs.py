import sqlite3 as sq
import telebot

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


def prof_info(user_id, chat_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        user_info = cur.fetchall()

        # Unpack dict
        for key in user_info:
            us_id = key[1]
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

    bot.send_message(chat_id, text="Имя — " + str(us_f_name).title() +
                                   '\n' +
                                   "Ник в телеграме — @" + str(us_nick) +
                                   '\n\n' +
                                   "Метро отправленя: \n" + str(us_m_dep).title() +
                                   " (" + str(us_way_dep) + " линия метро)\n" +
                                   '\n' +
                                   "Метро прибытия: \n" + str(us_m_arr).title() + " (" + str(
        us_way_arr) + " линия метро)"
                     )


def remove_user(user_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))


def find_matches(way, num):
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT * FROM stations WHERE way=? AND station_number BETWEEN ?-5 AND ?+5''',
                    (way, num, num))
        for station in cur.fetchall():
            print(station)
