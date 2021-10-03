import random
import sqlite3 as sq
import classes
import consts
from functions_fold import error_funcs

bot = consts.bot


def define_way_class(way_number):
    # Define ring starts and ends for each way

    # Ring is the way_5
    way_1 = classes.Way(ring_starts=6, ring_ends=13)
    way_2 = classes.Way(ring_starts=9, ring_ends=14)
    way_3 = classes.Way(ring_starts=3, ring_ends=15)
    way_4 = classes.Way(ring_starts=10, ring_ends=13)
    way_5 = classes.Way(ring_starts=1, ring_ends=12)
    way_6 = classes.Way(ring_starts=8, ring_ends=13)
    way_7 = classes.Way(ring_starts=10, ring_ends=14)

    # We have some problems here
    way_8 = classes.Way(ring_starts=1, ring_ends=20)

    way_9 = classes.Way(ring_starts=9, ring_ends=14)
    way_10 = classes.Way(ring_starts=9, ring_ends=11)

    # Here we also have some problems
    way_11 = classes.Way(ring_starts=1, ring_ends=11)

    way_12 = classes.Way(ring_starts=0, ring_ends=0)
    way_13 = classes.Way(ring_starts=1, ring_ends=5)
    way_14 = classes.Way(ring_starts=0, ring_ends=0)
    way_15 = classes.Way(ring_starts=0, ring_ends=0)

    # Ring is the first cross with metro station
    way_21 = classes.Way(ring_starts=7, ring_ends=15)
    way_22 = classes.Way(ring_starts=7, ring_ends=27)

    if way_number == 1:
        way_class = way_1
    elif way_number == 2:
        way_class = way_2
    elif way_number == 3:
        way_class = way_3
    elif way_number == 4:
        way_class = way_4
    elif way_number == 5:
        way_class = way_5
    elif way_number == 6:
        way_class = way_6
    elif way_number == 7:
        way_class = way_7
    elif way_number == 8:
        way_class = way_8
    elif way_number == 9:
        way_class = way_9
    elif way_number == 10:
        way_class = way_10
    elif way_number == 11:
        way_class = way_11
    elif way_number == 12:
        way_class = way_12
    elif way_number == 13:
        way_class = way_13
    elif way_number == 14:
        way_class = way_14
    elif way_number == 15:
        way_class = way_15
    elif way_number == 21:
        way_class = way_21
    elif way_number == 22:
        way_class = way_22

    return way_class


def is_station_in_ring(station_number, way_class):
    # Define ring range
    ring_range = list(range(way_class.ring_starts_at, way_class.ring_ends_at + 1))

    # Check if the station is inside the ring or not
    if station_number in ring_range:
        station_in_ring = True
    elif station_number not in ring_range:
        station_in_ring = False

    # Return station ring status
    return station_in_ring


# Func gets station's way and number on the way from db using unique code
# Return tuple
def get_way_number_from_code(code):
    # Connect to db
    con = sq.connect('db/metro.db')
    cur = con.cursor()

    # Execute data
    cur.execute('SELECT way, number FROM stations_coo WHERE code=?', (code,))
    package = cur.fetchone()

    # Close connection
    con.close()

    return package


# Func returns MDC name or metro way num if it's a metro
def get_way_name(way_number):
    if way_number < 20:
        way_name = way_number
        return way_name

    elif way_number == 21:
        way_name = 'МДЦ 1'
        return way_name

    elif way_number == 22:
        way_name = 'МДЦ 2'
        return way_name

    else:
        pass


