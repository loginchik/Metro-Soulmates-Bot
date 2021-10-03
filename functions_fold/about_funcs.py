import consts

bot = consts.bot


def about_func(message, markup):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=consts.about_text, reply_markup=markup)
