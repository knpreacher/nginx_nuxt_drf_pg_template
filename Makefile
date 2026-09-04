.PHONY: up down dev dev-down build logs migrate makemigrations superuser seed shell-be shell-fe hybrid hybrid-down hybrid-back hybrid-front

# прод-стек
up:             ; docker compose up -d --build
down:           ; docker compose down
build:          ; docker compose build
logs:           ; docker compose logs -f

# дев-стек
dev:            ; docker compose -f docker-compose.dev.yml up --build
dev-down:       ; docker compose -f docker-compose.dev.yml down

# команды джанго — только в дев-стеке
migrate:        ; docker compose -f docker-compose.dev.yml exec backend python manage.py migrate
makemigrations: ; docker compose -f docker-compose.dev.yml exec backend python manage.py makemigrations
superuser:      ; docker compose -f docker-compose.dev.yml exec backend python manage.py createsuperuser
seed:           ; docker compose -f docker-compose.dev.yml exec backend python manage.py seed_catalog
shell-be:       ; docker compose -f docker-compose.dev.yml exec backend sh
shell-fe:       ; docker compose -f docker-compose.dev.yml exec frontend sh

# гибридный dev: postgres+nginx в docker, back+front на хосте.
# hybrid — поднять инфраструктуру; back/front запускать в отдельных терминалах.
hybrid:         ; docker compose -f docker-compose.hybrid.yml up -d
hybrid-down:    ; docker compose -f docker-compose.hybrid.yml down
hybrid-back:    ; set -a && . ./.env && set +a && cd backend/app && POSTGRES_HOST=localhost uv run python manage.py migrate && POSTGRES_HOST=localhost uv run python manage.py runserver 0.0.0.0:8000
hybrid-front:   ; set -a && . ./.env && set +a && cd frontend/app && NUXT_API_INTERNAL=http://localhost:8000 yarn dev
