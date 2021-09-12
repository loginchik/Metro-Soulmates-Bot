import consts
import classes
import sqlite3 as sq
import random

user_1 = consts.user
bot = consts.bot


# поиск станций отправления, которые войдут в обработку
def find_dep_stats(dep_station_code):
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        # получает код станции и определяет ее путь и номер
        cur.execute('''SELECT way, number FROM stations_coo WHERE code=?''', (dep_station_code,))
        pack = cur.fetchall()
        for i in pack:
            way = i[0]
            number = i[1]

        # определяет и запаковывает в список перечень подходящих станций
        cur.execute('''SELECT code FROM stations_coo WHERE way=? AND 
                                                    (number BETWEEN ?-2 AND ?+2)''', (way, number, number))
        stat_pack = cur.fetchall()
    return stat_pack


def find_dep_souls(stations_pack, user_id):
    stat_pack = stations_pack
    souls_dep = []

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
            if not soul == user_id:
                souls_dep.append(soul)
            else:
                pass

    return souls_dep


def find_arr_souls(arr_station_code, user_id):
    arr_code = arr_station_code
    souls_arr = []

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT user_id FROM beta_users WHERE metro_arr=?''', (arr_code,))
        soul_arr_pack = cur.fetchall()

    for i in soul_arr_pack:
        soul = int(i[0])
        if not soul == user_id:
            souls_arr.append(soul)
        else:
            pass

    return souls_arr


def find_matching_souls(souls_arr, souls_dep):
    arr_list = souls_arr
    dep_list = souls_dep

    matching_souls = []

    for i in arr_list:
        if i in dep_list:
            matching_souls.append(i)
        else:
            pass

    return matching_souls


def get_random_for_souls(souls_all_package):
    souls_len = len(souls_all_package)

    k = list(range(0, souls_len))
    random.shuffle(k)
    m = []
    for item in k:
        if k.index(item) < 5:
            m.append(item)
    return m


def find_current_souls(souls_all_package):
    random_nums = get_random_for_souls(souls_all_package)
    cur_souls = []
    for soul in souls_all_package:
        if souls_all_package.index(soul) in random_nums:
            cur_souls.append(soul)
    return cur_souls


def get_soul_info(soul_id):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr FROM beta_users WHERE user_id=?''', (soul_id,))
        info = cur.fetchall()

        soul = classes.User(soul_id)
        for i in info:
            soul.name = i[0]
            soul.nickname = i[1]
            soul.dep_code = i[2]
            soul.arr_code = i[3]

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT way, name FROM stations_coo WHERE code=?''', (soul.dep_code,))
        dep_pack = cur.fetchall()
        for i in dep_pack:
            soul.dep_way = i[0]
            soul.dep_name = i[1]

        cur.execute('''SELECT way, number FROM stations_coo WHERE code=?''', (soul.arr_code,))
        arr_pack = cur.fetchall()
        for i in arr_pack:
            soul.arr_way = i[0]
            soul.arr_name = i[1]

    return soul


def send_soul_info(soul_info_class, chat_id):
    soul = soul_info_class

    text = 'Имя: ' + str(soul.name).title() + \
           '\n\nНик: @' + str(soul.nickname) + \
           '\n\nСтанция отправления: ' + str(soul.dep_name).title() + \
           '\n\nСтанция прибытия: ' + str(soul.arr_name).title()
    bot.send_message(chat_id, text=text)


def main_find_souls(dep_code, arr_code, user_id, chat_id):
    dep_stat_pack = find_dep_stats(dep_station_code=dep_code)
    souls_dep = find_dep_souls(stations_pack=dep_stat_pack, user_id=user_id)
    souls_arr = find_arr_souls(arr_station_code=arr_code, user_id=user_id)
    all_souls_matching = find_matching_souls(souls_arr=souls_arr, souls_dep=souls_dep)
    current_souls = find_current_souls(souls_all_package=all_souls_matching)
    for soul in current_souls:
        soul_info = get_soul_info(soul)
        print(soul_info.name, soul_info.nickname, soul_info.dep_code, soul_info.arr_code)
        send_soul_info(soul_info, chat_id)


main_find_souls(dep_code='2_20', arr_code='7_11', user_id=73478274)
