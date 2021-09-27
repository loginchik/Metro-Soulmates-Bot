from consts import bot

faq_text = 'Если в файле не найдется ответ на ваш вопрос, можете адресоватьа его @loginchik'
file_name = 'FAQ.pdf'


def send_faq(message):
    chat_id = message.chat.id
    with open(file_name, 'rb') as file:
        bot.send_document(chat_id, data=file, caption=faq_text)
