from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "form" TYPE VARCHAR(255) USING "form"::VARCHAR(255);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "form" TYPE VARCHAR(10) USING "form"::VARCHAR(10);"""


MODELS_STATE = (
    "eJztmFFv2jAQx79KlCcqdRUEKGxvQNnKVGBq6TZ1myKTmGDh2FnitEVdv/tsh5DEECisXd"
    "mUt+T8P+fuZ8dn+0F3qQ1xcHIdQF9/pz3oBLiQP2Tsx5oOPC+xCgMDYyyFIVdICxgHzAcW"
    "48YJwAHkJhsGlo88hijhVhJiLIzU4kJEnMQUEvQzhCajDmRTGci3H9yMiA3vYRC/ejNzgi"
    "C2M3EiW3xb2k0296StR9h7KRRfG5sWxaFLErE3Z1NKlmpEmLA6kEAfMCi6Z34owhfRLdKM"
    "M4oiTSRRiCkfG05AiFkq3ScysCgR/Hg0gUzQEV95Y1RqjVqzelprcomMZGlpPEbpJblHjp"
    "LAYKQ/ynbAQKSQGBNuzDHXoWsjJ5fe0mU7wBjXARB8axjVasMoV0+b9VqjUW+WlyhXmzYx"
    "bfc+CKxcQPk0jyZ/zDnDVfwR8nWFbmcK/Fy2aTeFME/rCYQX/JaAY0lCOPkvnwmxC+5NDI"
    "nDpmJm1usb8H1uXXbOW5clrjrKQhwsmoyobYXnBPkBM/cgmnUsmKaYYrAf0oxfQTQmOqG+"
    "uwvJWL8XwZWV9L9AiAKTQWBNo/2GUpUoxRCQnKKecVSIjrnnSyHddZejMN1UaobDCxG1Gw"
    "Q/cVR7lMIzuO63u5eliiTMRYjl1CNOZ4ypNYPriv0WrCnHAmsWq+VDkbYJ2CrWM97CkAvX"
    "c816KlzthetJ/HCgywHPwR4SPF+s5xuYj3r97tWo1f+UAX/WGnVFiyGtc8VaOlUWjmUn2p"
    "fe6FwTr9rNcNCVBGnAHF9+MdGNbnQREwgZNQm9M4Gd2mDG1hhMZmBlgeOnGHQL9xjcVe9i"
    "gF91gGXw4vA4maWOQcIwBtbsDvi2udJCDZqnXW1yDVe1AAIcOSqCrYgydZbu+NCGhCE+Xn"
    "rOcTstOd528jYtRb3tEK5fzLmLo5Wu+KyFR1rKX/seGuVKTRPTyoNEmLWJT12N65HoVnRx"
    "oisT6Fk6/IMLgJc9yB7OTcBfOcfm3xdgOcompg4iu+x0Vb9ix6si9UAQ3FF/zRzeSjXtWo"
    "Bdgg09e8/NWdazqN1F7V4U5hb0kTVdV7IXLRsrNUg0xSX585fGF7skv4V+IELaYWVOuRQr"
    "8hKk+DV2gLiQ/5sAK+XyEwByVS5A2abcN1DCIFlTzz5eDQc5Fw2Ji1rIkMW0Xxrme/DDBL"
    "qBn8g3U61ibKV+66tKtHMxbKtlSHTQ5nRftbA8/gbwWmlZ"
)
