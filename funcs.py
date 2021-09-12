import consts

bot = consts.bot


def func_error(chat_id):
    bot.send_message(chat_id, text=consts.any_error_text)
