from consts import bot

faq_text = 'нет ответов, увы'


def send_faq(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, faq_text)
