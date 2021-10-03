import logging

import telebot
from telebot import types

import classes

# consts
with open('token.txt', 'r') as tgtoken:
    token = str(tgtoken.read())

logger = logging.getLogger('TelebotExceptionHandler')


class MyExceptionHandler(telebot.ExceptionHandler):

    def handle(self, exception):
        logger.error("Error calling API", exception)
        return True


exception_handler = MyExceptionHandler
bot = telebot.TeleBot(token=token, exception_handler=exception_handler)
user = classes.User(None)

# texts
about_text = 'Metro Soulmates — это бот, разработанный небольшой командой студенток, которые хотели облегчить ' \
             'и разнообразить себе и другим таким же студентам жизнь. \n\nДля чего нужен бот? Ответ прост: чтобы ' \
             'искать попутчиков — таких же студентов — и ездить на учебу и с нее вместе.' \
             '\n\nИнстаграм проекта - @metro.soulmates'

# ------ Account functions ------

# account registration
acc_create_conf_text = 'Регистрация прошла успешно, теперь Вы можете полноценно пользоваться ботом!' \
                       '\n\n{0}\n{1}\n\n{2}\n{3}'.format('/help',
                                                         '/faq',
                                                         '/viewaccount',
                                                         '/soulssearch')

dep_ask_text = 'Как называется станция отправления?'
arr_ask_text = 'Как называется станция прибытия?'

few_stations_warning_first_text = 'Станция с таким названием есть на нескольких линиях. ' \
                                  'Сейчас я пришлю схему с номерами, цветами и названиями линий метро'
few_stations_warning_second_text = 'Если станция, которую Вы имеете в виду, находится на одной из линий ' \
                                   'метро, напишите номер этой линии (не название или цвет, а именно номер). ' \
                                   '\n\nЕсли станция находится на МДЦ 1, то напишите "МЦД 1"; ' \
                                   'если на МЦД 2 — "МЦД 2."'

acc_exists_text = 'Вы уже создавали профиль, повторная регистрация невозможна \n\n{0}\n{1}'.format('/viewaccount',
                                                                                                   '/help')

what_to_change_text = 'Что Вы хотите изменить? \n\nВозможные варианты ответа (без кавычек): ' \
                      '\n"{0}", \n"{1}", \n"{2}", \n"{3}"'.format('Имя',
                                                                  'Никнейм',
                                                                  'Станция отправления',
                                                                  'Станция прибытия')

nick_update_text = 'Сейчас обновлю Ваш ник из данных Вашего профиля в Телеграм'
new_name_text = 'Пожалуйста, напишите новое имя'
new_dep_text = 'Как называется новая станция отправления?'
new_arr_text = 'Как называется новая станция прибытия?'

# delete account
acc_del_conf_text = 'Ваш аккаунт успешно удален. Если захотите еще раз воспользоваться ботом, ' \
                    'не забудьте зарегистрироваться \n\n{0}'.format('/register')
goodbye_text = 'Надеемся, бот был для Вас полезен! \n\nЕсли у Вас есть какие-то комментарии , Вы можете написать ' \
               'разработчику (@loginchik) или в директ нашего инстаграма: metro.soulmates.'
do_not_delete_acc_text = 'Это хорошо, что Вы решили остаться. Аккаунт сохранен в базе пользователей'
delete_acc_confirm_ask_text = 'Вы уверены, что хотите удалить аккаунт? Восстановить данные будет невозможно' \
                              '\n\n- Да\n- Нет)'

# ------ Soulmates text ------

no_souls_found_text = "К сожалению, Ваш соул еще не зарегистрировался\n\n{0}\n{1}".format('/help', '/faq')

conf_success_text = 'Отчет о встрече успешно записан, спасибо большое!\n\n' \
                    'Чтобы и у Вас, и у Вашего соула появилась еще одна звездочка, попросите соула подтвердить ' \
                    'встречу со своей стороны с помощью команды /trustme. \n\n' \
                    'Если Вы еще раз захотите встретиться с тем же человеком, Вы можете записать еще один ' \
                    '(или два, или три, или больше) отчет — это не запрещено и, наоборот, порадует тех, ' \
                    'кто работает над проектом.'

ask_for_conf_text = 'Пожалуйста, пришлите доказательство. \n\nИм может быть аудио, видео или фото, ' \
                    'на котором слышно или видно Вас и Вашего соула (вы можете быть в масках, чтобы соблюдать ' \
                    'ковидные ограничения).'

ask_for_soul_nick = 'Пришлите ник того, с кем Вы встретились. Ник должен начинаться с @!'

no_unapproved_text = 'У Вас нет неподтвержденных встреч'