# Func finds departure stations which are suitable for soulmates search process
# Return package with matching departure stations' codes
def find_dep_stats(dep_station_code):
    try:
        # Get way and number from unique code
        pack = get_way_number_from_code(dep_station_code)
        way = pack[0]
        number = pack[1]

        way_class = define_way_class(way)
        station_in_ring = is_station_in_ring(station_number=number, way_class=way_class)

        # Connect to db
        con = sq.connect('db/metro.db')
        cur = con.cursor()

        # Find and save matching stations
        # Select four nearest stations
        if station_in_ring:
            cur.execute('''SELECT code FROM stations_coo WHERE way=? AND (number BETWEEN ?-2 AND ?+2)''',
                        (way, number, number))
            stat_pack = cur.fetchall()

        # Select all stations outside the ring + nearest four
        elif not station_in_ring:
            if number < way_class.ring_starts_at:
                cur.execute('SELECT code FROM stations_coo WHERE way=? AND (number<? OR number BETWEEN ?-2 AND ?+2)',
                            (way, way_class.ring_starts_at, number, number))
                stat_pack = cur.fetchall()
            elif number > way_class.ring_ends_at:
                cur.execute('SELECT code FROM stations_coo WHERE way=? AND (number>? OR number BETWEEN ?-2 AND ?+2)',
                            (way, way_class.ring_ends_at, number, number))
                stat_pack = cur.fetchall()

        # Close connection
        con.close()

        # Return matching stations package [()]
        return stat_pack

    except:
        stat_pack = 'error'

    finally:
        return stat_pack


# Func finds all users with matching departure stations
def find_dep_souls(stations_pack, user_id):
    # Create empty dictionary to store potential souls' ids
    souls_matching_departure = []

    # Find potential souls process
    for station_code in stations_pack:
        station = station_code[0]

        # Connect to db
        con = sq.connect('db/users.db')
        cur = con.cursor()

        # Find potential souls and save into package
        cur.execute('''SELECT user_id FROM users WHERE metro_dep=?''', (station,))
        soul_dep_pack = cur.fetchall()

        # Close connection
        con.close()

        # Pack potential souls' ids into list
        for soul_id in soul_dep_pack:
            soul = int(soul_id[0])

            # Exclude self user from list
            if not soul == user_id:
                souls_matching_departure.append(soul)
            else:
                pass

    # Return a list of users matching by departure stations
    return souls_matching_departure


# Func finds all users with matching arrival station
def find_arr_souls(arr_station_code, user_id):
    # Create empty list to store potential souls
    souls_matching_arrival = []

    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Find matching users and save into package
    cur.execute('''SELECT user_id FROM users WHERE metro_arr=?''', (arr_station_code,))
    soul_arr_pack = cur.fetchall()

    # Close connection
    con.close()

    # Pack potential souls' ids into list
    for soul_id in soul_arr_pack:
        soul = int(soul_id[0])

        # Exclude self user from list
        if not soul == user_id:
            souls_matching_arrival.append(soul)
        else:
            pass

    # Return a list of users matching by arrival station
    return souls_matching_arrival


# Func merges departure and arrival souls to get truly matching soulmates
def find_matching_souls(souls_matching_departure, souls_matching_arrival):
    # Create empty list to store really matching soulmates
    matching_souls = []

    # Merge two lists
    for soul_id in souls_matching_arrival:
        if soul_id in souls_matching_departure:
            matching_souls.append(soul_id)
        else:
            pass

    # Return a list of truly matching souls' ids
    return matching_souls


# Func checks if soulmates exist
def check_souls_exist(all_soulmates_list):
    # Counts number of ids in list
    num = len(all_soulmates_list)

    # Defines exist variable
    if num == 0:
        exist = False
    elif num > 0:
        exist = True
    else:
        exist = 'error'

    return exist


# Func gets 5 random indexes
def get_random_indexes(souls_all_package):
    # Measure list of matching soulmates
    list_len = len(souls_all_package)

    # Create the list of suitable indexes
    indexes = list(range(0, list_len))

    # Shuffle indexes
    random.shuffle(indexes)

    # Create empty list to store 5 random indexes
    random_indexes = []

    # Select 5 first indexes from shuffled list
    for num in indexes:
        if indexes.index(num) < 5:
            random_indexes.append(num)
        else:
            pass

    # Return a list of 5 random indexes
    return random_indexes


