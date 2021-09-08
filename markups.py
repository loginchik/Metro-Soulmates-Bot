from telebot import types

# information buttons
help_button = types.KeyboardButton('/help')
about_button = types.KeyboardButton('/about')

# user account buttons
register_button = types.KeyboardButton('/register')
delete_ac_button = types.KeyboardButton('/delete_acc')
view_ac_button = types.KeyboardButton('/view_acc')
edit_ac_button = types.KeyboardButton('/edit_account')

# edit account buttons
change_name_button = types.KeyboardButton('/change_name')
change_dep_button = types.KeyboardButton('/change_dep_metro')
change_arr_button = types.KeyboardButton('/change_arr_metro')

# services buttons
review_button = types.KeyboardButton('/review')
search_button = types.KeyboardButton('/souls_search')

# help menu markup
help_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
help_markup.row(search_button)
help_markup.row(register_button, delete_ac_button, view_ac_button, edit_ac_button)
help_markup.row(about_button, review_button, help_button)

# edit account markup
edit_ac_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
edit_ac_markup.add(change_name_button, change_dep_button, change_arr_button)