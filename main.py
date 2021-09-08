import telebot
import sqlite3 as sq
import funcs

# globals import
from consts import token, registration_status, not_working_commands as error_commands
from markups import help_markup

# texts import
from consts import about_text

bot = telebot.TeleBot(token)

# globals
reg_status = registration_status
m_dep = ''
m_arr = ''
new_user_inf = {
    'user_id': '',
    'first_name': '',
    'nickname': '',
    'metro_dep': '',
    'metro_arr': ''
}
not_working_commands = error_commands

# Creating a table
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


@bot.message_handler(commands=['start', 'help'])
def help_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "В настоящее время бот умеет всего несколько вещей", reply_markup=help_markup)


@bot.message_handler(commands=['about'])
def about_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=about_text)


# Register user
@bot.message_handler(commands=['register'])
def checking_registration(message):
    global reg_status
    user_data = message.from_user
    user_id = user_data.id
    chat_id = message.chat.id
    funcs.check_reg(user_id)

    if reg_status:
        bot.send_message(chat_id, "Вы уже создавали профиль")
        print("повторная попытка регистрации")
        funcs.prof_info(user_id, chat_id)
    if not reg_status:
        get_basic(message)


def get_basic(message):
    global new_user_inf

    # getting information from user profile
    user_id = message.from_user.id
    name = str(message.from_user.first_name).lower()
    nick = str(message.from_user.username).lower()
    new_user_inf['user_id'] = user_id
    new_user_inf['first_name'] = name
    new_user_inf['nickname'] = nick

    # follow next step
    send = bot.send_message(message.chat.id, 'Метро отправления?')
    bot.register_next_step_handler(send, get_dep)


def get_dep(message):
    global new_user_inf
    global m_dep
    # saving metro dep
    mdep = str(message.text).lower()
    m_dep = mdep
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (mdep,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

        if stats_num_cur == 0:
            bot.send_message(message.chat.id,
                             'такой станции метро нет в базе. попробуйте начать регистрацию заново')
        if stats_num_cur == 1:
            cur.execute('''SELECT code FROM stations_coo WHERE name=?''', (mdep,))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_dep = str(''.join(code)).lower()
            new_user_inf['metro_dep'] = code_dep

            # follow next step
            send = bot.send_message(message.chat.id, "Метро прибытия?")
            bot.register_next_step_handler(send, get_arr)
        if stats_num_cur > 1:
            way_num = bot.send_message(message.chat.id, "пожалуйста введите номер линии")
            bot.register_next_step_handler(way_num, few_ways_st_dep)


def few_ways_st_dep(message):
    global m_dep
    global new_user_inf
    way = int(message.text)
    mdep = m_dep

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute("SELECT code FROM stations_coo WHERE name=? AND way=?", (mdep, way))
        code_pack = cur.fetchall()
        for code in code_pack:
            code_dep = str(''.join(code)).lower()
        new_user_inf['metro_dep'] = code_dep

        # follow next step
        send = bot.send_message(message.chat.id, "Метро прибытия?")
        bot.register_next_step_handler(send, get_arr)


def get_arr(message):
    global new_user_inf
    global m_arr

    # save metro arr
    marr = str(message.text).lower()
    m_arr = marr
    with sq.connect('db/metro.db') as con:
        cur = con.cursor()
        cur.execute('''SELECT count(code) as stats_here FROM stations_coo WHERE name=?''', (marr,))
        stats_here = cur.fetchall()
        for stats_num in stats_here:
            stats_num_cur = stats_num[0]

        if stats_num_cur == 0:
            bot.send_message(message.chat.id,
                             'такой станции метро нет в базе. попробуйте начать регистрацию заново')
        if stats_num_cur == 1:
            cur.execute("SELECT code FROM stations_coo WHERE name=?", (marr,))
            code_pack = cur.fetchall()
            for code in code_pack:
                code_arr = str(''.join(code)).lower()
            new_user_inf['metro_arr'] = code_arr
            funcs.write_new_user(user_id=new_user_inf['user_id'],
                                 first_name=new_user_inf['first_name'],
                                 nickname=new_user_inf['nickname'],
                                 metro_dep=new_user_inf['metro_dep'],
                                 metro_arr=new_user_inf['metro_arr']
                                 )
        if stats_num_cur > 1:
            way_num = bot.send_message(message.chat.id, "пожалуйста введите номер линии")
            bot.register_next_step_handler(way_num, few_ways_st_arr)


def few_ways_st_arr(message):
    global m_arr
    global new_user_inf
    way = int(message.text)
    marr = m_arr

    with sq.connect('db/metro.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT code FROM stations_coo WHERE name=? AND way=?''', (marr, way))
        code_pack = cur.fetchall()
        for code in code_pack:
            code_arr = str(''.join(code)).lower()
        new_user_inf['metro_arr'] = code_arr
        funcs.write_new_user(user_id=new_user_inf['user_id'],
                             first_name=new_user_inf['first_name'],
                             nickname=new_user_inf['nickname'],
                             metro_dep=new_user_inf['metro_dep'],
                             metro_arr=new_user_inf['metro_arr']
                             )
        bot.send_message(message.chat.id, "Ваш профиль успешно зарегистрироан.\n\n"
                                          "Чтобы посмотреть информацию о профиле, воспользуйтесь функцией /view_acc")


# Delete account
@bot.message_handler(commands=['delete_acc'])
def delete_account(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    funcs.remove_user(user_id)
    bot.send_message(chat_id, "Ваш аккаунт успешно удален")


# View account
@bot.message_handler(commands=['view_acc'])
def view_acc_func(message):
    funcs.prof_info(message.from_user.id, message.chat.id)


@bot.message_handler(commands=not_working_commands)
def sorry_no(message):
    bot.send_message(message.chat.id, "К сожалению, эта функция еще только разрабатывается :(")


bot.polling()
