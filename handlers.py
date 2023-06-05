from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove
from environs import Env
from httpx import Client

from keyboards import make_row_keyboard
from scenarios import Scenario

env = Env()

router = Router()

start_msg = """
I'm a Clotest bot. I can help you test Cloudike services.

Available commands:
/newacc - Create test company account and linked email
/cancel - Cancel the current command
"""

available_tokens = env.list("CLOUDIKE_TEAMEMBER_TOKENS")
available_host_names = env.list("CLOUDIKE_HOSTS")
available_plan_names = env.list("CLOUDIKE_COMPANY_PLANS")


class CreateCompany(StatesGroup):
    token = State()
    host = State()
    plan = State()


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=start_msg, reply_markup=ReplyKeyboardRemove())


@router.message(Command(commands=["cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="Action cancelled", reply_markup=ReplyKeyboardRemove())


@router.message(Command("newacc"))
async def cmd_newacc(message: Message, state: FSMContext):
    await message.answer(text="Enter access token:")
    await state.set_state(CreateCompany.token)


@router.message(CreateCompany.token, F.text.in_(available_tokens))
async def token_chosen(message: Message, state: FSMContext):
    await message.answer(
        text="Choose Clodike host:",
        reply_markup=make_row_keyboard(available_host_names),
    )
    await state.set_state(CreateCompany.host)


@router.message(CreateCompany.token)
async def toke_chosen_incorrectly(message: Message):
    await message.answer(text="Token incorrect! Please enter valid token:")


@router.message(CreateCompany.host, F.text.in_(available_host_names))
async def host_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_host=message.text.lower())
    await message.answer(
        text="Got it! Choose account plan:",
        reply_markup=make_row_keyboard(available_plan_names),
    )
    await state.set_state(CreateCompany.plan)


@router.message(CreateCompany.host)
async def host_chosen_incorrectly(message: Message):
    await message.answer(
        text="Please choose a host from the suggested list:",
        reply_markup=make_row_keyboard(available_host_names),
    )


@router.message(CreateCompany.plan, F.text.in_(available_plan_names))
async def plan_chosen(message: Message, state: FSMContext):
    user_data = await state.get_data()
    choosen_host = user_data["chosen_host"]
    choosen_plan = message.text.lower()

    await message.answer(
        text=f"Account with {choosen_plan} plan on {choosen_host} host will be created!\n"
        "The process can take some time, please wait...",
        reply_markup=ReplyKeyboardRemove(),
    )

    with Client() as client:
        scenario = Scenario(client)
        result = scenario.create_company_fake_email(choosen_host, choosen_plan)

    result_email_msg = f"""
    Mailbox / Cloudike Credentials:

    Email: {result["company_admin_email"]}
    Password: {result["company_admin_password"]}
    Mailbox Link: https://mail.tm/en/
    """

    await message.answer(text=result_email_msg)
    # await message.answer(
    #     text=f"Please open this link to complete registration and log in to account: {result['confirm_link']}"
    # )

    await state.clear()


@router.message(CreateCompany.plan)
async def plan_chosen_incorrectly(message: Message):
    await message.answer(
        text="Please choose a plan from the suggested list:",
        reply_markup=make_row_keyboard(available_plan_names),
    )


@router.message()
async def cmd_anything(message: Message):
    await message.answer(text=start_msg)
