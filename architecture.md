# Архитектура CareerPath Navigator

## Общая схема
┌─────────────────────────────────────────────────────────────────┐
│ MAX Messenger │
│ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ │
│ │ Чат с ботом │ │ Mini App │ │ Bridge API │ │
│ └────────┬───────┘ └────────┬───────┘ └────────┬───────┘ │
└───────────┼───────────────────┼───────────────────┼─────────────┘
│ webhook │ REST │ initData
▼ ▼ ▼
┌─────────────────────────────────────────────────────────────────┐
│ Backend (FastAPI) │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Routers: users, career, coach, gamification, ... │ │
│ └────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ Services: gap, plan, trudvsem, coach, gamification... │ │
│ └────────────────────────────────────────────────────────┘ │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ ORM: SQLAlchemy 2.0 + Alembic │ │
│ └────────────────────────────────────────────────────────┘ │
└────────────┬───────────────────┬───────────────────┬────────────┘
│ │ │
▼ ▼ ▼
┌────────────┐ ┌────────────┐ ┌────────────┐
│ PostgreSQL │ │ «Работа │ │ MAX Bot │
│ (Neon) │ │ России» │ │ API │
└────────────┘ └────────────┘ └────────────┘

text

## Backend: слои

### 1. Routers (`app/routers/`)

Обрабатывают HTTP-запросы, валидируют входные данные через Pydantic, вызывают сервисы, возвращают ответы. Никакой бизнес-логики.

- `users.py` — онбординг, профиль, opt-in
- `career.py` — gap-анализ, план, вакансии
- `coach.py` — AI-коуч
- `gamification.py` — XP, уровни, достижения
- `compass.py` — граф навыков
- `interview.py` — симулятор интервью
- `school.py` — RIASEC-тест
- `applications.py` — трекер откликов
- `leaderboard.py` — лидерборд
- `employer_api.py` — публичный API для HR
- `simulator.py` — карьерный симулятор дня
- `webhook.py` — приём событий от MAX
- `ats.py`, `resume.py`, `market.py`, `market_forecast.py`, `portfolio.py`, `export.py` — доп. функции

### 2. Services (`app/services/`)

Бизнес-логика. Не знают ничего о HTTP.

| Сервис | Назначение |
|---|---|
| `trudvsem.py` | Клиент API «Работа России» |
| `gap.py` | Skill gap анализ |
| `plan.py` | Генерация плана развития |
| `skills.py` | Извлечение навыков из YAML |
| `coach.py` | AI-коуч (LLM + fallback) |
| `llm_client.py` | Обёртка над OpenAI-совместимым API |
| `gamification.py` | XP, уровни, достижения |
| `compass.py` | Граф зависимостей навыков |
| `interview.py` | STAR-оценка |
| `career_test.py` | RIASEC-тест |
| `simulator.py` | Сценарии симулятора |
| `anonymization.py` | Анонимизация для HR |
| `api_keys.py` | Генерация API-ключей |
| `max_auth.py` | Валидация initData |
| `max_api.py` | Клиент MAX Bot API |
| `market.py`, `market_forecast.py` | Аналитика рынка |
| `resume.py`, `ats.py`, `portfolio.py`, `export.py` | Доп. функции |
| `cache.py` | TTL-кэш |
| `metrics.py` | Prometheus-метрики |
| `scheduler.py` | Планировщик напоминаний |

### 3. Data (`app/data/`)

- `skills.yaml` — 100+ паттернов навыков
- `roles.yaml` — профили ролей, core-навыки, зависимости
- `scenarios/*.json` — сценарии симулятора

## Модели данных
User ─┬─▶ PlanStep
├─▶ UserProgress
├─▶ Achievement
├─▶ Application
├─▶ InterviewSession
├─▶ SimulatorSession
├─▶ StudentVerification
└─▶ AnalyticsEvent

EmployerAccount ─┬─▶ EmployerAccessLog
└─▶ (по API-ключу)

VacancyCache — независимая

text

## Frontend: слои

### 1. API-клиент (`src/api/`)

- `client.ts` — типизированный fetch с автоматическим `X-Max-Init-Data`
- Все запросы идут через единый `request()` с обработкой ошибок

### 2. MAX Bridge (`src/max/bridge.ts`)

- `getInitData()` — строка для серверной валидации
- `getMaxUserId()` — только для UI-подсказок
- `initMax()` — вызов `ready()` + `expand()`

### 3. UI-адаптер (`src/ui/`)

Единственное место, зависящее от `@dementevdev/max-ui`. Если компонент есть в библиотеке — используется он, иначе — нативный фолбэк.

### 4. Компоненты (`src/components/`)

- Онбординг, дашборд, план, вакансии
- Симулятор, интервью, компас, коуч
- ATS, отклики, лидерборд, настройки

### 5. State

- XState-машина для симулятора (`machines/simulatorMachine.ts`)
- React state + hooks для остального

## Безопасность

### 1. Аутентификация

| Способ | Когда | Проверка |
|---|---|---|
| `X-Max-Init-Data` | Production | HMAC-SHA256 по бот-токену, TTL 1 час |
| `X-Max-User-Id` | Dev | Только при `ALLOW_INSECURE_INIT_DATA=true` |
| `X-API-Key` | Employer API | bcrypt |

### 2. Rate limiting

- `onboarding` — 10/min
- `plan/regenerate` — 5/min
- `employer/*` — 1000/hour
- `default` — 120/min

### 3. 152-ФЗ

- `consent_pd_given_at` — фиксируется при онбординге
- `employer_opt_in` — по умолчанию `false`
- Анонимизация в Employer API: имя, email, точный ID не передаются
- Регион округляется до федерального округа
- `DELETE /users/me` — полное удаление

## Производительность

- TTL-кэш (8 часов) для выдачи «Работы России»
- Rate limiting 2 req/s на один диалог в MAX
- Пул соединений с БД `pool_size=1` (serverless-friendly)
- Skeleton-загрузка на фронте
- Code splitting через Vite
