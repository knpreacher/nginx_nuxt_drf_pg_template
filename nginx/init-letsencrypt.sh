#!/usr/bin/env sh
# разовый бутстрап сертификата.
set -e

cd "$(dirname "$0")/.."

# docker compose читает .env сам, а этому скрипту DOMAIN/CERTBOT_EMAIL нужны в окружении
if [ -f .env ]; then
  set -a; . ./.env; set +a
fi

: "${DOMAIN:?задай DOMAIN (в .env или в окружении)}"
: "${CERTBOT_EMAIL:?задай CERTBOT_EMAIL (в .env или в окружении)}"

echo "1/4 временный self-signed сертификат для ${DOMAIN}"
docker compose run --rm --entrypoint sh certbot -c "
  set -e
  mkdir -p /etc/letsencrypt/live/${DOMAIN}
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout /etc/letsencrypt/live/${DOMAIN}/privkey.pem \
    -out /etc/letsencrypt/live/${DOMAIN}/fullchain.pem \
    -subj '/CN=${DOMAIN}'
"

echo "2/4 поднимаем nginx (теперь сертификат есть)"
# --no-deps намеренно: остальной стек уже поднят основным `up`
docker compose up -d --no-deps nginx

echo "3/4 удаляем заглушку и запрашиваем настоящий сертификат через webroot-челлендж"
docker compose run --rm --entrypoint sh certbot -c "
  rm -rf /etc/letsencrypt/live/${DOMAIN} /etc/letsencrypt/archive/${DOMAIN} /etc/letsencrypt/renewal/${DOMAIN}.conf
"

docker compose run --rm --entrypoint certbot certbot certonly --webroot -w /var/www/certbot \
  -d "${DOMAIN}" --email "${CERTBOT_EMAIL}" --agree-tos --no-eff-email \
  --non-interactive --force-renewal

echo "4/4 перечитываем конфиг nginx с настоящим сертификатом"
docker compose exec nginx nginx -s reload

echo "Сертификат для ${DOMAIN} получен."
