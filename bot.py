import configparser
import os

from telebot.types import Message, InlineQuery

from src.data import Data, helpdesk
from src.sections.main_menu import MainMenuSection

# from src.sections.helpdesk import HelpdeskSection

from src.staff.updates import Updater
from src.sections.team_menu import TeamMenu


# from src.staff import utils

# from src.objects import quiz

from telebot import TeleBot, logger

config = configparser.ConfigParser()
config.read("Settings.ini")

API_TOKEN = (
    os.environ.get("TOKEN", False)
    if os.environ.get("TOKEN", False)
    else config["TG"]["token"]
)
CONNECTION_STRING = (
    os.environ.get("DB", False)
    if os.environ.get("DB", False)
    else config["Mongo"]["db"]
)

bot = TeleBot(API_TOKEN, parse_mode="HTML")
data = Data(conn_string=CONNECTION_STRING, bot=bot)

# main_menu_section = MainMenuSection(data=data)
team_section = TeamMenu(data=data)
# admin_section = AdminSection(data=data)
from src.sections.helpdesk import HelpdeskSection

helpdesk_section = HelpdeskSection(data=data)
main_menu_section = MainMenuSection(data=data)

updater = Updater(data=data)


@bot.message_handler(commands=["start"])
def start_bot(message: Message):

    try:
        user = updater.update_user_interaction_time(message)
        main_menu_section.send_start_menu(user)

    except Exception as e:
        print(f"Exception during start - {e}")
        bot.send_message(message.chat.id, text="Упс, щось пішло не так. Спробуй знову!")


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query: InlineQuery):

    try:
        helpdesk_section.send_inline_result(inline_query)
    except Exception as e:
        print(e)


@bot.message_handler(content_types=["text"])
def handle_text_buttons(message):
    user = updater.update_user_interaction_time(message)
    message_text = message.text

    try:
        if message_text in data.ebec.current_menu.buttons_list:
            if (
                data.ebec.current_menu.get_btn_by_name(message_text).special_action
                == "team_info"
            ):
                team_section.send_team_info_menu(user)
            else:
                main_menu_section.process_button(user, message_text)

        elif message_text == "__next_menu":
            data.ebec.switch_to_next_menu()
            main_menu_section.send_start_menu(user)            


    except Exception as e:
        print(e)


# @bot.callback_query_handler(func=lambda call: True)
# def handle_callback_query(call):
#     # TODO - check if messsage exists (it is not exist in answered inline query)
#     user = updater.update_user_interaction_time(call.message)
#     section = call.data.split(";")[0]

#     try:
#         if section == "Team":
#             team_section.process_callback(user, call)

#         elif section == "Admin":
#             admin_section.process_callback(user, call)

#         else:
#             bot.answer_callback_query(call.id)

#     except Exception as e:
#         print(e)


if __name__ == "__main__":
    updater.start_update_threads()
    # helpdesk.init_data()
    bot.polling(none_stop=True)