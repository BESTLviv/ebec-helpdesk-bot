from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    InlineQuery,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from src.staff import quiz

from src.data.quiz import Quiz

from ..data import Data
from ..data.user import User, Team
from ..data.helpdesk import Item, ItemLog
from .section import Section
from ..staff.sender import Sender, DestinationEnum
from ..staff.filedownload import FileDownloader


class HelpdeskSection(Section):
    def __init__(self, data: Data):
        super().__init__(data)
        self._mailing_destinations = [v.value for v in DestinationEnum]

    def send_helpdesk_menu(self, user: User, call=None):
        if user.is_registered is False:
            self._register_user(user)
            return
        text = "Привіт"
        markup = self._create_item_list_markup()

        self.bot.send_message(user.chat_id, text=text, reply_markup=markup)    

    def send_inline_result(self, inline_query: InlineQuery):
        result_list = list()
        query = inline_query.query

        for item in Item.objects:
            item: Item
            if query.lower() not in item.full_name.lower() and query != "":
                continue

            result_list.append(
                InlineQueryResultArticle(
                    str(item.id),
                    title=item.full_name,
                    input_message_content=InputTextMessageContent(item.p_description),
                    description=item.p_description,
                    thumb_url=item.photo,
                )
                # InlineQueryResultPhoto(
                #    str(item.id),
                #    photo_url=item.photo,
                #    thumb_url=item.photo,
                #    title=item.full_name,
                #    caption=item.p_description,
                #    parse_mode="HTML",
                #    reply_markup=self._create_item_list_markup(),
                # )
            )

        self.bot.answer_inline_query(inline_query.id, result_list)

    def _create_item_list_markup(self) -> InlineKeyboardMarkup:
        markup = InlineKeyboardMarkup()

        for item in Item.objects:
            item: Item
            btn = InlineKeyboardButton(
                text=f"{item.alternative_names[0]} | {item.count}",
                callback_data="hello",
            )
            markup.add(btn)

        return markup