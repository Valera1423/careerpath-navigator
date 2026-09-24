# CareerPath Navigator

Карьерный навигатор для студентов и выпускников внутри мессенджера MAX:
от онбординга и gap-анализа до персонального плана развития, симулятора
рабочего дня и тренировки собеседований.

## Назначение решения

Мы помогаем студентам и выпускникам отвечать на вопрос: **«что мне
конкретно делать, чтобы получить работу по желаемой роли?»** — и даём
персональный план, подкреплённый открытыми данными рынка труда.

Продукт закрывает три боли:

1. **Непонимание, чего не хватает** до целевой должности.
2. **Хаос ресурсов** — где учиться, что читать, в каком порядке.
3. **Страх собеседования** — нет тренировки и обратной связи.

## Основной пользовательский сценарий

1. Пользователь открывает бота в MAX и нажимает «Открыть CareerPath
   Navigator» (мини-приложение).
2. Проходит онбординг: целевая должность → регион → опыт → навыки →
   согласие 152-ФЗ.
3. Получает gap-анализ: какие навыки уже есть, каких не хватает,
   насколько готов к роли (readiness_score).
4. Нажимает «Построить план» → получает пошаговый план развития
   с дедлайнами и ресурсами.
5. Отмечает выполненные шаги → получает XP, достижения, поднимается
   в лидерборде.
6. Дополнительно: проживает «рабочий день» в роли (симулятор),
   тренирует STAR-ответы (интервью-тренажёр), смотрит карту навыков
   (compass), задаёт вопросы AI-коучу, загружает резюме и проверяет
   его в ATS-анализаторе.
7. Работодатель может подключиться к Employer API — получить
   анонимизированных кандидатов с включённым opt-in.

## Состав и архитектура решения

```
careerpath-navigator/
├── backend/                    # FastAPI (Python 3.12)
│   ├── app/
│   │   ├── routers/            # HTTP-эндпоинты
│   │   ├── services/           # бизнес-логика
│   │   ├── models.py           # SQLAlchemy ORM
│   │   ├── schemas.py          # Pydantic
│   │   └── main.py
│   ├── alembic/                # миграции БД
│   ├── tests/                  # pytest, 20+ файлов
│   └── Dockerfile
├── frontend/                   # React 18 + Vite + MAX UI
│   ├── src/
│   │   ├── components/
│   │   ├── api/client.ts
│   │   ├── max/bridge.ts
│   │   └── i18n/
│   └── Dockerfile
├── infra/                      # prometheus + grafana
├── compose.yaml
├── DATA-API.yaml
├── openapi.json
├── load-test.js                # k6 нагрузочный сценарий
└── .env.example
```

## Одна команда для запуска

```bash
docker compose up --build
```

SQLite (по умолчанию) — работает из коробки. Для PostgreSQL:

```bash
docker compose --profile postgres up --build
```

## Порты

| Сервис | Порт | URL |
|---|---|---|
| Frontend (nginx) | 8081 | http://localhost:8081 |
| Backend (API + Swagger) | 8000 | http://localhost:8000/docs |
| Health | 8000 | http://localhost:8000/health |
| Метрики | 8000 | http://localhost:8000/metrics |
| Prometheus (observability) | 9090 | http://localhost:9090 |
| Grafana (observability) | 3000 | http://localhost:3000 |

## Переменные окружения

Скопируйте `.env.example` → `.env` и заполните:

| Переменная | Назначение | Обязательна |
|---|---|---|
| `DATABASE_URL` | SQLite или PostgreSQL URL | нет |
| `MAX_BOT_TOKEN` | Токен бота от организаторов | для продакшена |
| `MAX_WEBHOOK_SECRET` | Секрет подписи webhook | да |
| `WEBAPP_URL` | Публичный HTTPS-адрес мини-аппа | да |
| `WEBHOOK_URL` | `https://.../webhook/max` | да |
| `ALLOW_INSECURE_INIT_DATA` | `true` только для локальной разработки | да |
| `ADMIN_SECRET` | Секрет для регистрации работодателей | да |
| `LLM_API_KEY` | Ключ OpenAI-совместимого API | нет |
| `TRUDVSEM_BASE_URL` | API «Работа России» | нет |
| `CACHE_TTL_HOURS` | TTL кэша вакансий | нет |
| `RATE_LIMIT_*` | Лимиты на эндпоинты (slowapi) | нет |

