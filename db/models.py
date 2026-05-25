from tortoise import fields
from tortoise.models import Model

from bot.utils import RequestStatus


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    tg_user_name = fields.CharField(max_length=255)
    responder = fields.BooleanField(default=False)


class Request(Model):
    id = fields.IntField(pk=True)

    from_user = fields.ForeignKeyField("models.User", related_name="requests")
    responder_user = fields.ForeignKeyField(
        "models.User", related_name="responses", null=True
    )

    request_text = fields.TextField()
    response_text = fields.TextField(null=True)

    status = fields.CharField(max_length=10, default=RequestStatus.open.name)
    created_at = fields.DatetimeField(auto_now_add=True)
    answered_at = fields.DatetimeField(null=True)
