#!/bin/sh
set -e

case "$1" in
  bot)
    exec python -m tgbot
    ;;
  migrate)
    exec aerich upgrade
    ;;
  makemigrations)
    exec aerich migrate --name "${2:-auto}"
    ;;
  init-db)
    aerich init -t tgbot.db.TORTOISE_ORM --location ./migrations
    exec aerich init-db
    ;;
  *)
    exec "$@"
    ;;
esac
