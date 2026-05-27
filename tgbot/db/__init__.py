from tgbot.config import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["tgbot.db.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
