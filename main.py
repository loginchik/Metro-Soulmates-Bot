import sqlite3 as sq
import consts

from functions_fold import about_funcs, account_funcs, help_funcs, soulmates_search_funcs

bot = consts.bot
user_1 = consts.user

not_working_commands = consts.not_working_commands

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


def get_curr_user_1(user_id):
    global user_1

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT user_id FROM users WHERE user_id=?''', (user_id,))
        pack = cur.fetchall()
        print(len(pack))

        if len(pack) == 0:
            user_1.reg_status = False

        if len(pack) > 0:
            user_1.reg_status = True

            cur.execute('''SELECT first_name, nickname, metro_dep, metro_arr FROM users WHERE user_id=?''', (user_id,))
            pack = cur.fetchall()
            for i in pack:
                user_1.name = i[0]
                user_1.nickname = i[1]
                user_1.dep_code = i[2]
                user_1.arr_code = i[3]


@bot.message_handler(commands=not_working_commands)
def sorry_no(message):
    bot.send_message(message.chat.id, text=consts.no_func_text)


def listener(messages):
    for message in messages:
        chat_id = message.chat.id
        user_id = message.chat.id

        if message.content_type == 'text':
            new_msg = str(message.text).lower()

            if new_msg == '/help':
                help_funcs.help_func(message)
            if new_msg == '/about':
                about_funcs.about_func(message)
            if new_msg == '/register':
                get_curr_user_1(user_id)
                account_funcs.checking_registration(message)
            if new_msg == '/delete_acc':
                get_curr_user_1(user_id)
                account_funcs.delete_account(message)
            if new_msg == '/view_acc':
                get_curr_user_1(user_id)
                account_funcs.view_acc_func(message)
            if new_msg == '/souls_search':
                get_curr_user_1(user_id)
                soulmates_search_funcs.souls_search_func(message)

        if message.content_type == 'photo':
            bot.send_message(chat_id, 'Как жаль, что я не могу понять, что вы прислали')


bot.set_update_listener(listener)
bot.polling()
