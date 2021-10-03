import sqlite3 as sq

import classes
import consts
from functions_fold import about_funcs, account_funcs, help_funcs, soulmates_search_funcs, \
    confirmation_funcs, error_funcs, faq_funcs

bot = consts.bot
user = consts.user

# Create users db if not exists
with sq.connect('db/users.db') as con:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
        reg_number INTEGER PRIMARY KEY AUTOINCREMENT,      
        user_id INTEGER,
        first_name TEXT, 
        nickname TEXT, 
        metro_dep TEXT, 
        metro_arr TEXT,
        stars INTEGER DEFAULT 0
      )''')
    con.commit()

# Create confirms db if not exists
with sq.connect('db/users.db') as con:
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS confirms (
        user_id INTEGER,
        soul_id INTEGER,
        date TEXT,
        file TEXT,
        authorized INTEGER DEFAULT 0
        )''')


# Func gets current user info from db
def get_current_user(user_id):
    global user

    # Connect to db
    con = sq.connect('db/users.db')
    cur = con.cursor()

    # Count same user_id in db
    cur.execute('SELECT user_id FROM users WHERE user_id=?', (user_id,))
    pack = cur.fetchall()

    # Close connection
    con.close()

    pack_len = len(pack)

    # Change reg_status
    if pack_len == 0:
        user.reg_status = False

    elif pack_len > 0:
        user.reg_status = True

    # If registered, get info about the user
    if user.reg_status:

        # Connect to db
        con = sq.connect('db/users.db')
        cur = con.cursor()

        # Execute information
        cur.execute('SELECT SELECT first_name, nickname, metro_dep, metro_arr FROM users WHERE user_id=?', (user_id,))
        user_info = cur.fetchone()

        # Close connection
        con.close()

        # Load data into class
        user.name = user_info[0]
        user.nickname = user_info[1]
        user.dep_code = user_info[2]
        user.arr_code = user_info[3]

    else:
        pass

    return user


def listener(messages):
    for message in messages:

        # Save user's message data
        chat_id = message.chat.id
        user_id = message.chat.id

        if message.content_type == 'text':
            current_user = get_current_user(user_id)
            new_msg = str(message.text).lower()

            # Registration is not required
            if new_msg in ['/help', 'помощь', '/start']:
                help_funcs.help_func(message)
            elif new_msg == '/about':
                about_funcs.about_func(message)
            elif new_msg in ['/faq', 'faq']:
                faq_funcs.send_faq(message)

            # Not developed
            elif new_msg == '/report':
                error_funcs.no_func_error(message)
            elif new_msg == '/review':
                error_funcs.no_func_error(message)
            elif new_msg == '/mymeets':
                error_funcs.no_func_error(message)

            # Only without registration
            elif new_msg in ['/register', 'регистрация', 'зарегистрироваться']:
                if not current_user.reg_status:
                    account_funcs.get_basic_step(message)
                elif current_user.reg_status:
                    error_funcs.user_exists_error(message)

            # Only with registration
            elif new_msg in ['/viewaccount', 'посмотреть профиль']:
                if current_user.reg_status:
                    account_funcs.view_acc_func(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            elif new_msg in ['/editaccount', 'изменить аккаунт', 'редактировать профиль']:
                if current_user.reg_status:
                    account_funcs.ask_what_to_edit_step(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            elif new_msg in ['/deleteaccount', 'удалить профиль']:
                if current_user.reg_status:
                    account_funcs.delete_account(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            elif new_msg in ['/soulssearch', 'поиск попутчиков', 'искать попутчиков', 'найти попутчиков',
                             'найти соула', 'поиск соула', 'искать соула']:
                if current_user.reg_status:
                    soulmates_search_funcs.main_find_souls(message=message, user_class=user, user_id=user_id)
                else:
                    error_funcs.no_registration_error(message)

            elif new_msg in ['/confirm', 'мы встретились']:
                if current_user.reg_status:
                    confirmation_funcs.start_conf_process(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            elif new_msg == '/untrusted':
                if current_user.reg_status:
                    confirmation_funcs.send_unapproved_num(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            elif new_msg in ['/trustme', 'подтвердить встречу']:
                if current_user.reg_status:
                    confirmation_funcs.approve_conf(message)
                elif not current_user.reg_status:
                    error_funcs.no_registration_error(message)

            # Command is not recognized
            else:
                error_funcs.ununderstandable_text(message)

        # Content type != text
        elif message.content_type != 'text':
            bot.send_message(chat_id, 'Я не умею пока обрабатывать никакие входящие сообщения, кроме текстовых, '
                                      'только если я не прошу прислать мне такой файл.')


bot.set_update_listener(listener)
bot.polling(non_stop=True)
