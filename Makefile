.PHONY: bot makemigrations migrate init-db shell

# Run the bot locally
bot:
	python -m tgbot

# Generate new migration (usage: make makemigrations name=my_migration)
makemigrations:
	aerich migrate --name $(or $(name),auto)

# Apply all pending migrations
migrate:
	aerich upgrade

# One-time: initialise aerich and create the initial migration
init-db:
	aerich init -t tgbot.db.TORTOISE_ORM --location ./migrations
	aerich init-db

# Downgrade last migration
downgrade:
	aerich downgrade -v -1 --yes

# Show migration history
history:
	aerich history
