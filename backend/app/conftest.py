import os

# чтобы голый `uv run pytest` работал без ручного экспорта DATABASE_URL
# и чтобы явный DATABASE_URL из окружения (если он задан) имел приоритет
os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
