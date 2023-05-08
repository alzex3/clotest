from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_yes_no_kb() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Yes")
    kb.button(text="No")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)

def get_cloudike_host() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="frontend-dev")
    kb.button(text="stage")
    kb.button(text="prod-kr")
    kb.button(text="prod-net")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard=True)