conf_not_suitable_format_text = 'Кажется, Вы прислали доказательство в неприемлемом формате (я могу принять только ' \
                                'аудио-сообщение, видео-сообщение или фотографию). Процесс остановился, ' \
                                'попробуйте запустить его заново.'

conf_reminder_text = 'Когда встретитесь со своим соулом, не забудьте отправить отчет, чтобы получить звездочки! ' \
                     '\n\n{0}'.format('/confirm')

# ------ Errors ------

no_func_text = 'К сожалению, команда еще разрабатывается и недоступна в данный момент'

no_station_error_text = 'Ошибка регистрации: станции с таким названием нет в базе данных.' \
                        '\n\nНачните регистрацию заново.'

no_registration_error_text = 'Ваш аккаунт не найден в базе данных, команда недоступна\n\n{0}\n'.format('/register'
                                                                                                       '/help')

not_text_text = 'В ответ ожидалось текстовое сообщение, а получено нечто иное. К сожалению, работа над командой ' \
                'прекратилась. Вы можете попробовать запустить ее заново'

ununderstandable_text_text = 'Не удалось распознать никакую команду. Возможно, вы требуете невозможного ' \
                             'или ошиблись в написании запроса'

any_error_text = 'К сожалению, произошла системная ошибка, процесс остановлен. Если у Вас такое происходит не в ' \
                 'первый раз, напишите разработчику — {0}'.format('@loginchik')

few_ways_no_station_text = 'Станция с таким названием не найдена на этом пути. ' \
                           'Процесс регистрации остановлен, попробуйте заново'

not_nick_text = 'Это не похоже на ник пользователя... Процесс остановлен, попробуйте заново'

soul_is_not_reg_text = 'Похоже, Ваш соул не зарегистрирован в боте. ' \
                       'Попросите его сделать это и попробуйте отправить отчет заново'

# ---- Stickers -----
sad_sticker = 'CAACAgIAAxkBAAEC7aBhRl4U7rzGDaMoAWDhP1f3AutOOgACaBEAAkAwiUtLxBKN7HrbtiAE'
error_sticker = 'CAACAgIAAxkBAAEC7YxhRlfXHvsef8cgeKq8wiEhRnGjKgACqg0AAuODiUjd0_CDy4ej6yAE'

# ----- Keyboard Markups -----

# Edit account buttons
edit_account_markup = types.ReplyKeyboardMarkup()
edit_account_markup.one_time_keyboard = True

edit_name_btn = types.KeyboardButton(text='Имя')
update_nickname_btn = types.KeyboardButton(text='Никнейм')
edit_dep_btn = types.KeyboardButton(text='Станция отправления')
edit_arr_btn = types.KeyboardButton(text='Станция прибытия')

edit_account_markup.row(edit_name_btn, update_nickname_btn)
edit_account_markup.row(edit_dep_btn, edit_arr_btn)

# New user markup
not_registered_markup = types.ReplyKeyboardMarkup()

register_btn = types.KeyboardButton(text='Регистрация')
help_btn = types.KeyboardButton(text='Помощь')
faq_btn = types.KeyboardButton(text='FAQ')

not_registered_markup.row(register_btn)
not_registered_markup.row(help_btn, faq_btn)

not_registered_markup.one_time_keyboard = True

# Basic markup

basic_markup = types.ReplyKeyboardMarkup()

viewaccount_btn = types.KeyboardButton(text='Посмотреть профиль')
editaccount_btn = types.KeyboardButton(text='Редактировать профиль')
searchsouls_btn = types.KeyboardButton(text='Найти соула')
confirm_btn = types.KeyboardButton(text='Мы встретились')
trustme_btn = types.KeyboardButton(text='Подтвердить встречу')
help_btn = types.KeyboardButton(text='Помощь')

basic_markup.row(help_btn, viewaccount_btn, editaccount_btn)
basic_markup.row(searchsouls_btn)
basic_markup.row(confirm_btn, trustme_btn)

basic_markup.one_time_keyboard = True

# Yes or no markup
yn_markup = types.ReplyKeyboardMarkup()

yes_btn = types.KeyboardButton(text='Да')
no_btn = types.KeyboardButton(text='Нет')

yn_markup.row(yes_btn, no_btn)
yn_markup.one_time_keyboard = True

# Choose way markup
ways_markup = types.ReplyKeyboardMarkup()

ways_markup.row('1', '2', '3', '4', '5', '6', '7', '8')
ways_markup.row('9', '10', '11', '12', '13', '14', '15')
ways_markup.row('МЦД 1', 'МЦД 2')

ways_markup.one_time_keyboard = True
