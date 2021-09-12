import classes
import telebot

# consts
token = '1981840763:AAFZr6Dk58S_rpHLEX6wjxcqFA12Ys0rUmA'
not_working_commands = ['review', 'edit_account']

user = classes.User(None)
bot = telebot.TeleBot(token)

# texts
about_text = 'Этот бот предназначен для поиска соулмейта на метро. Работает только для вышкинцев (по крайней мере ' \
             'пока). '
help_text = '/register \n/about \n/delete_acc \n/view_acc \n/souls_search '
acc_create_conf_text = 'Ваш аккаунт успешно зарегистрирован. Чтобы посмотреть информацию вашего профиля, ' \
                       'воспользуйтесь функцией {0}'.format('/view_acc')
acc_del_conf_text = 'Ваш аккаунт успешно удален. Если захотите еще раз воспользоваться ботом, ' \
                    'не забудьте зарегистрироваться снова, запустив команду {0}'.format('/register')
acc_exists_text = 'Вы уже создавали профиль. Чтобы посмотреть информацию, ' \
                  'воспользуйтесь командой {0}'.format('/view_acc')
no_func_text = 'К сожалению, эта функция еще только разрабатывается'

mdep_ask_text = 'Метро отправления?'
way_ask_text = 'На какой ветке эта станция?'
marr_ask_text = 'Метро прибытия?'

no_station_error_text = 'Ошибка регистрации: станции с таким названием нет в базе данных.' \
                        '\n\nНачните регистрацию заново.'
no_registration_error_text = 'Ваш аккаунт не найден в базе данных, функция недоступна'

no_souls_found_text = "К сожалению, ваш соул еще не зарегистрировался"

any_error_text = 'К сожалению, произошла системная ошибка'

few_ways_no_station_text = 'Станция под таким названием не найдена на этом пути. ' \
                           'Процесс регистрации остановлен, попробуйте заново'