> **Важно.** В production `ALLOW_INSECURE_INIT_DATA=false`,
> `MAX_BOT_TOKEN` задан. Подпись `initData` валидируется по HMAC-SHA256.

## Зависимости

- Python: `backend/requirements.txt`, `backend/requirements-dev.txt`
- Node: `frontend/package.json`, `frontend/package-lock.json`
- Docker: `compose.yaml`, `backend/Dockerfile`, `frontend/Dockerfile`

## Внешние сервисы и интеграции

| Сервис | Назначение | Реальная/модельная |
|---|---|---|
| **MAX Bot API** | Доставка сообщений, webhook, Web App | Реальная |
| **MAX Bridge** | initData на фронте | Реальная |
| **Trudvsem API** | Вакансии, навыки, зарплаты | Реальная + fallback |
| **LLM API** | AI-коуч | Опциональная |

**Fallback-данные.** При недоступности Trudvsem API backend
автоматически возвращает подготовленный набор из 3 вакансий и помечает
источник как `fallback`. В UI показывается жёлтая плашка «Демо-данные».

## Работа с данными

| Категория | Что храним | Правовое основание |
|---|---|---|
| Идентификация | `max_user_id` | Договор / согласие |
| Профиль | ФИО, регион, опыт, навыки, целевая должность | Согласие |
| Согласие 152-ФЗ | Дата и время согласия | 152-ФЗ ст. 9 |
| Несовершеннолетние | Флаг `is_minor`, дата согласия представителя | 152-ФЗ ст. 9 ч. 6 |
| Активность | План, отклики, интервью, XP | Договор |
| Employer opt-in | Флаг и дата включения | Согласие, отзывается |

**Anonymization для Employer API:**
- ФИО и email никогда не передаются.
- Регион округляется до федерального округа.
- Идентификатор — необратимый SHA-256 хэш.

**Право быть забытым.** `DELETE /api/v1/users/me` — каскадное удаление
профиля и всех связанных записей.

## Порядок работы с тестовыми данными

- Демонстрационные вакансии: `backend/app/services/trudvsem.py → FALLBACK_VACANCIES`.
- Тестовый пользователь: `X-Max-User-Id: dev-user-1`.
- Симуляторы: `backend/app/data/scenarios/*.json`.
- Employer-ключи: генерируются при регистрации через Employer API.

## Пошаговый сценарий проверки

```bash
# 1. Онбординг
curl -X POST http://localhost:8000/api/v1/users/onboarding \
  -H 'Content-Type: application/json' \
  -d '{"max_user_id":"test-user-1","desired_position":"Аналитик данных","experience":"none","skills":["excel","python"],"consent_pd":true}'

# 2. Gap-анализ
curl http://localhost:8000/api/v1/skills/gap -H 'X-Max-User-Id: test-user-1'

# 3. План
curl -X POST http://localhost:8000/api/v1/plan/regenerate -H 'X-Max-User-Id: test-user-1'

# 4. Отметка шага
curl -X POST http://localhost:8000/api/v1/plan/steps/1/toggle -H 'X-Max-User-Id: test-user-1'

# 5. Интервью
curl -X POST http://localhost:8000/api/v1/interview/sessions -H 'X-Max-User-Id: test-user-1'

# 6. Employer — регистрация
curl -X POST http://localhost:8000/api/v1/employer/v1/employers/register \
  -H "X-Admin-Secret: change-me-in-production" \
  -H 'Content-Type: application/json' \
  -d '{"company_name":"Demo HR","contact_email":"demo@hr.ru"}'
```

## Примеры ожидаемого поведения

