import funcs
import consts

user_1 = consts.user
bot = consts.bot


def souls_search_func(message):
    global user_1
    chat_id = message.chat.id

    if user_1.reg_status:
        stats = funcs.find_stats(user_1.dep_code)
        souls_exist_bool = funcs.check_souls_exist(stats)
        if souls_exist_bool:
            all_souls = funcs.find_all_souls(stats, user_1.arr_code, user_1.user_id)
            cur_souls = funcs.find_current_souls(all_souls)
            soul = funcs.get_soul_info(cur_souls)
            bot.send_message(chat_id, text=soul)
        else:
            bot.send_message(chat_id, text=consts.no_souls_found_text)
    if not user_1.reg_status:
        bot.send_message(chat_id, text=consts.no_registration_error_text)
