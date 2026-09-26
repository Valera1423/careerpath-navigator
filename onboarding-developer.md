# Onboarding нового разработчика

**Цель:** за 1 час поднять проект локально и сделать первый коммит.

## Требования к окружению

| Инструмент | Версия | Зачем |
|---|---|---|
| Python | 3.12+ | Backend |
| Node.js | 20+ | Frontend |
| Docker | 24+ | Полный стек одной командой |
| Git | 2.40+ | Версии |
| VS Code | любой | Рекомендуемый редактор |

**Проверка:**
```bash
python --version     # Python 3.12+
node --version       # v20+
docker --version     # Docker 24+
Шаг 1. Клонирование (2 минуты)
bash
git clone https://github.com/Valera1423/careerpath-navigator.git
cd careerpath-navigator
cp .env.example .env
Шаг 2. Выбор пути
Путь А — Docker (5 минут, если образы уже скачаны)
bash
docker compose up --build
Frontend: http://localhost:8080

Backend: http://localhost:8000/docs

БД: SQLite в Docker volume

Это самый быстрый способ увидеть продукт целиком. Не требует установки Python/Node на хост.

Путь Б — локальная разработка (30 минут, в первый раз)
Для активной разработки — backend и frontend запускаются отдельно.

Backend
bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
Создайте backend/.env:

dotenv
DATABASE_URL=sqlite:///./data/careerpath.db
ALLOW_INSECURE_INIT_DATA=true
CORS_ORIGINS=http://localhost:5173
ADMIN_SECRET=dev-secret
Миграции и запуск:

bash
mkdir -p data
alembic upgrade head
uvicorn app.main:app --reload --port 8000
Frontend
bash
cd frontend
npm install
Создайте frontend/.env:

dotenv
VITE_API_BASE=http://localhost:8000/api/v1
VITE_DEV_USER_ID=dev-user-1
Запуск:

bash
npm run dev
# http://localhost:5173
Vite проксирует /api на localhost:8000.

Путь В — VS Code с devcontainer (для команды)
Если установлен расширение Dev Containers, откройте проект через F1 → Dev Containers: Reopen in Container. Всё поднимется автоматически.

Шаг 3. Первый запуск — что проверить
Откройте http://localhost:5173

Пройдите онбординг: должность → опыт → навыки → согласие

Увидите дашборд с % готовности и списком gap-навыков

Отметьте первый шаг плана — XP увеличится

Откройте http://localhost:8000/docs — Swagger со всеми эндпоинтами

Если что-то не работает — см. Troubleshooting в README.

Шаг 4. Карта кода
Backend: где что искать
Что нужно	Куда смотреть
Добавить эндпоинт	app/routers/ — новый файл + регистрация в main.py
Поменять бизнес-логику	app/services/ — сервис по домену
Добавить поле в модель	app/models.py + миграция Alembic
Поменять DTO	app/schemas.py
Конфиг	app/config.py
Новый навык в словарь	app/data/skills.yaml
Новый сценарий симулятора	app/data/scenarios/*.json
Метрика Prometheus	app/services/metrics.py
Frontend: где что искать
Что нужно	Куда смотреть
Новый экран	src/components/
Новый API-метод	src/api/client.ts + типы в src/types.ts
Компонент UI	src/ui/index.tsx — адаптер над MAX UI
Локализация	src/i18n/ru/*.json, src/i18n/en/*.json
Глобальные стили	src/styles.css
Машина состояний	src/machines/
Работа с MAX	src/max/bridge.ts
Хук для переиспользования	src/hooks/
Правила слоёв
Backend:

Router → Service → ORM. Никакой бизнес-логики в роутерах.

Сервисы не знают про HTTP. Не импортируют Request, HTTPException.

Модель = таблица БД, схема = DTO API. Не смешивать.

Frontend:

Компоненты не знают про fetch. Все запросы — через api/client.ts.

Компоненты не импортируют @dementevdev/max-ui напрямую. Только src/ui/index.tsx.

Любая строка — через t('key'), никакого хардкода.

Шаг 5. Рабочий процесс
Ветки
text
main              — стабильная, деплоится на Vercel/Wispbyte
feat/<название>   — новая фича
fix/<название>    — багфикс
docs/<название>   — документация
Коммиты
Conventional Commits:

text
feat: add skill gap caching
fix: correct webapp button format
docs: update deploy guide
refactor: extract trudvsem client
test: add simulator tests
Перед коммитом
bash
# Backend
cd backend
ruff check app tests
ruff format app tests
mypy app
pytest

# Frontend
cd frontend
npm run typecheck
npm run build
Или одной командой:

bash
make lint
make test
Pull Request
Форк / ветка в основном репо

Push

Открыть PR в main

CI должен быть зелёным

Запросить ревью у второго разработчика

Релиз
Тег на main: git tag v1.2.0 && git push --tags

Vercel пересоберёт автоматически

Backend — ручной Restart в панели Wispbyte

Шаг 6. Полезные команды
bash
# Makefile
make help          # список команд
make up            # docker compose up
make down          # docker compose down
make test          # pytest + npm typecheck
make lint          # ruff + mypy + tsc
make fmt           # автоформат
make migrate       # alembic upgrade head
make revision m="add field"   # новая миграция
make shell         # shell в backend контейнере

# Прямые
docker compose logs -f backend      # логи
docker compose exec backend bash    # shell
cd frontend && npx vite             # dev-сервер
Шаг 7. Частые проблемы
Проблема	Решение
ModuleNotFoundError	Активируйте venv: source .venv/bin/activate
relation "users" does not exist	alembic upgrade head
CORS error в браузере	Проверьте CORS_ORIGINS в .env — должен совпадать с доменом фронта
Frontend не видит API	Проверьте VITE_API_BASE в frontend/.env
MAX UI не находит экспорт	Проверьте @dementevdev/max-ui версию в package.json
Docker ругается на образы	Настройте registry-mirrors в Docker Desktop
Что почитать
README.md — общий обзор

docs/architecture.md — как всё связано

docs/testing.md — как тестировать

docs/deploy.md — как деплоить

FastAPI docs

MAX Bridge docs

Первая задача для новичка
Возьмите issue с меткой good first issue. Обычно это:

Добавить 5–10 навыков в skills.yaml

Написать тест на существующий сервис

Исправить текст в i18n/ru/*.json

Если что-то не получается — пишите в чат команды. Не тратьте больше 30 минут на затык в одиночку.
