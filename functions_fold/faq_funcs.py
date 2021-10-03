from consts import bot

faq_text = 'Все часто задаваемые вопросы собраны для удобства собраны в одном файле, и сейчас я его пришлю. ' \
           'Если в файле не найдется ответ на ваш вопрос, можете адресовать его @loginchik'
file_name = 'FAQ.pdf'


def send_faq(message, markup):
    chat_id = message.chat.id
    bot.send_message(chat_id, faq_text)
    with open(file_name, 'rb') as file:
        bot.send_document(chat_id, data=file, reply_markup=markup)
