import classes
import telebot
import logging

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
             'искать попутчиков — таких же студентов — и ездить на учебу и с нее вместе.'

acc_create_conf_text = 'Ваш аккаунт успешно зарегистрирован. Чтобы посмотреть информацию вашего профиля, ' \
                       'воспользуйтесь функцией /view_acc'
acc_del_conf_text = 'Ваш аккаунт успешно удален. Если захотите еще раз воспользоваться ботом, ' \
                    'не забудьте зарегистрироваться снова, запустив команду {0}'.format('/register')
acc_exists_text = 'Вы уже создавали профиль. Чтобы посмотреть информацию, ' \
                  'воспользуйтесь командой {0}'.format('/view_acc')
no_func_text = 'К сожалению, эта функция еще только разрабатывается'

mdep_ask_text = 'Метро отправления?'
way_ask_text = 'На какой ветке эта станция? Пожалуйста, укажите номер, а не название или цвет'
marr_ask_text = 'Метро прибытия?'

no_station_error_text = 'Ошибка регистрации: станции с таким названием нет в базе данных.' \
                        '\n\nНачните регистрацию заново.'
no_registration_error_text = 'Ваш аккаунт не найден в базе данных, функция недоступна'

no_souls_found_text = "К сожалению, ваш соул еще не зарегистрировался"

any_error_text = 'К сожалению, произошла системная ошибка'

few_ways_no_station_text = 'Станция под таким названием не найдена на этом пути. ' \
                           'Процесс регистрации остановлен, попробуйте заново'

conf_success_text = 'Успешно!'
ask_for_conf_text = 'Пришлите доказательство. \n\nИм может быть аудио, видео или фото, ' \
                    'на котором слышно или видно вас двоих'
ask_for_soul_nick = 'Пришлите ник того, с кем вы встретились. Ник должен начинаться с @!'
no_unapproved_text = 'У вас нет неподтвержденных встреч'

not_text_text = 'В ответ ожидалось текстовое сообщение, а получено нечто иное. К сожалению, функция прекратилась. ' \
                'Вы можете попробовать запустить ее заново'

ununderstandable_text_text = 'Не удалось распознать никакую команду. Возможно, вы требуете невозможного ' \
                             'или ошиблись в написании запроса'
