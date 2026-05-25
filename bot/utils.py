from enum import Enum
from functools import wraps
from typing import Callable

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.log import logger
from config import Config


class ConfirmButtons(Enum):
    send = "Отправить"
    cancel = "Отмена"


class RequestStatus(Enum):
    open = "Открыто"
    work = "В работе"
    closed = "Закрыто"


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Старт"),
        BotCommand(command="cancel", description="Отмена"),
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def make_inline_keyboard(buttons_info: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button_info in buttons_info:
        builder.add(
            InlineKeyboardButton(
                text=f"{button_info.get('text')}",
                callback_data=button_info.get("callback_data"),
            )
        )
    return builder.as_markup()


def _reformat_requests_list(requests_list_raw: list) -> str:
    requests_list = [f"{i} - {req_text}" for i, req_text in requests_list_raw]
    return "\n".join(requests_list)


def log_deco(coroutine: Callable):
    @wraps(coroutine)
    async def wrapper(*args, **kwargs):
        logger.info(f"Вызов метода: {coroutine.__name__}")
        return await coroutine(*args, **kwargs)
    return wrapper


def split_text(text: str, max_len: int = Config.MAX_MESSAGE_LEN) -> list[str]:
    if max_len <= 0:
        raise ValueError("max_len must be positive")

    chunks = []
    current_chunk = []
    current_len = 0

    for line in text.splitlines():
        separator_len = 1 if current_chunk else 0
        line_len = len(line) + separator_len

        # Если строка сама больше лимита
        if len(line) > max_len:
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_len = 0

            for i in range(0, len(line), max_len):
                chunks.append(line[i:i + max_len])

            continue

        if current_len + line_len > max_len:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_len = len(line)
        else:
            current_chunk.append(line)
            current_len += line_len

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks
