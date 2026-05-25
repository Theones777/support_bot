from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from bot.states import User
from bot.utils import ConfirmButtons, make_inline_keyboard

user_router = Router()


@user_router.callback_query(
    User.wait_confirm, F.data.in_([el.name for el in ConfirmButtons])
)
async def request_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    if callback.data == ConfirmButtons.send.name:
        user_request = user_data.get("user_request")
        if not await bot.db_client.save_new_request(
            callback.from_user.id, user_request
        ):
            message = "Ошибка передачи данных"
        else:
            message = "Спасибо за Ваш вопрос. Ответ поступит в этот же чат"
    else:
        message = "Внесение информации отменено"

    await state.set_data({})
    await state.clear()
    await callback.message.answer(text=message)
    await callback.answer()


@user_router.message(User.wait_request)
async def request_inserted(msg: Message, state: FSMContext):
    user_request = msg.text
    await state.update_data(user_request=user_request)
    keyboard = await make_inline_keyboard(
        [
            {"text": button.value, "callback_data": button.name}
            for button in ConfirmButtons
        ]
    )
    await state.set_state(User.wait_confirm)

    message = f"Вы уверены, что хотите отправить данный запрос?\n\n{user_request}"
    await msg.answer(text=message, reply_markup=keyboard)