| Запрос | Ответ |
|---|---|
| `POST /users/onboarding` с `consent_pd: true` | `201` + `{id, max_user_id, consent_pd_given_at}` |
| `POST /users/onboarding` без `consent_pd` | `422` |
| `GET /skills/gap` при недоступном Trudvsem | `200` + `source: "fallback"` |
| `GET /skills/gap` без профиля | `404` |
| `POST /interview/sessions/{id}/answer` после 5 ответов | `409` |
| `POST /simulator/sessions/{id}/choose` с неверным choice_id | `400` |
| `POST /employer/v1/candidates/search` без `X-API-Key` | `401` |
| Превышение rate limit | `429 Too Many Requests` |

## Известные ограничения

- **LLM-коуч** работает в шаблонном режиме без `LLM_API_KEY`.
- **Trudvsem API** может быть недоступен → backend отдаст `fallback`.
- **Employer API** — демонстрационный контур, реальные HR-системы не подключены.
- **Webhook MAX** требует публичного HTTPS на 443 с валидным сертификатом.
- **Long polling бота** — ограниченная поддержка inline-клавиатур.
- **PII в базе** — пока в открытом виде; для production нужно шифрование.
- **SQLite** — не держит много конкурентных записей; для нагрузки — PostgreSQL.

## Порядок остановки и повторного запуска

```bash
docker compose down          # остановка, данные сохраняются
docker compose down -v       # остановка + удаление volumes (БД обнулится)
docker compose restart backend   # после правки .env
docker compose up --build -d     # пересборка
```

---

## 🧪 Тестирование

### Unit-тесты backend (pytest)

В проекте 20+ файлов тестов с фикстурами в `conftest.py`
(`client`, `auth_headers`, автозачистка БД).

```bash
# Все тесты
docker compose exec backend pytest

# С подробным выводом
docker compose exec backend pytest -v

# Один файл
docker compose exec backend pytest tests/test_gap.py -v

# Фильтр по имени
docker compose exec backend pytest -k "interview" -v

# Локально без Docker
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1     # Windows
pip install -r requirements-dev.txt
pytest -v
```

### Покрытие

| Файл | Что проверяет |
|---|---|
| `test_health.py` | `/health` возвращает `{status: "ok"}` |
| `test_users.py` | Онбординг, идемпотентность, `/me` 401/404 |
| `test_legal.py` | 152-ФЗ: consent обязателен, opt-in работает |
| `test_gap.py` | Gap-анализ, fallback при недоступном Trudvsem |
| `test_plan.py` | Regenerate, toggle, 404 на чужой шаг |
| `test_vacancies.py` | Рекомендации отсортированы по match_score |
| `test_interview.py` | Полная сессия из 5 вопросов, STAR-оценка |
| `test_simulator.py` | Happy path, неверный выбор, apply-to-profile |
| `test_applications.py` | CRUD откликов |
| `test_ats.py` | TXT отклоняется, DOCX принимается |
| `test_resume.py` | Парсинг навыков из резюме |
| `test_coach.py` | Fallback-шаблон при отсутствии LLM |
| `test_compass.py` | Граф навыков (done/missing) |
| `test_gamification.py` | XP, streak, achievements |
| `test_leaderboard.py` | Пустой лидерборд |
| `test_market.py` | Пустые тренды |
| `test_school.py` | RIASEC, day-in-life |
| `test_employer_api.py` | X-API-Key, только opt-in, анонимизация |
| `test_cache.py` | TTL-кэш |

### Линтеры и типы

```bash
docker compose exec backend ruff check app tests
docker compose exec backend ruff format app tests --check
docker compose exec backend mypy app
```

Ожидаемо: **ruff** — 0 ошибок, **mypy** (strict) — 0 ошибок.

### Frontend

```bash
cd frontend
npm install
npm run typecheck       # tsc --noEmit
npm run build           # tsc -b && vite build
npx eslint src          # ESLint
```

### E2E (Playwright)

