from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "users" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL UNIQUE,
    "tg_username" VARCHAR(255),
    "tg_first_name" VARCHAR(255),
    "tg_last_name" VARCHAR(255),
    "form" VARCHAR(10) NOT NULL,
    "is_teacher" BOOL NOT NULL DEFAULT False,
    "is_blocked" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "last_active_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "user_credentials" (
    "tg_id" BIGSERIAL NOT NULL PRIMARY KEY,
    "lycreg_login" VARCHAR(255) NOT NULL,
    "lycreg_password" VARCHAR(255) NOT NULL,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE "user_credentials" IS 'Lycreg (Scole) credentials — independent from registration.';
CREATE TABLE IF NOT EXISTS "user_logs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "tg_id" BIGINT NOT NULL,
    "tg_username" VARCHAR(255),
    "tg_first_name" VARCHAR(255),
    "log_type" VARCHAR(20) NOT NULL,
    "text" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmW1v0zoUx79KlFebBFObdeu477pRYKhrESsXBPcqchM3tebYIXG2VbDvjo+TNE9N+g"
    "CFFuVdc3yOc/yz4/O3+013uY1pcPIhwL7+j/ZNZ8jF8kfO/kzTkeelVjAINKHKMZQeyoIm"
    "gfCRJaRximiApcnGgeUTTxDOpJWFlIKRW9KRMCc1hYx8DbEpuIPFTCXy5X9pJszGjzhIHr"
    "07c0owtXN5EhvereymmHvKds3EK+UIb5uYFqehy1Jnby5mnC28CRNgdTDDPhIYuhd+COlD"
    "dvEwkxFFmaYuUYqZGBtPUUhFZrhrMrA4A34ym0AN0IG3PDfanW7n4vS8cyFdVCYLS/cpGl"
    "469ihQERiO9SfVjgSKPBTGlJtwzGXoLolTSW8RshpggmsPCL4wjNPTrtE6Pb8463S7Zxet"
    "BcpyUx3Ty+vXgFU6cLnMo8WfcM5xhS9CPZboXs2QX8k2G1YgLIe1BuGY3wJw4pISTr/LX4"
    "TYRY8mxcwRM1iZZ2c1+P7tvb9603t/JL2O8xCHcZMRtZV4TokfCHMLovnAhmmGKUXbIc3F"
    "NUQTolPuu5uQTPy3IljaSX83wnZrDYLtViVAaMrzI4EpMLJmkdgolCTOKUasoqLnAgs4Jz"
    "JyVzw3lTgFoHV1ZjQaQNZuEHylUeEpVJ3hh5vLviSsAEsnIiqKkaQzody6w8sq/QqsmcAG"
    "ax6r5WMYtolEGetL2SKIi5dzzUcWuNpx6EnyY0/3AjkGe8ToPN7Ma5iPr2/6t+Pezbsc+J"
    "e9cR9aDGWdF6xH54V9Y9GJ9vF6/EaDR+3zaNhXBHkgHF+9MfUbf9YhJxQKbjL+YCI7oy4T"
    "awImN7GquskjDLnHW0xuObqZ4D86wSp5ODlO7zJnIDBMkHX3gHzbLLVwg1f5lptcwy1aEE"
    "OOmhVgC1lmDtJXPrYxE0TOl15x1s66PFt17DatgveqE7g+mMsQRzu6lasWH2uZeO2/0Gi1"
    "OxosKw8zMGtTn7ua9CfQLXRxohcW0C/p8CdO/7s9xe7PNcBvOcRWXxZQNcsm5Q5hm8jcYt"
    "xhyt2dnBhiNB4KggfuL1nDK6lmQxuwC7ChZ28pzvKRTe1uanemMA+4U1WzoWl1rZabYHNN"
    "3lyT7+Oe0VyU/wV1r7ko34FI406EYRN1lok5UFm2zvWuUX29a5SudwV+XKLGxtJasSRj/w"
    "NZiXUiq/9pnNNXCaajm96n45zGGoyGrxP3DNarweiyuX/8GyVudP+4Jxq3h31izfQlEjdu"
    "qVW4KPVp5O0Bydt77AeQ0gb1LRNyoOVtF0oBPo0NIMbuhwmw3Vrv/9+6P4BLEkG+UWC2pK"
    "C9vR0NK4pZGlKsZMQS2neNkmBPj1w1/GC89YqhKA4KdQg6AMXwRwvL0w96p956"
)
