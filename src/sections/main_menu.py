from datetime import date

from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from src.data.user import Team
from src.sections.team_menu import TeamMenu
from ..data import User, Data, Ebec
from ..data.ebec import ReplyButton
from ..sections.section import Section
from ..staff.quiz import start_starting_quiz


class MainMenuSection(Section):
    def __init__(self, data: Data):
        super().__init__(data)

    @property
    def special_buttons(self):
        return {
            "time_left": self._b_time_left,
            "need_help": self._b_team_need_help,
        }

    def send_start_menu(self, user: User):

        if user.is_registered is False:
            self._register_user(user)
            return

        self.data.ebec.current_menu.send_menu(self.bot, user)

    def send_help(self, user: User, bot):
        markup = InlineKeyboardMarkup()

        url_button = InlineKeyboardButton(text="Допомога⁉️", url="https://telegra.ph/EBEC22-Help-02-10")
        markup.add(url_button)

        bot.send_photo(
            chat_id=user.chat_id,
            photo="https://i.ibb.co/J3nMcpJ/ebecPic.png",
            caption="Перейди по посиланню нижче, та отримай допогу🧡",
            reply_markup=markup,
        )  

    def process_button(self, user: User, btn_name: str):

        button = self.data.ebec.current_menu.get_btn_by_name(btn_name)

        if button.special_action is None:
            button.send_content(self.bot, user)

        else:
            self.special_buttons[button.special_action](user, button)

    def _register_user(self, user: User):
        self.bot.send_photo(
            user.chat_id,
            photo=self.data.ebec.start_photo,
            caption=self.data.ebec.start_text,
        )

        start_starting_quiz(user=user, bot=self.bot, final_func=self.send_start_menu)

    def _b_team_need_help(self, user: User, button: ReplyButton):
        admin_team: Team = self.data.admin_team

        if user.team is None:
            return

        if admin_team is None:
            return

        text = f"Команда потребує допомоги!"
        markup = InlineKeyboardMarkup()
        btn = InlineKeyboardButton(
            text=user.team.name,
            callback_data=self.form_admin_callback(
                action="TeamInfoMenu", team_id=user.team.id, new=True
            ),
        )
        markup.add(btn)
        for admin in admin_team.members:
            self.bot.send_message(admin.chat_id, text=text, reply_markup=markup)

        self.bot.send_message(
            user.chat_id, text="Зараз з вами зв'яжуться адміністратори!"
        )

    #################
    ## Informative
    #################

    def _b_time_left(self, user: User, button: ReplyButton):
        time_left = self.data.ebec.time_left

        if time_left is None:
            msg_text = "Ібек ще не розпочався"

        elif time_left.days < 0:
            msg_text = "Ібек закінчено!"

        else:
            hours = int(time_left.seconds / 3600)
            minutes = int(time_left.seconds % 3600 / 60)
            seconds = time_left.seconds % 60
            msg_text = (
                f"До кінця ібеку залишилось <b>{hours}год {minutes}хв {seconds}с</b>"
            )

        self.bot.send_message(chat_id=user.chat_id, text=msg_text)

    #################
    ## Registration
    #################
