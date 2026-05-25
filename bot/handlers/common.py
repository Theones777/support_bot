from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
)

from bot.states import User, Responder
from bot.utils import make_inline_keyboard, RequestStatus
from config import Config

common_router = Router()


@common_router.message(StateFilter("*"), Command(commands=["start"]))
async def message_start_handler(msg: Message, state: FSMContext, bot: Bot):
    db_client = bot.db_client
    user_id: int = msg.from_user.id

    user_data = await state.get_data()
    if request_id := user_data.get("request_id"):
        await db_client.update_request_status(
            request_id, user_id, RequestStatus.open.name
        )

    await state.set_data({})
    await state.clear()

    user_full_name: str = msg.from_user.full_name
    tg_user_name: str = msg.from_user.username
    await db_client.save_new_user(user_id, user_full_name, tg_user_name)
    responders_ids = await db_client.get_responders_list()

    if user_id in responders_ids:
        message = "Чтобы начать работу нажмите кнопку ниже"

        keyboard = await make_inline_keyboard(
            [
                {"text": "Получить обращения", "callback_data": "get_requests"}
            ]
        )
        state_name = Responder.wait_start
    else:
        message = "Здравствуйте! Напишите, пожалуйста, Ваш вопрос"
        keyboard = ReplyKeyboardRemove()
        state_name = User.wait_request

    await state.set_state(state_name)
    await msg.answer(message, reply_markup=keyboard)


@common_router.message(StateFilter("*"), Command(commands=["cancel"]))
async def cancel_handler(msg: Message, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    if request_id := user_data.get("request_id"):
        await bot.db_client.update_request_status(
            request_id, msg.from_user.id, RequestStatus.open.name
        )

    await state.set_data({})
    await state.clear()
    await msg.answer("Отмена", reply_markup=ReplyKeyboardRemove())


@common_router.message(StateFilter("*"), Command(commands=["register"]))
async def add_admin_handler(
    msg: Message, command: CommandObject, state: FSMContext, bot: Bot
):
    if command.args == Config.RESPONDER_REGISTRATION_PHRASE:
        if await bot.db_client.save_new_responder(
            msg.from_user.id, msg.from_user.full_name
        ):
            await msg.answer(
                text="Теперь Вы можете отвечать на обращения. Введите /start"
            )
            await state.clear()
