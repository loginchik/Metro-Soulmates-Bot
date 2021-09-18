import shutil
import sqlite3 as sq
from datetime import datetime

import classes
import consts
import funcs

bot = consts.bot


# Технические функции для обработки полученного от первого пользователя подтверждения встречи
def voice_processing(message, file_name):
    file_info = bot.get_file(message.voice.file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    shutil.move(file_name, 'confirms')


def photo_processing(message, file_name):
    file_info = bot.get_file(message.photo[-1].file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    shutil.move(file_name, 'confirms')


def video_note_processing(message, file_name):
    file_info = bot.get_file(message.video_note.file_id)

    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    shutil.move(file_name, 'confirms')


def write_conf(user_id, soul_id, date, file_name):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO confirms (user_id, soul_id, date, file) VALUES (?, ?, ?, ?)''',
                    (user_id, soul_id, date, file_name))


# Получение подтверждения от первого пользователя
conf = classes.Confirmation()


def start_conf_process(message):
    global conf
    conf.reset()

    chat_id = message.chat.id

    conf.user_id = int(message.from_user.id)

    msg = bot.send_message(chat_id, consts.ask_for_soul_nick)
    bot.register_next_step_handler(msg, get_soul_id)


def get_soul_id(message):
    global conf
    chat_id = message.chat.id

    got_soul_nick = str(message.text).lower()
    list_soul_nick = []
    for i in got_soul_nick:
        list_soul_nick.append(i)

    if list_soul_nick[0] == '@':
        del list_soul_nick[0]
        soul_nick = ''.join(list_soul_nick)
        with sq.connect('''db/users.db''') as con:
            cur = con.cursor()

            cur.execute('''SELECT user_id FROM users WHERE nickname=?''', (soul_nick,))
            soul_id_pack = cur.fetchall()
            if len(soul_id_pack) == 0:
                print('error')
            elif len(soul_id_pack) == 1:
                for i in soul_id_pack:
                    soul_id = i[0]
                conf.soul_id = soul_id
                msg = bot.send_message(chat_id, consts.ask_for_conf_text)
                bot.register_next_step_handler(msg, get_conf)
            else:
                funcs.func_error(message.chat.id)
    else:
        funcs.func_error(message.chat.id)


def get_conf(message):
    global conf
    content_type = message.content_type
    chat_id = message.chat.id

    if content_type == 'voice' or 'photo' or 'video_note':
        try:
            date = datetime.now()
            if content_type == 'voice':
                file_name = str(conf.user_id) + '_' + str(date) + '.ogg'
                voice_processing(message, file_name)
                conf.file_name = file_name
                write_conf(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)
                bot.send_message(chat_id, text=consts.conf_success_text)

            if content_type == 'photo':
                file_name = str(conf.user_id) + '_' + str(date) + '.png'
                photo_processing(message, file_name)
                conf.file_name = file_name
                write_conf(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)
                bot.send_message(chat_id, text=consts.conf_success_text)

            if content_type == 'video_note':
                file_name = str(conf.user_id) + '_' + str(date) + '.mp4'
                video_note_processing(message, file_name)
                conf.file_name = file_name
                write_conf(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)
                bot.send_message(chat_id, text=consts.conf_success_text)

            if content_type == 'text':
                bot.send_message(chat_id, 'это текст, а я прошу фото или видео или аудио')

        except:
            funcs.func_error(chat_id)


# Подтверждение встречи от другого пользователя, который не отправлял первоначальное подтверждение
def datetime_list(meet_date):
    date_list = meet_date.split()
    date_date = date_list[0]
    date_time = date_list[1]

    date_date_list = date_date.split('-')
    year = date_date_list[0]
    month = date_date_list[1]
    day = date_date_list[2]

    date_time_list = date_time.split(':')
    hour = date_time_list[0]
    minute = date_time_list[1]

    return [year, month, day, hour, minute]


def get_approval(message, user_id, soul_id, file_name):
    chat_id = message.chat.id

    approval = str(message.text).lower()

    if approval == 'да':
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute('''UPDATE confirms SET authorized=1 WHERE user_id=? AND soul_id=? AND file=?''',
                        (user_id, soul_id, file_name))
            con.commit()
        send_unapproved_num(message)

    elif approval == 'нет':
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute('''UPDATE confirms SET authorized=-1 WHERE user_id=? AND soul_id=? AND file=?''',
                        (user_id, soul_id, file_name))
        send_unapproved_num(message)
    else:
        funcs.func_error(chat_id)


def get_unapproved_num(message):
    user_id = message.from_user.id

    with sq.connect('db/users.db') as con:
        cur = con.cursor()

        cur.execute('''SELECT * FROM confirms WHERE soul_id=? AND authorized=0''', (user_id,))
        unapproved_pack = cur.fetchall()

    return len(unapproved_pack)


def send_unapproved_num(message):
    chat_id = message.chat.id
    unapproved_num = get_unapproved_num(message)
    if unapproved_num == 0:
        bot.send_message(chat_id, text=consts.no_unapproved_text)
    elif unapproved_num == 1:
        bot.send_message(chat_id, text='У вас 1 неподтвержденная встреча. Чтобы ее подтвердить, '
                                       'воспользуйтесь функцией /trust_me')
    elif unapproved_num in range(2, 4):
        bot.send_message(chat_id, text='У вас ' + str(unapproved_num) + ' неподтвержденных встречи. Чтобы их '
                                                                        'подтвердить, воспользуйтесь функцией '
                                                                        '/trust_me')
    elif unapproved_num > 4:
        bot.send_message(chat_id, text='У вас ' + str(unapproved_num) + ' неподтвержденных встреч. Чтобы их '
                                                                        'подтвердить, воспользуйтесь функцией '
                                                                        '/trust_me')
    else:
        funcs.func_error(message)


def approve_conf(message):
    unapproved_num = get_unapproved_num(message)
    soul_id = message.from_user.id
    chat_id = message.chat.id

    if unapproved_num > 0:
        with sq.connect('db/users.db') as con:
            cur = con.cursor()

            cur.execute('''SELECT * FROM confirms WHERE authorized=0 AND soul_id=?''', (soul_id,))
            meet_info = cur.fetchone()
            user_id = meet_info[0]
            soul_id = meet_info[1]
            date = meet_info[2]
            file_name = meet_info[3]

            cur.execute('''SELECT first_name, nickname FROM users WHERE user_id=?''', (user_id,))
            soul_name_nick_pack = cur.fetchone()
        user_name = soul_name_nick_pack[0]
        user_nick = soul_name_nick_pack[1]

        date_list = datetime_list(date)

        text = date_list[3] + '.' + date_list[2] + ' вы встречались с ' + str(user_name).title() + \
               ' (@' + str(user_nick).lower() + '). Если это так, пришлите "да" в ответ,  если это не так, ' \
                                                'то пришлите в ответ "нет".'

        approval = bot.send_message(chat_id, text=text)
        bot.register_next_step_handler(approval, get_approval, user_id, soul_id, file_name)
