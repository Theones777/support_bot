import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.handlers.common import common_router
from bot.handlers.responder import responder_router
from bot.handlers.user import user_router
from bot.log import logger
from bot.utils import set_commands
from config import Config
from db.tort_client import Storage


async def main():
    # bot init
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # include routers
    dp.include_router(common_router)
    dp.include_router(user_router)
    dp.include_router(responder_router)

    # init db
    db_client = Storage()
    await db_client.init_db()

    # set menu buttons
    await set_commands(bot)

    # bot start
    bot.db_client = db_client
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot is starting!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
