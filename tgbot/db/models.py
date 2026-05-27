from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    tg_id = fields.BigIntField(unique=True)
    tg_username = fields.CharField(max_length=255, null=True)
    tg_first_name = fields.CharField(max_length=255, null=True)
    tg_last_name = fields.CharField(max_length=255, null=True)
    form = fields.CharField(max_length=10)
    is_teacher = fields.BooleanField(default=False)
    is_blocked = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_active_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return f"User(tg_id={self.tg_id}, form={self.form})"


class UserCredentials(Model):
    """Lycreg (Scole) credentials — independent from registration."""
    tg_id = fields.BigIntField(pk=True)
    lycreg_login = fields.CharField(max_length=255)
    lycreg_password = fields.CharField(max_length=255)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "user_credentials"
