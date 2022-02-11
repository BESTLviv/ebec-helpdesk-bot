from datetime import date, datetime, timedelta
from typing import Union

import mongoengine as me
from telebot import TeleBot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
)

from .user import User

DEFAULT_TEXT = (
    "Привіт! Я розкажу тобі більше про EBEC 2022, та допоможу зареєструватися"
)
DEFAULT_PHOTO = "https://ibb.co/rvSM6tr"


class ReplyButton(me.EmbeddedDocument):
    name = me.StringField()
    text = me.StringField(default=DEFAULT_TEXT)
    photo = me.StringField(default=DEFAULT_PHOTO)
    url_link = me.StringField(default=None)
    url_text = me.StringField(default=None)
    special_action = me.StringField(default=None)

    def send_content(self, bot: TeleBot, user: User):
        if self.special_action:
            print(f"Кнопка {self.name} не проста!")
            return

        # if content have link button
        markup = InlineKeyboardMarkup()

        if self.url_link:
            url_button = InlineKeyboardButton(text=self.url_text, url=self.url_link)
            markup.add(url_button)

        if self.photo:
            bot.send_photo(
                chat_id=user.chat_id,
                photo=self.photo,
                caption=self.text,
                reply_markup=markup,
            )
            return

        if self.text:
            bot.send_message(
                chat_id=user.chat_id,
                text=self.text,
                reply_markup=markup,
            )


class EbecMenu(me.Document):
    name = me.StringField(
        required=True,
        choices=[
            "informative",
            "registration",
            "selection",
            "after_selection",
            "project",
            "after_project",
        ],
    )
    menu_text = me.StringField(required=True, default=DEFAULT_TEXT)
    menu_photo = me.StringField(default=DEFAULT_PHOTO)
    columns_number = me.IntField(default=2)
    menu_buttons = me.ListField(me.EmbeddedDocumentField("ReplyButton"), default=list())
    start_date = me.DateField(required=True)
    end_date = me.DateField(required=True)

    @property
    def buttons_list(self):
        return [btn.name for btn in self.menu_buttons]

    @property
    def markup(self) -> InlineKeyboardMarkup:
        markup = ReplyKeyboardMarkup()

        for btn_row in self._reply_keyboard_columns_generator():
            markup.add(*btn_row)

        return markup

    def update_from_db(self):
        return EbecMenu.objects.filter(name=self.name).first()

    def send_menu(self, bot: TeleBot, user: User) -> Message:

        if self.menu_photo is None:
            return bot.send_message(
                user.chat_id, self.menu_text, reply_markup=self.markup
            )

        else:
            return bot.send_photo(
                user.chat_id,
                photo=self.menu_photo,
                caption=self.menu_text,
                reply_markup=self.markup,
            )

    def _reply_keyboard_columns_generator(self):
        row = []

        for index, btn in enumerate(self.menu_buttons, 1):
            row += [KeyboardButton(btn.name)]

            if index % self.columns_number == 0:
                yield row
                row = []

        if row:
            yield row

    def get_btn_by_name(self, btn_name: str) -> ReplyButton:
        for btn in self.menu_buttons:
            if btn.name == btn_name:
                return btn


class Ebec(me.Document):
    # cv_archive_file_id_list = me.ListField(default=None)
    # cv_archive_last_update = me.DateTimeField(default=None)
    # cv_archive_size = me.IntField(default=0)
    start_text = me.StringField(default=None)
    start_photo = me.StringField(default=None)

    current_menu: EbecMenu = me.ReferenceField(EbecMenu)
    project_start_datetime: datetime = me.DateTimeField(default=None)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)

        self.MENU_LIST = [
            self.p_informative_menu,
            self.p_registration_menu,
            self.p_selection_menu,
            self.p_after_selection_menu,
            self.p_project_menu,
            self.p_after_project_menu,
        ]

    @property
    def p_informative_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="informative").first()

    @property
    def p_registration_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="registration").first()

    @property
    def p_selection_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="selection").first()

    @property
    def p_after_selection_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="after_selection").first()

    @property
    def p_project_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="project").first()

    @property
    def p_after_project_menu(self) -> EbecMenu:
        return EbecMenu.objects.filter(name="after_project").first()

    @property
    def time_left(self) -> Union[timedelta, None]:
        if self.project_start_datetime is None:
            return None

        expected_end_time = self.project_start_datetime + timedelta(days=1)
        return expected_end_time - datetime.now()

    @property
    def is_ongoing(self) -> bool:
        if self.project_start_datetime is None:
            return False

        expected_end_time = self.project_start_datetime + timedelta(days=1)
        return expected_end_time > datetime.now()

    def switch_to_next_menu(self):
        current_index = self.MENU_LIST.index(self.current_menu)
        next_index = current_index + 1

        if next_index == len(self.MENU_LIST):
            # return
            print("Знову найперше меню")
            next_index = 0

        self.current_menu = self.MENU_LIST[next_index]
        self.save()
        print(f"Menu switched to {self.current_menu.name}")

    def silent_refresh_menu_data(self):
        updated_menu = self.current_menu.update_from_db()

        current_index = self.MENU_LIST.index(self.current_menu)
        self.MENU_LIST[current_index] = updated_menu

        self.current_menu = updated_menu
        self.save()

        # for user in users:
        #    temp_msg = self.current_menu.send_menu(bot, user)
        #    bot.delete_message(user.chat_id, temp_msg.message_id)