# Func finds 5 random soulmates from all the soulmates matching
def find_current_souls(souls_all_package):
    # Get random indexes
    indexes = get_random_indexes(souls_all_package)

    # Create a list to store 5 random soulmates
    random_soulmates = []

    # Find souls by indexes
    for soul in souls_all_package:
        if souls_all_package.index(soul) in indexes:
            random_soulmates.append(soul)

    # Return a list of soulmates found this time
    return random_soulmates


# Func creates soul class and loads all info there
def get_soul_info(soul_id):
    # Create a class to store data
    soul = classes.User(soul_id)

    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Load data from db
    cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr, stars FROM users WHERE user_id=?''', (soul_id,))
    info_package = cur.fetchone()

    # Close connection
    con.close()

    # Unpack info package
    soul.name = info_package[0]
    soul.nickname = info_package[1]
    soul.dep_code = info_package[2]
    soul.arr_code = info_package[3]
    soul.stars = info_package[4]

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('SELECT name FROM stations_coo WHERE code=?', (soul.dep_code,))
        soul.dep_name = cur.fetchone()[0]

    # Get info about departure station
    dep_info = get_way_number_from_code(soul.dep_code)
    soul.dep_way = dep_info[0]
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('SELECT name FROM stations_coo WHERE code=?', (soul.dep_code,))
        soul.dep_name = cur.fetchone()[0]

    # Get info about arrival station
    arr_info = get_way_number_from_code(soul.arr_code)
    soul.arr_way = arr_info[0]
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('SELECT name FROM stations_coo WHERE code=?', (soul.arr_code,))
        soul.arr_name = cur.fetchone()[0]

    # Return soul class
    return soul


# Func sends soul info to user
def send_soul_info(soul_class, chat_id):
    dep_way_name = get_way_name(soul_class.dep_way)
    arr_way_name = get_way_name(soul_class.arr_way)

    # Generate text
    text = '{0}\n@{1}\n\n⭐: {2}\n\n🚇 Метро отправления:\n{3} ({4} линия)\n\n🚇 Метро прибытия:\n{5} ({6} линия)'.format(
        str(soul_class.name).title(),
        str(soul_class.nickname).lower(),
        str(soul_class.stars),
        str(soul_class.dep_name).title(),
        str(dep_way_name),
        str(soul_class.arr_name).title(),
        str(arr_way_name)
    )

    # Send text to user
    bot.send_message(chat_id, text=text)


# Func is main in soulmates search process
# It forwards to other functions
def main_find_souls(message, user_class, user_id):
    try:
        # Save user's message data
        chat_id = message.chat.id

        # Find matching stations for soulmates search process
        dep_stat_pack = find_dep_stats(dep_station_code=user_class.dep_code)

        # Work with errors
        if dep_stat_pack == 'error':
            error_funcs.other_error(message)

        # If no errors, continue process
        else:
            # Find users matching by departure stations
            souls_matching_departure = find_dep_souls(stations_pack=dep_stat_pack,
                                                      user_id=user_id)

            # Find users matching by arrival station
            souls_matching_arrival = find_arr_souls(arr_station_code=user_class.arr_code,
                                                    user_id=user_id)

            # Merge two lists to find truly matching souls
            all_souls_matching = find_matching_souls(souls_matching_departure=souls_matching_departure,
                                                     souls_matching_arrival=souls_matching_arrival)

            # Check if soulmates exist
            exist = check_souls_exist(all_souls_matching)

            # Continue searching process
            if exist:

                # Find 5 random soulmates
                soulmates = find_current_souls(all_souls_matching)

                # Send info about each
                for soul in soulmates:
                    soul_info = get_soul_info(soul_id=soul)
                    send_soul_info(soul_info, chat_id)

            # Send notification that no souls are found
            elif not exist:
                bot.send_message(chat_id, text=consts.no_souls_found_text)
                bot.send_sticker(chat_id, data=consts.sad_sticker)

            # Work with errors
            elif exist == 'error':
                error_funcs.other_error(message)

    except:
        error_funcs.other_error(message)
