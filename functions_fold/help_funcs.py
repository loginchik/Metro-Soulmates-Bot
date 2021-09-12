import consts

bot = consts.bot


def help_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=consts.help_text)