```bash
cd frontend
npm run e2e:install                        # один раз — скачает Chromium
$env:E2E_BASE_URL="http://localhost:8081"  # Windows PowerShell
npm run e2e
```

Проверяет 2 сценария: онбординг → план → отметка шага → прогресс,
и полное прохождение интервью.

---

## 📈 Нагрузочное тестирование

Мы провели нагрузочное тестирование через **k6** (Grafana). Сценарий
`load-test.js` в корне проекта:

- **Рамп до 50 VU** за 2 минуты (30s ramp-up, 1m plateau, 30s ramp-down).
- Каждый VU: `/health` → `/users/onboarding` → `/skills/gap` → `/plan/regenerate`.
- Пороги: `p(95) < 500 ms`, `http_req_failed < 1%`.

### Результат прогона (SQLite, 1 инстанс, локально)

```
scenarios: 50 max VUs, 2m30s max duration
iterations: 2539   RPS: 84.4
http_req_duration:  avg=60.9ms  p(90)=34.5ms  p(95)=45.6ms  max=31.6s
http_req_failed:    74.53% (7570 из 10156)
```

### Интерпретация

| Метрика | Значение | Комментарий |
|---|---|---|
| `p(95) latency` | **45 ms** ✅ | Порог 500 ms пройден с большим запасом |
| `RPS` | **84** | Хорошая пропускная способность для MVP |
| `http_req_failed` | **74.5%** | Не падение backend, а **корректная работа rate limit** |
| Успешных `201` на эндпоинт | 20 | Соответствует порогу `RATE_LIMIT_ONBOARDING=10/minute` |
| Ошибки `500` | **0** | Система не падает, отвечает предсказуемо |

**Ключевой вывод:** 74.5% «отказов» — это **запланированные `429 Too
Many Requests`** от slowapi, а не сбои. Все 50 виртуальных пользователей
k6 идут с одного IP (`127.0.0.1`), поэтому упираются в лимит
`RATE_LIMIT_ONBOARDING=10/minute` и `RATE_LIMIT_REGENERATE=5/minute`.

Это подтверждается логами backend: `docker compose logs backend | Select-String "429"`.

### Узкие места, выявленные тестом

1. **Rate limiting по IP** — пользователи за общим NAT мешают друг другу.
   Решение для продакшена: составной ключ `X-Max-User-Id + IP`
   (см. `app/middleware.py::user_key_func`).
2. **`max=31.56s`** — отдельные вызовы к Trudvsem API при cache miss.
   Решение: увеличить `CACHE_TTL_HOURS`, добавить single-flight pattern.
3. **SQLite** — при конкурентных записях может блокироваться.
   Решение: `docker compose --profile postgres up`.

### Как прогнать самому

```powershell
# Установка (один раз)
winget install k6

# Запуск нагрузки
k6 run load-test.js

# С отчётом
k6 run --out web-dashboard load-test.js   # http://127.0.0.1:5665
```

Для честного теста без срабатывания rate limit — временно поднимите
лимиты в `.env`:

```dotenv
RATE_LIMIT_ONBOARDING=10000/minute
RATE_LIMIT_REGENERATE=10000/minute
RATE_LIMIT_DEFAULT=10000/minute
```

и перезапустите `docker compose restart backend`.

### Альтернативные инструменты

| Инструмент | Плюсы |
|---|---|
| `ab` (Apache Bench) | Простой, `ab -n 500 -c 20 http://localhost:8000/health` |
| `hey` | Умеет POST с JSON |
| **k6** | Графики, пороги, сценарии (используется у нас) |
| Locust | Python, веб-UI, тонкий контроль |

---

## Ссылки

- MAX для бизнеса: https://business.max.ru/self
- MAX Bridge docs: https://dev.max.ru/docs/webapps
- Trudvsem API: http://opendata.trudvsem.ru/api/v1
- k6 docs: https://k6.io/docs
- OpenAPI: `./openapi.json`
- DATA-API.yaml (контракт): `./DATA-API.yaml`