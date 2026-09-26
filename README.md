# CareerPath Navigator

Мини-приложение для платформы **MAX**, помогающее студентам выпускных курсов и выпускникам понять, какие навыки нужны для желаемой должности, и построить пошаговый план карьерного развития.

**Стек:** FastAPI + PostgreSQL + React + TypeScript + MAX UI + MAX Bot API

**Демо:** https://frontend-coral-seven-71.vercel.app  
**Бот в MAX:** [@se14433704_bot](https://max.ru/@se14433704_bot)  
**Backend API:** https://mytestmaxbot.wisp.uno/docs

---

## Содержание

- [Возможности](#возможности)
- [Архитектура](#архитектура)
- [Быстрый старт (Docker)](#быстрый-старт-docker)
- [Локальная разработка](#локальная-разработка)
- [Тестирование](#тестирование)
- [API](#api)
- [Деплой](#деплой)
- [Переменные окружения](#переменные-окружения)
- [Структура проекта](#структура-проекта)
- [Troubleshooting](#troubleshooting)

---

## Возможности

1. **Онбординг** — 3 шага: должность и регион → опыт → навыки + согласие 152-ФЗ.
2. **Skill Gap** — сравнение навыков пользователя с требованиями реальных вакансий из API «Работа России».
3. **План развития** — пошаговый план (курсы + проекты) для закрытия разрыва.
4. **Рекомендации вакансий** — до 10 позиций с % совпадения навыков.
5. **Трекинг прогресса** — чек-лист шагов + XP + достижения + streak.
6. **AI-коуч** — ответы на вопросы про навыки через бота в MAX.
7. **ATS-анализ** — проверка резюме на проходимость автоматического отбора.
8. **Симулятор дня** — «Один день из жизни аналитика / разработчика / дизайнера».
9. **Карьерный компас** — граф зависимостей навыков.
10. **Симулятор интервью** — 5 вопросов с STAR-оценкой.

---

## Архитектура

```
┌──────────────────┐    HTTPS     ┌─────────────────────┐
│  MAX Messenger   │ ───────────▶ │  Backend (FastAPI)  │
│  + Mini App      │ ◀─────────── │  Wispbyte / Docker  │
│  (React + MAX UI)│   webhook    │                     │
└──────────────────┘              └──────────┬──────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                  │ PostgreSQL   │   │  «Работа     │   │   MAX Bot    │
                  │   (Neon)     │   │  России» API │   │     API      │
                  └──────────────┘   └──────────────┘   └──────────────┘
```

**Backend слои:**
- `app/routers/` — HTTP-эндпоинты
- `app/services/` — бизнес-логика (trudvsem, gap, plan, coach, gamification и т.д.)
- `app/models.py`, `app/schemas.py` — ORM и Pydantic DTO
- `alembic/` — миграции

**Frontend слои:**
- `src/api/` — типизированный клиент REST
- `src/max/` — обёртка над MAX Bridge
- `src/ui/` — адаптер над `@dementevdev/max-ui`
- `src/components/` — экраны приложения

---

## Быстрый старт (Docker)

### Требования
- Docker Desktop 24+
- Docker Compose v2

### Запуск

```bash
git clone <repo-url> careerpath-navigator
cd careerpath-navigator
cp .env.example .env
docker compose up --build
```

**Адреса после запуска:**

| Сервис | URL |
|---|---|
| Frontend | http://localhost:8080 |
| Backend | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Метрики | http://localhost:8000/metrics |
| Health | http://localhost:8000/health |

### С PostgreSQL

```bash
# В .env: DATABASE_URL=postgresql+psycopg://careerpath:careerpath@db:5432/careerpath
docker compose --profile postgres up --build
```

### С мониторингом

```bash
docker compose --profile postgres --profile observability up --build
```

| Сервис | URL |
|---|---|
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 (admin / admin) |

### Проверка

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"CareerPath Navigator API"}

docker compose ps
# все контейнеры healthy
```

---

## Локальная разработка

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

# Настройка окружения
cp ../.env.example .env
# Отредактируйте .env: DATABASE_URL, MAX_BOT_TOKEN

# Миграции
alembic upgrade head

# Запуск
uvicorn app.main:app --reload --port 8000
```

Swagger: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
cp .env.example .env
# Отредактируйте .env: VITE_API_BASE=http://localhost:8000/api/v1

npm run dev
# http://localhost:5173
```

### Планировщик напоминаний

```bash
cd backend
python -m app.services.scheduler
```

### Полезные команды

```bash
make up          # docker compose up -d
make down        # docker compose down
make test        # pytest
make lint        # ruff + mypy + tsc
make fmt         # авто-формат
make migrate     # alembic upgrade head
make revision m="add column"   # новая миграция
make logs        # логи
make shell       # shell в backend
```

---

## Тестирование

### Backend

```bash
cd backend

# Все тесты
pytest

# С покрытием
pytest --cov=app --cov-report=term-missing

# Конкретный файл
pytest tests/test_users.py -v

# Один тест
pytest tests/test_users.py::test_onboarding_creates_profile -v
```

### Frontend

```bash
cd frontend

# Проверка типов
npm run typecheck

# Сборка
npm run build

# Линтер
npx eslint src
```

### E2E (Playwright)

```bash
cd frontend
npm run e2e:install    # один раз
E2E_BASE_URL=http://localhost:8080 npm run e2e
```

### Ручной сценарий проверки

| # | Действие | Ожидаемый результат |
|---|---|---|
| 1 | `curl http://localhost:8000/health` | `{"status":"ok"}` |
| 2 | Открыть `http://localhost:8080` | Онбординг |
| 3 | Заполнить онбординг | Дашборд с gap-анализом |
| 4 | Отметить шаг плана | XP растёт, достижение разблокируется |
| 5 | Открыть вкладку «Компас» | Граф навыков с зелёными/красными узлами |
| 6 | Пройти симулятор интервью | STAR-оценка по 5 вопросам |
| 7 | Открыть бота в MAX | Ответ на `/start` с кнопками |

### Проверка через curl (backend)

```bash
# Создать профиль
curl -X POST http://localhost:8000/api/v1/users/onboarding \
  -H 'Content-Type: application/json' \
  -d '{
    "max_user_id": "test-user-1",
    "desired_position": "Аналитик данных",
    "region": "Москва",
    "experience": "none",
    "skills": ["excel", "python"],
    "consent_pd": true
  }'

# Gap-анализ
curl http://localhost:8000/api/v1/skills/gap \
  -H 'X-Max-User-Id: test-user-1'

# Регенерация плана
curl -X POST http://localhost:8000/api/v1/plan/regenerate \
  -H 'X-Max-User-Id: test-user-1'

# Рекомендации вакансий
curl 'http://localhost:8000/api/v1/vacancies/recommendations?limit=5' \
  -H 'X-Max-User-Id: test-user-1'

# Интервью
curl -X POST http://localhost:8000/api/v1/interview/sessions \
  -H 'X-Max-User-Id: test-user-1'
```

---

## API

**Базовый URL:** `https://mytestmaxbot.wisp.uno/api/v1`  
**Swagger:** `/docs`  
**OpenAPI:** `/openapi.json`

### Аутентификация

Все эндпоинты (кроме `/health`, `/users/onboarding`) требуют один из заголовков:

| Заголовок | Когда использовать |
|---|---|
| `X-Max-Init-Data` | Production: строка `initData` от MAX Bridge |
| `Authorization: MaxInit <data>` | Альтернатива |
| `X-Max-User-Id` | Только при `ALLOW_INSECURE_INIT_DATA=true` |

### Основные эндпоинты

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/health` | Healthcheck |
| `POST` | `/users/onboarding` | Создать/обновить профиль |
| `GET` | `/users/me` | Текущий профиль |
| `PATCH` | `/users/me/skills` | Обновить навыки |
| `POST` | `/users/me/employer-opt-in` | Включить/выключить opt-in |
| `DELETE` | `/users/me` | Удалить профиль (152-ФЗ) |
| `GET` | `/skills/gap` | Skill Gap анализ |
| `GET` | `/plan` | Текущий план |
| `POST` | `/plan/regenerate` | Пересчитать план |
| `POST` | `/plan/steps/{id}/toggle` | Отметить шаг |
| `GET` | `/vacancies/recommendations` | Рекомендации вакансий |
| `POST` | `/users/me/resume` | Загрузить резюме (PDF/DOCX) |
| `POST` | `/ats/analyze` | ATS-анализ резюме |
| `POST` | `/coach/ask` | Вопрос AI-коучу |
| `GET` | `/gamification/progress` | XP, уровень, streak |
| `GET` | `/gamification/achievements` | Достижения |
| `GET` | `/compass/graph` | Граф навыков |
| `POST` | `/interview/sessions` | Старт интервью |
| `POST` | `/interview/sessions/{id}/answer` | Ответ на вопрос |
| `GET` | `/school/questions` | RIASEC-тест (школьники) |
| `POST` | `/school/evaluate` | Результат теста |
| `GET` | `/school/day-in-life` | Один день из жизни |
| `GET` | `/applications` | Отклики |
| `POST` | `/applications` | Создать отклик |
| `GET` | `/leaderboard` | Лидерборд |
| `GET` | `/simulator/scenarios` | Сценарии симулятора |
| `POST` | `/simulator/sessions` | Старт сессии |
| `POST` | `/simulator/sessions/{id}/choose` | Выбор варианта |
| `GET` | `/market/trends` | Тренды рынка |
| `GET` | `/market/forecast` | Прогноз навыков |
| `GET` | `/employer/v1/candidates/search` | Employer API |
| `POST` | `/webhook/max` | Webhook MAX |

Полная схема — в Swagger `/docs`.

---

## Деплой

### Архитектура прода

| Компонент | Платформа | URL |
|---|---|---|
| Backend | Wispbyte (Python 3.11, Docker) | https://mytestmaxbot.wisp.uno |
| Frontend | Vercel | https://frontend-coral-seven-71.vercel.app |
| PostgreSQL | Neon (Free) | внутр. |
| Бот | MAX Bot API | @se14433704_bot |

### Backend на Wispbyte

1. Создайте сервер с Python 3.11 в панели.
2. Загрузите `backend/` через файловый менеджер.
3. `.env` — заполните переменные (см. ниже).
4. **Startup Command**: `python run_both.py`
5. **Server Port**: 9727 (или ваш allocation).
6. `run_both.py` — скачает сертификаты Минцифры, применит миграции, запустит uvicorn + планировщик.

### Frontend на Vercel

```bash
cd frontend
npm i -g vercel
vercel login
vercel --prod
```

При деплое:
- Detected Vite
- Framework: Vite
- Build: `vite build`
- Output: `dist`

**Environment Variables:**

| Ключ | Значение |
|---|---|
| `VITE_API_BASE` | `https://mytestmaxbot.wisp.uno/api/v1` |

### Webhook MAX

Регистрация подписки:

```bash
curl -X POST "https://platform-api2.max.ru/subscriptions" \
  -H "Authorization: <MAX_BOT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://mytestmaxbot.wisp.uno/webhook/max",
    "update_types": ["message_created", "message_callback", "bot_started"],
    "secret": "<MAX_WEBHOOK_SECRET>"
  }'
```

**Требования MAX:**
- HTTPS на порту 443
- Валидный TLS-сертификат
- Ответ 200 в течение 30 секунд

### Сертификаты Минцифры

MAX API использует сертификаты НУЦ Минцифры. Для работы backend на Linux:

1. Скачать бандл: https://gu-st.ru/content/Other/doc/russiantrustedca.pem
2. Сохранить в `/home/container/russian_trusted.pem`
3. `run_both.py` автоматически скачивает при первом запуске.

Для локальной разработки на Windows — установить вручную в хранилище `Trusted Root`.

---

## Переменные окружения

### Backend (`.env`)

```dotenv
# База данных
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname?sslmode=require

# Источники данных
TRUDVSEM_BASE_URL=http://opendata.trudvsem.ru/api/v1
TRUDVSEM_TIMEOUT=15
TRUDVSEM_RETRIES=2

# CORS
CORS_ORIGINS=https://frontend-coral-seven-71.vercel.app,http://localhost:5173

# MAX
MAX_BOT_TOKEN=<токен>
MAX_WEBHOOK_SECRET=<секрет 32+ символа, только A-Za-z0-9_->
WEBAPP_URL=https://frontend-coral-seven-71.vercel.app
ALLOW_INSECURE_INIT_DATA=false

# Admin
ADMIN_SECRET=<случайная строка>

# Rate limits
RATE_LIMIT_ONBOARDING=10/minute
RATE_LIMIT_REGENERATE=5/minute
RATE_LIMIT_DEFAULT=120/minute
RATE_LIMIT_EMPLOYER=1000/hour

# Cache
CACHE_TTL_HOURS=8

# LLM (опционально)
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini

# Порт (для Wispbyte)
PORT=9727
```

### Frontend (`.env`)

```dotenv
VITE_API_BASE=https://mytestmaxbot.wisp.uno/api/v1
```

> **Важно:** в production **не задавайте** `VITE_DEV_USER_ID` — иначе фронт будет показывать чужой профиль.

---

## Структура проекта

```
careerpath-navigator/
├── backend/
│   ├── app/
│   │   ├── data/                # YAML словари, JSON сценарии симулятора
│   │   ├── routers/             # HTTP эндпоинты
│   │   ├── services/            # Бизнес-логика
│   │   ├── bot/                 # Регистрация webhook
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # pydantic-settings
│   │   ├── database.py          # SQLAlchemy engine
│   │   ├── models.py            # ORM
│   │   ├── schemas.py           # Pydantic
│   │   ├── dependencies.py      # get_current_user, get_employer
│   │   └── middleware.py        # rate limiter
│   ├── alembic/                 # Миграции
│   ├── tests/                   # pytest
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── run_both.py              # Точка входа для Wispbyte
│   ├── entrypoint.sh            # Для Docker
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── api/                 # REST-клиент
│   │   ├── components/          # Экраны
│   │   ├── hooks/               # useTheme, useVoiceInput
│   │   ├── i18n/                # ru/en переводы
│   │   ├── machines/            # XState для симулятора
│   │   ├── max/bridge.ts        # MAX Bridge wrapper
│   │   ├── ui/                  # Адаптер над MAX UI
│   │   ├── utils/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── styles.css
│   │   └── types.ts
│   ├── public/
│   ├── e2e/                     # Playwright
│   ├── index.html
│   ├── nginx.conf               # Для Docker
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── infra/
│   ├── prometheus/
│   └── grafana/
├── docs/
│   ├── architecture.md
│   ├── deploy.md
│   └── demo-script.md
├── .github/workflows/           # CI
├── compose.yaml
├── .env.example
├── .gitignore
├── Makefile
└── README.md
```

---

## Troubleshooting

### Backend

| Проблема | Решение |
|---|---|
| `relation "users" does not exist` | `alembic upgrade head` в контейнере |
| `CERTIFICATE_VERIFY_FAILED` к MAX | Установить сертификаты Минцифры или `verify=False` для httpx |
| `Field 'secret' does not match required pattern` | Секрет должен содержать только `A-Za-z0-9_-`, 5–256 символов |
| `Field 'webApp' cannot be null` | Для `open_app` использовать тип `link` или `web_app: "bot_username"` |
| `400 Can't deserialize body` | Кнопка `open_app` не поддерживает `web_app: {url}` — используйте `link` |
| `Missing 1 required positional argument: 'update'` | Проверить сигнатуру `handle_update` в `bot_commands.py` |
| CORS-ошибка | `CORS_ORIGINS` должен содержать точный домен фронта без слэша |
| `deadline exceeded` при pull образов | Настроить `registry-mirrors` в Docker Desktop |
| `EOF` при pull | Использовать зеркала `dockerhub.timeweb.cloud`, `mirror.gcr.io` |

### Frontend

| Проблема | Решение |
|---|---|
| Белая страница | F12 → Console, проверить ошибки JS |
| `hhtps://` в Network | Опечатка в `VITE_API_BASE`, пересоздать переменную на Vercel |
| `Cannot find module 'xstate'` | `npm install xstate @xstate/react` |
| `error TS...` | Проверить `npm run typecheck` локально |
| `Couldn't parse JSON` | Убрать BOM из `package.json` (сохранить как UTF-8 без BOM) |
| `Module not found: './ru/plan.json'` | Проверить наличие всех 14 файлов i18n |

### MAX Bot

| Проблема | Решение |
|---|---|
| Бот не отвечает | Проверить `/health` backend, логи webhook |
| `403 Invalid secret` | `MAX_WEBHOOK_SECRET` не совпадает с тем, что отправляет MAX |
| `401 Unauthorized` к MAX API | Сменить токен, он мог быть отозван |
| `HTTPS required` | MAX принимает только HTTPS на 443 |
| Кнопки не работают | Добавить `message_callback` в `update_types` подписки |

### Логи

```bash
# Backend (Docker)
docker compose logs -f backend

# Backend (Wispbyte)
# Вкладка Console в панели

# Frontend (Vercel)
vercel inspect <deployment-url> --logs

# MAX webhook
# Логи backend — все запросы на /webhook/max с payload
```

---

## Лицензия

MIT

## Команда

- Валерий — backend, бот MAX
- Валентина — frontend, UI

## Контакты

- GitHub: https://github.com/Valera1423/careerpath-navigator
- Бот в MAX: [@se14433704_bot](https://max.ru/@se14433704_bot)
