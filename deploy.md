# Инструкция по деплою

## Компоненты прода

| Компонент | Платформа | Стоимость |
|---|---|---|
| Backend | Wispbyte (Python 3.11) | Free |
| Frontend | Vercel | Free |
| PostgreSQL | Neon | Free |
| Бот MAX | platform-api2.max.ru | Free |

## 1. PostgreSQL (Neon)

1. Зарегистрируйтесь на [neon.tech](https://neon.tech).
2. Создайте проект `careerpath`.
3. Скопируйте Connection String:
postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

text
4. Преобразуйте для psycopg:
postgresql+psycopg://user:pass@ep-xxx.neon.tech/dbname?sslmode=require

text

## 2. Backend (Wispbyte)

### 2.1 Подготовка

Убедитесь, что в `backend/` есть:
- `run_both.py` — точка входа
- `requirements.txt` — без `asyncpg`, без `numpy`, без `reportlab`
- `alembic/` с миграциями
- `app/` целиком

### 2.2 Загрузка

1. Создайте сервер `Python 3.11` в панели Wispbyte.
2. Загрузите `backend/` через файловый менеджер.
3. Распакуйте так, чтобы `run_both.py` был в корне.

### 2.3 `.env`

Создайте файл `.env` в корне контейнера:

```dotenv
DATABASE_URL=postgresql+psycopg://...
MAX_BOT_TOKEN=<токен>
MAX_WEBHOOK_SECRET=<секрет>
WEBAPP_URL=https://frontend-xxx.vercel.app
ALLOW_INSECURE_INIT_DATA=false
CORS_ORIGINS=https://frontend-xxx.vercel.app
ADMIN_SECRET=<случайная>
PORT=9727
2.4 Startup
Main File: run_both.py

Startup Command: python run_both.py

Port: 9727 (или ваш из панели)

2.5 Проверка
bash
curl https://<ваш-домен>/health
# {"status":"ok","service":"CareerPath Navigator API"}
3. Frontend (Vercel)
3.1 Через CLI
bash
cd frontend
npm i -g vercel
vercel login
vercel --prod
Ответы:

Set up and deploy — Y

Which scope — ваш аккаунт

Link to existing — N

Project name — careerpath-navigator-frontend

Directory — ./

Modify settings — N

3.2 Environment Variables
bash
vercel env add VITE_API_BASE production
# Значение: https://<ваш-backend>.wisp.uno/api/v1
Не добавляйте VITE_DEV_USER_ID в production.

3.3 Передеплой
bash
vercel --prod
4. Бот MAX
4.1 Регистрация
Откройте business.max.ru/self.

Создайте бота → получите токен.

В настройках укажите URL мини-приложения = ваш Vercel URL.

4.2 Webhook
bash
curl -X POST "https://platform-api2.max.ru/subscriptions" \
  -H "Authorization: <MAX_BOT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://<backend>.wisp.uno/webhook/max",
    "update_types": ["message_created", "message_callback", "bot_started"],
    "secret": "<MAX_WEBHOOK_SECRET>"
  }'
Требования:

HTTPS на 443

Доверенный TLS-сертификат

Ответ 200 в течение 30 секунд

4.3 Проверка
Откройте бота в MAX.

Напишите /start.

Должен ответить приветствием с кнопками.

5. Сертификаты Минцифры
MAX API использует TLS-сертификаты НУЦ Минцифры. На Linux они отсутствуют.

Автоматическая установка (в run_both.py)
python
CERT_URL = "https://gu-st.ru/content/Other/doc/russiantrustedca.pem"
CERT_PATH = BASE_DIR / "russian_trusted.pem"

if not CERT_PATH.exists():
    # скачать
Ручная (локально)
Windows:

Скачать windows_russian_trusted_root_ca.zip и russian_trusted_sub_ca.zip с gu-st.ru.

Распаковать.

Установить корневые в Cert:\CurrentUser\Root, промежуточные в Cert:\CurrentUser\CA.

Linux:

bash
curl -o /usr/local/share/ca-certificates/russian_trusted.pem \
  https://gu-st.ru/content/Other/doc/russiantrustedca.pem
update-ca-certificates
6. Обновление деплоя
Backend
Загрузить изменённые файлы через файловый менеджер.

Restart в панели.

Или (если включён git):

bash
git push
# Автоматический webhook от Wispbyte (если настроен)
Frontend
bash
git push
# Vercel автоматически пересоберёт
Или вручную:

bash
vercel --prod
7. Откат
Vercel
Deployments → выбрать предыдущий → Promote to Production.

Wispbyte
Хранить бэкапы в .zip перед крупными изменениями. Откат — распаковать архив и Restart.

8. Мониторинг
Healthcheck
bash
curl https://<backend>/health
Логи
Backend — вкладка Console в панели Wispbyte

Frontend — Vercel Dashboard → Deployments → Logs

MAX webhook — в логах backend

Метрики
bash
curl https://<backend>/metrics | grep trudvsem
9. Чек-лист деплоя
□ PostgreSQL создан, миграции применены
□ Backend отвечает на /health
□ /docs открывается
□ Frontend задеплоен на Vercel
□ VITE_API_BASE указывает на backend
□ VITE_DEV_USER_ID не установлен
□ CORS настроен на домен Vercel
□ Webhook MAX зарегистрирован
□ Бот отвечает на /start
□ Mini App открывается из MAX
□ Онбординг создаёт профиль
text

---

## `docs/testing.md`

```markdown
# Руководство по тестированию

## Уровни тестирования

| Уровень | Инструмент | Покрытие |
|---|---|---|
| Unit | pytest | services, утилиты |
| Integration | pytest + respx | роутеры + БД |
| E2E | Playwright | happy path |
| Manual | curl + браузер | приёмочное |

## Backend тесты

### Установка

```bash
cd backend
pip install -r requirements-dev.txt
Запуск
bash
# Все
pytest

# С покрытием
pytest --cov=app --cov-report=html
# open htmlcov/index.html

# Один файл
pytest tests/test_users.py -v

# Один тест
pytest tests/test_users.py::test_onboarding_creates_profile -v

# По маркеру
pytest -m "not slow"
Структура
text
tests/
├── conftest.py                  # фикстуры (client, auth_headers, clean_db)
├── test_health.py
├── test_users.py                # онбординг, /me, 401/404/422
├── test_gap.py                  # skill gap + fallback
├── test_plan.py                 # regenerate, toggle
├── test_vacancies.py
├── test_resume.py               # PDF/DOCX
├── test_ats.py
├── test_market.py
├── test_cache.py
├── test_gamification.py
├── test_compass.py
├── test_coach.py
├── test_interview.py
├── test_applications.py
├── test_school.py
├── test_legal.py                # 152-ФЗ
├── test_employer_api.py
├── test_simulator.py
└── fixtures/
    ├── resume_analyst.pdf
    └── resume_designer.docx
Фикстуры
python
# conftest.py

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def auth_headers():
    return {"X-Max-User-Id": "test-user-1"}
Мок внешних API
python
import respx
from httpx import Response

@respx.mock
def test_gap_falls_back(client):
    respx.get(url__startswith="http://opendata.trudvsem.ru").mock(
        return_value=Response(500)
    )
    # тест использует fallback-данные
Frontend тесты
Typecheck
bash
cd frontend
npm run typecheck
Сборка
bash
npm run build
# результат в dist/
E2E (Playwright)
bash
npm run e2e:install
E2E_BASE_URL=http://localhost:8080 npm run e2e
Сценарии в frontend/e2e/:

happy-path.spec.ts — онбординг → план → toggle

interview.spec.ts — полное прохождение интервью

Ручное тестирование
Backend через curl
bash
# Health
curl http://localhost:8000/health

# Онбординг
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

# Gap
curl http://localhost:8000/api/v1/skills/gap \
  -H 'X-Max-User-Id: test-user-1' | python -m json.tool

# План
curl -X POST http://localhost:8000/api/v1/plan/regenerate \
  -H 'X-Max-User-Id: test-user-1'

curl -X POST http://localhost:8000/api/v1/plan/steps/1/toggle \
  -H 'X-Max-User-Id: test-user-1'

# Вакансии
curl 'http://localhost:8000/api/v1/vacancies/recommendations?limit=5' \
  -H 'X-Max-User-Id: test-user-1'

# Интервью
curl -X POST http://localhost:8000/api/v1/interview/sessions \
  -H 'X-Max-User-Id: test-user-1'
Frontend вручную
Открыть http://localhost:8080 (или Vercel URL)

Пройти онбординг

Проверить дашборд — % готовности, gap-список

Отметить 2 шага плана

Проверить геймификацию (XP, достижения)

Открыть компас

Пройти симулятор интервью

Открыть настройки, сменить язык и тему

Проверить opt-in

Чек-лист приёмочного тестирования
Функциональность
□ Онбординг принимает все поля, создаёт профиль
□ Gap-анализ показывает matched / missing
□ План генерируется с курсами и проектами
□ Toggle шага увеличивает прогресс и XP
□ Достижения разблокируются
□ Вакансии сортируются по match_score
□ ATS-анализ возвращает score и рекомендации
□ Интервью даёт STAR-оценку
□ Симулятор проходит до конца
□ Компас строит граф с зависимостями
Нефункциональные
□ Мобильная вёрстка работает
□ Тёмная тема переключается
□ Язык переключается
□ Loading-скелетоны отображаются
□ Empty state показывается корректно
□ Согласие 152-ФЗ обязательно
□ Opt-in влияет на Employer API
Edge cases
□ Пустой список навыков — gap не падает
□ «Работа России» недоступна — используется fallback
□ LLM недоступна — коуч отвечает шаблоном
□ Долгая генерация плана — фронт показывает прогресс
□ Потеря соединения — фронт не ломается
