from aiogram.fsm.state import StatesGroup, State


class Responder(StatesGroup):
    wait_start = State()
    wait_request_id = State()
    wait_response = State()
    wait_confirm = State()


class User(StatesGroup):
    wait_request = State()
    wait_confirm = State()
