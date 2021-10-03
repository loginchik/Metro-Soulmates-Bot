import consts

bot = consts.bot

first_help_text = '*Список команд*' \
                  '\n\n/help — техническая справка' \
                  '\n/about — информация о боте' \
                  '\n/faq — ответы на частые вопросы' \
                  '\n\n/register — регистрация нового пользователя' \
                  '\n/viewaccount — посмотреть информацию профиля' \
                  '\n/editaccount — изменить профиль' \
                  '\n/deleteaccount — удалить профиль' \
                  '\n\n/soulssearch — искать попутчиков' \
                  '\n/confirm — подтвердить встречу с попутчиком' \
                  '\n/untrusted — узнать количество неподтвержденных встреч, которые можно подтвердить' \
                  '\n/trustme — подтвердить встречу, о которой уведомляли не вы'
second_help_text = '*Вместо некоторых команд вы можете написать боту просто сообщение, и процесс запустится*' \
                   '\n\n«помощь» — вместо /help' \
                   '\nFAQ — вместо /faq' \
                   '\n\n«зарегистрироваться» — вместо /register' \
                   '\n«посмотреть профиль» — вместо /viewaccount' \
                   '\n«редактировать профиль» — вместо /editaccount' \
                   '\n«удалить профиль» — вместо /deleteaccount' \
                   '\n\n«найти попутчиков» — вместо /soulssearch' \
                   '\n«мы встретились» — вместо /confirm' \
                   '\n«подтвердить встречу» — вместо /trustme'


def help_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=first_help_text, parse_mode='MarkdownV2')
    bot.send_message(chat_id, text=second_help_text, parse_mode='MarkdownV2')
