# nginx + Nuxt (SSR) + DRF + PostgreSQL -> шаблон

Готовый Docker-шаблон для проекта: nginx перед двумя приложениями (Nuxt SSR и
Django REST Framework), Postgres, JWT-аутентификация через httponly-cookie,
раздельные dev/prod стеки.

Наружу торчит только nginx (80/443 в проде, 80 в dev). Все остальные сервисы
доступны только внутри docker-сети.

Код приложений лежит строго в `backend/app/` и `frontend/app/` — остальное
в `backend/` и `frontend/` это только Docker (Dockerfile, entrypoint, ...).

## Быстрый старт (dev)

```bash
cp .env.example .env
# для локальной разработки по http:
#   DJANGO_DEBUG=1
#   JWT_COOKIE_SECURE=0
#   POSTGRES_PASSWORD=<свой пароль>
#   DJANGO_SECRET_KEY=<что угодно для дев>

make dev          # docker compose -f docker-compose.dev.yml up --build
```

Создать суперпользователя (модель User без username, ключ — email):

```bash
make superuser     # интерактивно спросит email/password, НЕ username
```

Неинтерактивно:

```bash
docker compose -f docker-compose.dev.yml exec \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  -e DJANGO_SUPERUSER_PASSWORD=adminpass \
  backend python manage.py createsuperuser --noinput
```

## Гибридный dev (back/front на хосте)

Когда удобнее запускать Django и Nuxt нативно (быстрее итерации, дебаггер),
а в Docker держать только инфраструктуру:

```bash
make hybrid          # postgres + nginx в docker (nginx проксирует на host.docker.internal)
make hybrid-back     # в отдельном терминале: миграции + runserver на хосте (:8000)
make hybrid-front    # в отдельном терминале: nuxt dev на хосте (:3000)
```

Открыть — `http://localhost` (nginx на :80). Оба таргета читают `.env` и точечно
перебивают хост БД (`POSTGRES_HOST=localhost`, postgres опубликован на :5432) и
внутренний адрес API для SSR (`NUXT_API_INTERNAL=http://localhost:8000`).
Требуется `uv` и `corepack`-включенный `yarn` на машине.

## Прод-деплой

### 0. Предварительно
- На сервере установлен Docker с `docker compose` v2 (`docker compose version`).
- A-запись домена указывает на IP сервера.
- Порты 80 и 443 открыты снаружи.
- Пользователь в группе `docker` (команды без `sudo`).

### 1. Заполнить `.env`
```bash
cp .env.example .env
```
Обязательные для прода значения:

| Переменная | Значение |
|---|---|
| `DOMAIN` | домен, напр. `app.example.ru` |
| `CERTBOT_EMAIL` | email для Let's Encrypt |
| `DJANGO_SECRET_KEY` | длинная случайная строка (`openssl rand -base64 48`) |
| `DJANGO_DEBUG` | `0` |
| `DJANGO_ALLOWED_HOSTS` | `<домен>` |
| `POSTGRES_PASSWORD` | сильный пароль |
| `JWT_COOKIE_SECURE` | `1` |
| `CSRF_TRUSTED_ORIGINS` | `https://<домен>` |

`DATABASE_URL` **не задавать** - иначе backend уйдет с Postgres на этот URL.

### 2. Собрать и поднять
```bash
docker compose build          # первая сборка долгая: внутри идет yarn build SSR
docker compose up -d          # или make up
```
`postgres`, `backend` (миграции + collectstatic), `frontend` поднимутся нормально.
`nginx` пока перезапускается в цикле — сертификата еще нет, 443 не стартует. Это
ожидаемо, чиним.

### 3. Сертификат TLS (один раз)
```bash
./nginx/init-letsencrypt.sh
```
Скрипт сам читает `.env`, кладет временный self-signed, поднимает `nginx` на 80,
проходит ACME-челлендж и заменяет заглушку на настоящий сертификат Let's Encrypt,
затем перечитывает конфиг.

### 4. Суперпользователь
```bash
docker compose exec backend python manage.py createsuperuser
# либо неинтерактивно:
docker compose exec \
  -e DJANGO_SUPERUSER_EMAIL=admin@<домен> \
  -e DJANGO_SUPERUSER_PASSWORD=<пароль> \
  backend python manage.py createsuperuser --noinput
```

Прод-`nginx` раздает `/static/` и `/media/` напрямую из volume (backend пишет
туда при `collectstatic` / загрузке файлов, nginx читает read-only).

## Два baseURL и cookie-прокидывание (SSR)

Nuxt делает запросы к API из двух разных мест, поэтому у `$fetch` два
базовых адреса (`frontend/app/nuxt.config.ts` → `runtimeConfig`):

- **Сервер (SSR)** — `NUXT_API_INTERNAL` (`http://backend:8000/api`), минуя
  nginx, напрямую в docker-сети. Cookie браузера сюда сами не долетают —
  плагин `plugins/api.ts` руками копирует заголовок `Cookie` из входящего
  SSR-запроса в исходящий запрос к backend.
- **Браузер** — `NUXT_PUBLIC_API_BASE` (`/api`), тот же origin, через nginx;
  cookie летят как обычно.

Гейт авторизации — `middleware/auth.global.ts`: на каждом переходе (кроме
`/login`) дергает `/api/auth/me/`; если не авторизован — редирект на
`/login` (при SSR это настоящий HTTP 302, не JS-редирект).
