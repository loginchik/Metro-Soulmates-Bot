from consts import bot
import consts


def not_text_error(message):
    chat_id = message.chat.id
    text = consts.not_text_text
    bot.send_message(chat_id, text)


def other_error(message):
    chat_id = message.chat.id
    text = consts.any_error_text
    bot.send_message(chat_id, text)


def no_registration_error(message):
    chat_id = message.chat.id
    text = consts.no_registration_error_text
    bot.send_message(chat_id, text)


def user_exists_error(message):
    chat_id = message.chat.id
    text = consts.acc_exists_text
    bot.send_message(chat_id, text)


def no_func_error(message):
    chat_id = message.chat.id
    text = consts.no_func_text
    bot.send_message(chat_id, text)
