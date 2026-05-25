from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.states import Responder
from bot.utils import (
    _reformat_requests_list,
    RequestStatus,
    make_inline_keyboard,
    ConfirmButtons, split_text,
)

responder_router = Router()


@responder_router.callback_query(
    Responder.wait_confirm, F.data.in_([el.name for el in ConfirmButtons])
)
async def response_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    user_data = await state.get_data()
    request_id = user_data.get("request_id")

    if callback.data == ConfirmButtons.send.name:
        response_text = user_data.get("response")

        if user_id := await bot.db_client.update_request_response(
            request_id, response_text
        ):
            user_answer = f"Ответ на Ваш запрос: \n\n" f"{response_text}"
            await bot.send_message(user_id, user_answer)

            message = "Спасибо! Ответ поступил в нужный чат"

            await bot.db_client.update_request_status(
                request_id, callback.from_user.id, RequestStatus.closed.name
            )
        else:
            message = "Ошибка передачи данных"
    else:
        message = "Внесение информации отменено"
        await bot.db_client.update_request_status(
            request_id, callback.from_user.id, RequestStatus.open.name
        )

    await state.set_data({})
    await state.clear()
    await callback.message.answer(text=message)
    await callback.answer()


@responder_router.message(Responder.wait_response)
async def get_response(msg: Message, state: FSMContext):
    response = msg.text

    await state.update_data(response=response)
    keyboard = await make_inline_keyboard(
        [
            {"text": button.value, "callback_data": button.name}
            for button in ConfirmButtons
        ]
    )
    await state.set_state(Responder.wait_confirm)

    message = f"Вы уверены, что хотите отправить данный ответ?\n\n{response}"
    await msg.answer(text=message, reply_markup=keyboard)


@responder_router.message(Responder.wait_request_id)
async def get_request_id(msg: Message, state: FSMContext, bot: Bot):
    request_id = msg.text

    if await bot.db_client.check_request_status(request_id):
        request_text = await bot.db_client.update_request_status(
            request_id, msg.from_user.id, RequestStatus.work.name
        )
        message = (
            f"Ответьте, пожалуйста, на данный вопрос в данном чате:\n\n"
            f"{request_text}"
        )
        await state.update_data(request_id=request_id)
        await state.set_state(Responder.wait_response)
        await msg.answer(message, reply_markup=ReplyKeyboardRemove())
    else:
        message = "На данный вопрос уже ответили, выберите, пожалуйста другой"
        await state.set_state(Responder.wait_request_id)
        await msg.answer(message, reply_markup=ReplyKeyboardRemove())


@responder_router.callback_query(Responder.wait_start)
async def response_start(callback: CallbackQuery, state: FSMContext, bot: Bot):
    requests_list = await bot.db_client.get_requests_list()
    tg_requests = _reformat_requests_list(requests_list)
    message = (
        f"Введите номер вопроса, на который хотите ответить\n" f"{tg_requests}"
    )
    await state.set_state(Responder.wait_request_id)
    if tg_requests:
        for chunk in split_text(message):
            await callback.message.answer(
                chunk,
                reply_markup=ReplyKeyboardRemove(),
            )
    else:
        await callback.message.answer(
            "Обращений нет",
            reply_markup=ReplyKeyboardRemove(),
        )
    await callback.answer()
