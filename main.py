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


@bot.message_handler(commands=not_working_commands)
def sorry_no(message):
    bot.send_message(message.chat.id, text=consts.no_func_text)


def listener(messages):
    for message in messages:
        chat_id = message.chat.id

        if message.content_type == 'text':
            new_msg = str(message.text).lower()

            if new_msg == '/help':
                help_funcs.help_func(message)
            if new_msg == '/about':
                about_funcs.about_func(message)
            if new_msg == '/register':
                account_funcs.checking_registration(message)
            if new_msg == '/delete_acc':
                account_funcs.delete_account(message)
            if new_msg == '/view_acc':
                account_funcs.view_acc_func(message)
            if new_msg == '/souls_search':
                soulmates_search_funcs.souls_search_func(message)

        if message.content_type == 'photo':
            bot.send_message(chat_id, 'Как жаль, что я не могу понять, что вы прислали')


bot.set_update_listener(listener)
bot.polling()