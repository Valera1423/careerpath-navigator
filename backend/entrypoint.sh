#!/bin/sh
# Универсальный entrypoint backend-контейнера.
# - если передана команда (CMD / command) — выполняем её
# - иначе: ждём БД → alembic upgrade → uvicorn (режим API)

set -e
cd /app
export PYTHONPATH=/app

# Если передали команду — сразу её и выполняем.
# Пример: `docker compose run backend pytest`
# Пример: `command: ["python", "-m", "app.services.bot_poller"]`
if [ "$#" -gt 0 ]; then
    echo "[entrypoint] running custom command: $*"
    exec "$@"
fi

# --- Ниже режим API (без переданной команды) ---

echo "[entrypoint] waiting for database..."

python -c "
from app.config import settings
u = settings.database_url
if '@' in u:
    scheme, rest = u.split('://', 1)
    creds, host = rest.split('@', 1)
    user = creds.split(':', 1)[0]
    print(f'[entrypoint] DATABASE_URL = {scheme}://{user}:***@{host}')
else:
    print(f'[entrypoint] DATABASE_URL = {u}')
"

i=1
while [ "$i" -le 30 ]; do
    if python -c "
from sqlalchemy import create_engine
from app.config import settings

url = (
    settings.database_url
    .replace('+asyncpg', '+psycopg')
    .replace('+aiosqlite', '')
)
create_engine(url).connect().close()
" 2>/tmp/check_db.err; then
        echo "[entrypoint] database is ready"
        break
    fi

    if [ "$i" -eq 1 ] || [ "$i" -eq 30 ]; then
        echo "[entrypoint] попытка $i/30 — ошибка:"
        cat /tmp/check_db.err
    else
        echo "[entrypoint] попытка $i/30 — БД ещё не готова, ждём 2с"
    fi

    if [ "$i" -eq 30 ]; then
        echo "[entrypoint] FATAL: не удалось подключиться к БД за 60 секунд"
        exit 1
    fi

    i=$((i + 1))
    sleep 2
done

echo "[entrypoint] applying migrations..."
alembic upgrade head

echo "[entrypoint] starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000