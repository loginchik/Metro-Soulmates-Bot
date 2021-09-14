import consts
from datetime import datetime
import shutil
import sqlite3 as sq
import funcs
import classes

bot = consts.bot


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


def write_stats(user_id, soul_id, date, file_name):
    with sq.connect('db/users.db') as con:
        cur = con.cursor()
        cur.execute('''INSERT INTO confirms (user_id, soul_id, date, file) VALUES (?, ?, ?, ?)''',
                    (user_id, soul_id, date, file_name))


conf = classes.Confirmation()


def start_conf_process(message):
    global conf
    conf.reset()
    print('start', conf.user_id, conf.soul_id, conf.file_name)

    chat_id = message.chat.id

    conf.user_id = int(message.from_user.id)
    print('us id', conf.user_id)

    msg = bot.send_message(chat_id, 'Пришлите ник того, с кем вы встретились')
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
                msg = bot.send_message(chat_id, 'доказательство?')
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
                write_stats(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)

            if content_type == 'photo':
                file_name = str(conf.user_id) + '_' + str(date) + '.png'
                photo_processing(message, file_name)
                conf.file_name = file_name
                write_stats(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)

            if content_type == 'video_note':
                file_name = str(conf.user_id) + '_' + str(date) + '.mp4'
                video_note_processing(message, file_name)
                conf.file_name = file_name
                write_stats(user_id=conf.user_id, soul_id=conf.soul_id, date=date, file_name=file_name)

            bot.send_message(chat_id, 'успешно')

        except:
            funcs.func_error(chat_id)

    if content_type == 'text':
        bot.send_message(chat_id, 'это текст, а я прошу фото или видео или аудио')
