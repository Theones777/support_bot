from os import getenv

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = getenv("BOT_TOKEN")
    RESPONDER_REGISTRATION_PHRASE = getenv("RESPONDER_REGISTRATION_PHRASE", "just_love")

    DB_URL = getenv("DB_URL", "sqlite://data/database.db")
    RECORD_LIFETIME = 60
    MAX_MESSAGE_LEN = 4000
