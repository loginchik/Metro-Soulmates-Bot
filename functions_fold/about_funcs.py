import consts

bot = consts.bot


def about_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=consts.about_text)