def add_test_data():
    menu_informative = EbecMenu(
        name="informative",
        start_date=date.today(),
        end_date=date(2022, 1, 19),
        menu_buttons=list(),
    )
    menu_informative.menu_buttons = [
        ReplyButton(name="Інфа про Ібек"),
        ReplyButton(name="Інфа про бест"),
        ReplyButton(
            name="Реєстрація на ібек",
            text="Реєстрація на ібек розпочнеться {date}",
            photo=None,
            special_action="time_till_start",
        ),
        ReplyButton(name="Чат для людей без команди"),
        ReplyButton(name="Тестове завдання"),
    ]
    menu_informative.save()

    menu_registration = EbecMenu(
        name="registration",
        menu_text="",
        menu_photo="https://i.ibb.co/SrMZVJp/welcome-Pic.png",
        start_date=date(2022, 1, 19),
        end_date=date(2022, 2, 12),
        menu_buttons=[
            ReplyButton(name="Моя команда", special_action="team_info"),
            ReplyButton(
                name="Правила EBEC",
                text="Перейди по посиланню нижче, та ознайомся з нашими правилами 📜",
                photo="https://i.ibb.co/9pvcBkM/rulesPic.png",
                url_link="https://telegra.ph/EBEC-General-Rules-02-10",
                url_text="Правила 📜",
            ),
            ReplyButton(
                name="Розклад",
                text="Розклад стане доступним ближче до початку змагань",
                photo="https://i.ibb.co/xfZQKxH/schedule-Not-Ready-Pic.png",
            ),
            ReplyButton(
                name="Чат для людей без команди",
                text="Чат буде доступний згодом",
                photo="https://i.ibb.co/xfZQKxH/schedule-Not-Ready-Pic.png",
            ),
            ReplyButton(
                name="Тестове завдання",
                text="Тестове завдання стане доступним ближче до початку змагань",
                photo="https://i.ibb.co/cc30H9v/test-Task-Pic.png ",
            ),
        ],
    )
    menu_registration.save()

    menu_selection = EbecMenu(
        name="selection",
        start_date=date(2022, 2, 12),
        end_date=date(2022, 2, 20),
        menu_buttons=[
            ReplyButton(name="Інформація про команду"),
            ReplyButton(name="Компанії"),
            ReplyButton(name="Розклад"),
            ReplyButton(name="Тестове завдання"),
        ],
    )
    menu_selection.save()

    menu_after_selection = EbecMenu(
        name="after_selection",
        start_date=date(2022, 2, 20),
        end_date=date(2022, 2, 26),
        menu_buttons=[
            ReplyButton(name="Інформація про команду"),
            ReplyButton(name="Розклад"),
            ReplyButton(name="Форма з орг питаннями"),
            ReplyButton(name="Компанії"),
            ReplyButton(name="Інформація про проєкт"),
            ReplyButton(name="Здати CV"),
        ],
    )
    menu_after_selection.save()

    menu_project = EbecMenu(
        name="project",
        start_date=date(2022, 2, 26),
        end_date=date(2022, 2, 28),
        menu_buttons=[
            ReplyButton(name="Час"),
            ReplyButton(name="Потрібна допомога"),
            ReplyButton(name="Організатори"),
            ReplyButton(name="Розклад"),
            ReplyButton(name="Компанії"),
            ReplyButton(name="Здати CV"),
        ],
    )
    menu_project.save()

    menu_after_project = EbecMenu(
        name="after_project",
        start_date=date(2022, 2, 28),
        end_date=date(2022, 2, 28),
        menu_buttons=[
            ReplyButton(name="Нас підтримують"),
            ReplyButton(name="Переможці"),
            ReplyButton(name="Фідбек форма"),
        ],
    )
    menu_after_project.save()

    ebec = Ebec(
        current_menu=menu_registration,
        start_text="Привіт, юний інженере 👷‍♀️👷\n\nПеред тим, як ти станеш учасником інженерних змагань EBEC 2022, мені потрібно задати тобі декілька питань 🔧",
        start_photo="https://i.ibb.co/J3nMcpJ/ebecPic.png",
    )
    ebec.save()
