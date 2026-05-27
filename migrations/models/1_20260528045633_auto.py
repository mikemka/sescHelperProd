from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "user_logs";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """


MODELS_STATE = (
    "eJztmF1P2zAUhv9KlCuQGGrTlna7a0s3mKCdoGwT2xS5iZtadeyQOEDF+O+znaT5avo1Ck"
    "XKXXL8Huf4sePj4yfVpibE3vGNB131k/KkEmBD/pCyHykqcJzYKgwMjLAU+lwhLWDkMRcY"
    "jBvHAHuQm0zoGS5yGKKEW4mPsTBSgwsRsWKTT9CdD3VGLcgmMpBff7gZERM+Qi96dab6GE"
    "FspuJEpvi2tOts5kjbOWGfpVB8baQbFPs2icXOjE0omasRYcJqQQJdwKDonrm+CF9EFw4z"
    "GlEQaSwJQkz4mHAMfMwSw12TgUGJ4Mej8eQALfGVD1q13qy3aif1FpfISOaW5nMwvHjsga"
    "Mk0B+qz7IdMBAoJMaYG7P0Reg6yCqkN3dZDTDCtQcEP2pardbUKrWTVqPebDZalTnKfNMy"
    "pp3zLwIrF1C+zIPFH3FOcRV/hHzN0e1OgFvINumWIcyHtQbhkN8ccCSJCcf/5QshtsGjji"
    "Gx2ESszEZjCb7v7avuWfvqgKsO0xD7YZMWtOV4jpHrMX0LomnHkmmCKQbbIU35lUQjomPq"
    "2puQjPRbEcztpK+NsFpZg2C1UghQNKX5IU9nEBiT4LCRSUmUYghIQUZPOWZwjrjnrnhues"
    "TJAF2WZwaDCxG17Xl3OEg8mazTv7ns9DhhCZiLECtIRpzOCFNjChdl+hVYE44l1jRWw4Vi"
    "2DpgeaynvIUhGy7mmvbMcDVD1+PoYU/3Aj4Gc0DwLNzMlzAfnl/2rofty28p8KftYU+0aN"
    "I6y1gPTjL7xrwT5cf58EwRr8rtoN+TBKnHLFd+MdYNb1URE/AZ1Ql90IGZOF1G1ghMamJl"
    "duMlDLqHW0xu3ruc4DedYBm8qBzH00QNJAwjYEwfgGvquRaq0SJtvsnW7KwFEGDJWRFsRZ"
    "SJQrrrQhMShvh8qQW1dlJytKrs1o2MelUFrl7MuIulHFzzVQsPlYS/8tvXKtW6IpaVA4kw"
    "K2OX2grXI9Gt6OJYzSygF+nwP6r/3Vax+3MN8CpFbPFlAZazrGNqIbLJMTfr9z6PuzupGE"
    "I0DvC8B+ouWMMrqSZdS7BzsL5jbnk4S3uWubvM3WFibkMXGZNFKTtsWZqpQawpb8hfPjXu"
    "7Ib8HrqeCGmDnTnhUu7Ic5Di19gAYih/nwCrlfXuxpZdjuVux/gXGSQL8tnX60G/4KIhds"
    "kmMmQw5a+C+Rl8P4Eu4SfGm8pWEbaDy/bPLNHuxaCTTUOigw6n+6aJ5fkfYBJoqA=="
)
