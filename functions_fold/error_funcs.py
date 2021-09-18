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
