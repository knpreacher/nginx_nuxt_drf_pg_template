#!/usr/bin/env sh
set -e

# ждем поднятия postgres перед миграциями
echo "Waiting for postgres at ${POSTGRES_HOST:-postgres}:${POSTGRES_PORT:-5432}..."
until python -c "import socket,os,sys; s=socket.socket(); s.settimeout(2); \
  s.connect((os.environ.get('POSTGRES_HOST','postgres'), int(os.environ.get('POSTGRES_PORT','5432')))); s.close()" 2>/dev/null; do
  sleep 1
done

python manage.py migrate --noinput

# статику собираем только в проде (флаг выключен в dev-образе)
if [ "${DJANGO_COLLECTSTATIC:-1}" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
