from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from httpx import Client

from keyboards import get_yes_no_kb, get_cloudike_host
from scenarios import Scenario


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Choose Cloudike host to create account:",
        reply_markup=get_cloudike_host()
    )

@router.message(Text(text="frontend-dev", ignore_case=True))
async def answer_yes(message: Message):
    with Client() as client:
        scenario = Scenario(client)
        result = str(scenario.create_company("frontend-dev"))

    await message.answer(
        result,
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(Text(text="stage", ignore_case=True))
async def answer_no(message: Message):
    with Client() as client:
        scenario = Scenario(client)
        result = str(scenario.create_company("stage"))

    await message.answer(
        result,
        reply_markup=ReplyKeyboardRemove()
    )