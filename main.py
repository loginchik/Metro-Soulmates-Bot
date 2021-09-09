import sqlite3 as sq
import telebot
import classes
import consts
import funcs

bot = telebot.TeleBot(consts.token)

not_working_commands = consts.not_working_commands
user_1 = classes.User(None)

# Creating a users table if not exists
with sq.connect('db/users.db') as con:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        reg_number INTEGER PRIMARY KEY AUTOINCREMENT,      
        user_id INTEGER,
        first_name TEXT, 
        nickname TEXT, 
        metro_dep TEXT, 
        metro_arr TEXT
      )''')
    con.commit()


@bot.message_handler(commands=['start', 'help'])
def help_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=consts.help_text)


@bot.message_handler(commands=['about'])
def about_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=consts.about_text)


# Register user
@bot.message_handler(commands=['register'])
def checking_registration(message):
    global user_1
    chat_id = message.chat.id

    if user_1.reg_status:
        bot.send_message(chat_id, text=consts.acc_exists_text)
        funcs.prof_info(user_1.user_id)
    else:
        user_1.user_id = int(message.from_user.id)
        user_1.name = str(message.from_user.first_name).lower()
        user_1.nickname = str(message.from_user.username).lower()

        # follow next step
        send = bot.send_message(message.chat.id, text=consts.mdep_ask_text)
        bot.register_next_step_handler(send, get_dep)


def get_dep(message):
    global user_1

    # saving metro dep
    user_1.dep_name = str(message.text).lower()

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (user_1.dep_name,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

        if stats_num_cur == 0:
            bot.send_message(message.chat.id, text=consts.no_station_error_text)
        if stats_num_cur == 1:
            cur.execute('''SELECT code FROM stations_coo WHERE name=?''', (user_1.dep_name,))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_dep = str(''.join(code)).lower()
            user_1.dep_code = code_dep

            # follow next step
            send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
            bot.register_next_step_handler(send, get_arr)
        if stats_num_cur > 1:
            way_num = bot.send_message(message.chat.id, text=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_dep)


def few_ways_st_dep(message):
    global user_1

    way = int(message.text)

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, user_1.dep_name))
        got = cur.fetchone()
        for i in got:
            print(i)
            if i > 0:
                exists = True
            else:
                exists = False

    if exists:
        user_1.dep_way = way

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()

            cur.execute("SELECT code FROM stations_coo WHERE name=? AND way=?", (user_1.dep_name, user_1.dep_way))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_dep = str(''.join(code)).lower()
            user_1.dep_code = code_dep

            # follow next step
            send = bot.send_message(message.chat.id, text=consts.marr_ask_text)
            bot.register_next_step_handler(send, get_arr)

    if not exists:
        bot.send_message(message.chat.id, text=consts.few_ways_no_station_text)


def get_arr(message):
    global user_1

    # save metro arr
    user_1.arr_name = str(message.text).lower()

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (user_1.arr_name,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

        if stats_num_cur == 0:
            bot.send_message(message.chat.id, text=consts.no_station_error_text)
        if stats_num_cur == 1:
            cur.execute("SELECT code FROM stations_coo WHERE name=?", (user_1.arr_name,))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_arr = str(''.join(code)).lower()
            user_1.arr_code = code_arr
            funcs.write_new_user(user_id=user_1.user_id,
                                 first_name=user_1.name,
                                 nickname=user_1.nickname,
                                 metro_dep=user_1.dep_code,
                                 metro_arr=user_1.arr_code
                                 )
        if stats_num_cur > 1:
            way_num = bot.send_message(message.chat.id, text=consts.way_ask_text)
            bot.register_next_step_handler(way_num, few_ways_st_arr)


def few_ways_st_arr(message):
    global user_1

    way = int(message.text)

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT count(*) FROM stations_coo WHERE way=? AND name=?''', (way, user_1.arr_name))
        got = cur.fetchone()
        for i in got:
            if i > 0:
                exists = True
            else:
                exists = False

    if exists:
        user_1.arr_way = way

        with sq.connect('db/metro.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT code FROM stations_coo WHERE name=? AND way=?''', (user_1.arr_name, user_1.arr_way))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_arr = str(''.join(code)).lower()
            user_1.arr_code = code_arr
        funcs.write_new_user(user_id=user_1.user_id,
                             first_name=user_1.name,
                             nickname=user_1.nickname,
                             metro_dep=user_1.dep_code,
                             metro_arr=user_1.arr_code
                             )
        user_1.reg_status = True
        bot.send_message(message.chat.id, text=consts.acc_create_conf_text)

    if not exists:
        bot.send_message(message.chat.id, text=consts.few_ways_no_station_text)


# Delete account
@bot.message_handler(commands=['delete_acc'])
def delete_account(message):
    global user_1
    chat_id = message.chat.id

    if not user_1.reg_status:
        bot.send_message(chat_id, text=consts.no_registration_error_text)
    if user_1.reg_status:
        funcs.remove_user(user_1.user_id)
        bot.send_message(chat_id, consts.acc_del_conf_text)
        user_1.delete_account()


# View account
@bot.message_handler(commands=['view_acc'])
def view_acc_func(message):
    global user_1

    if user_1.reg_status:
        text = funcs.prof_info(message.from_user.id)
        bot.send_message(message.chat.id, text=text)
    if not user_1.reg_status:
        bot.send_message(message.chat.id, text=consts.no_registration_error_text)


# Search for souls
@bot.message_handler(commands=['souls_search'])
def souls_search_func(message):
    global user_1
    chat_id = message.chat.id

    if user_1.reg_status:
        stats = funcs.find_stats(user_1.dep_code)
        souls_exist_bool = funcs.check_souls_exist(stats)
        if souls_exist_bool:
            all_souls = funcs.find_all_souls(stats, user_1.arr_code, user_1.user_id)
            cur_souls = funcs.find_current_souls(all_souls)
            soul = funcs.get_soul_info(cur_souls)
            bot.send_message(chat_id, text=soul)
        else:
            bot.send_message(chat_id, text=consts.no_souls_found_text)
    if not user_1.reg_status:
        bot.send_message(chat_id, text=consts.no_registration_error_text)


@bot.message_handler(commands=not_working_commands)
def sorry_no(message):
    bot.send_message(message.chat.id, text=consts.no_func_text)


bot.polling()
