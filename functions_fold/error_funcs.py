from consts import bot
import consts

error_sticker = 'CAACAgIAAxkBAAEC7YxhRlfXHvsef8cgeKq8wiEhRnGjKgACqg0AAuODiUjd0_CDy4ej6yAE'

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
    bot.send_sticker(chat_id, data=error_sticker)


def ununderstandable_text(message):
    text = consts.ununderstandable_text_text
    bot.reply_to(message, text)


def no_station_found(message):
    text = consts.no_station_error_text
    bot.reply_to(message, text)
    bot.send_sticker(message.chat.id, data=error_sticker)


def no_station_on_way_found(message):
    text = consts.few_ways_no_station_text
    bot.reply_to(message, text)
    bot.send_sticker(message.chat.id, data=error_sticker)


def not_nick_sent(message):
    text = consts.not_nick_text
    bot.reply_to(message, text)


def soul_not_registered(message):
    text = consts.soul_is_not_reg_text
    bot.reply_to(message, text)


def not_suitable_conf_format(message):
    text = consts.conf_not_suitable_format_text
    bot.reply_to(message, text)
