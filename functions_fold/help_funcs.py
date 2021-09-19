import consts

bot = consts.bot

first_help_text = 'Список команд' \
                  '\n\n/help — техническая справка' \
                  '\n/about — информация о боте' \
                  '\n/faq — ответы на частые вопросы' \
                  '\n\n/register — регистрация нового пользователя' \
                  '\n/view_account — посмотреть информацию профиля' \
                  '\n/edit_account — изменить профиль' \
                  '\n/delete_account — удалить профиль' \
                  '\n\n/souls_search — искать попутчиков' \
                  '\n/confirm — подтвердить встречу с попутчиком' \
                  '\n/untrusted — узнать количество неподтвержденных встреч, которые можно подтвердить' \
                  '\n/trust_me — подтвердить встречу, о которой уведомляли не вы'
second_help_text = 'Вместо некоторых команд вы можете написать боту просто сообщение, и процесс запустится:' \
                   '\n\n«помощь» — вместо /help' \
                   '\nFAQ — вместо /faq' \
                   '\n\n«зарегистрироваться» — вместо /register' \
                   '\n«посмотреть профиль» — вместо /view_account' \
                   '\n«редактировать профиль» — вместо /edit_account' \
                   '\n«удалить профиль» — вместо /delete_account' \
                   '\n\n«найти попутчиков» — вместо /search_souls' \
                   '\n«мы встретились» — вместо /confirm' \
                   '\n«подтвердить встречу» — вместо /trust_me'


def help_func(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, text=first_help_text)
    bot.send_message(chat_id, text=second_help_text)
