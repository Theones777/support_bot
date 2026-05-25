import os
from datetime import datetime, UTC

from tortoise import Tortoise

from bot.log import logger
from bot.utils import log_deco
from config import Config
from db.models import *


class Storage:

    @staticmethod
    async def init_db():
        os.makedirs("data", exist_ok=True)
        await Tortoise.init(db_url=Config.DB_URL, modules={"models": ["db.models"]})
        await Tortoise.generate_schemas()
        await Tortoise.get_connection("default").execute_script(
            "PRAGMA journal_mode=WAL;"
        )
        logger.info(f"База данных проинициализирована")

    @staticmethod
    @log_deco
    async def save_new_user(user_id: int, user_name: str, tg_user_name: str):
        user, created = await User.get_or_create(
            id=user_id,
            name=user_name,
            tg_user_name=tg_user_name,
        )
        if created:
            logger.info(f"Новый пользователь {user_name} добавлен")

    @staticmethod
    @log_deco
    async def get_responders_list() -> list:
        return await User.filter(responder=True).all().values_list("id", flat=True)

    @staticmethod
    @log_deco
    async def save_new_request(user_id: int, request_text: str):
        user, created = await Request.get_or_create(
            from_user_id=user_id,
            request_text=request_text,
            status=RequestStatus.open.name,
        )
        if created:
            logger.info("Создано новое обращение")
            return True
        return None

    @staticmethod
    @log_deco
    async def save_new_responder(responder_id: int, responder_name: str):
        user = await User.filter(id=responder_id).first()
        user.responder = True
        await user.save()
        logger.info(f"Новый responder {responder_name} добавлен")
        return True

    @staticmethod
    @log_deco
    async def get_requests_list() -> list:
        return await Request.filter(status=RequestStatus.open.name).order_by("created_at").values_list("id", "request_text")

    @staticmethod
    @log_deco
    async def check_request_status(request_id: int):
        if request_status := await Request.filter(id=request_id).first().values_list("status"):
            return request_status[0] == RequestStatus.open.name
        return None

    @staticmethod
    @log_deco
    async def update_request_status(
        request_id: int, responder_user_id: int, status: str
    ):
        request = await Request.filter(id=request_id).first()
        request.status = status
        request.responder_user_id = responder_user_id
        await request.save()
        logger.info(f"request {request_id} обновлен статус {status}")
        return request.request_text

    @staticmethod
    @log_deco
    async def update_request_response(request_id: int, response_text: str) -> int:
        request = await Request.filter(id=request_id).first()
        request.response_text = response_text
        request.answered_at = datetime.now(UTC)
        await request.save()
        logger.info(f"request {request_id} обработан")
        return request.from_user_id
