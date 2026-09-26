# Безопасность и 152-ФЗ

## Аутентификация

### Production (обязательно)

Все запросы к API должны содержать заголовок `X-Max-Init-Data` —
строку, полученную из `window.WebApp.initData`. Backend валидирует
HMAC-SHA256 подпись с бот-токеном:

```python
def verify_init_data(raw: str) -> MaxUser:
    pairs = parse_qsl(raw)
    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(pairs) if k != "hash"
    )
    secret = hmac.new(b"WebAppData", bot_token.encode(), sha256).digest()
    expected = hmac.new(secret, data_check_string.encode(), sha256).hexdigest()
    received = next((v for k, v in pairs if k == "hash"), None)
    if not hmac.compare_digest(expected, received):
        raise HTTPException(401)
TTL: 1 час. Если auth_date старше — 401.

Dev
При ALLOW_INSECURE_INIT_DATA=true принимается заголовок X-Max-User-Id.
Никогда не включайте в production.

152-ФЗ
Что делаем
Согласие при онбординге — обязательный чекбокс, фиксируется в consent_pd_given_at.

Opt-in для передачи данных — по умолчанию выключено.

Анонимизация для работодателей — ФИО, email, точный ID не передаются.

Регион округляется до федерального округа.

DELETE /users/me — полное удаление профиля и связанных данных.

Что передаётся в Employer API
Данные	Передаётся
ФИО	❌
Email	❌
Точный user_id	❌
Регион (округ)	✅
Опыт	✅
Навыки	✅
Match score	✅
Rate limiting
Endpoint	Лимит
/users/onboarding	10/min
/plan/regenerate	5/min
/employer/v1/*	1000/hour
default	120/min
Реализовано через slowapi. Ключ для employer — API-ключ, для остальных — IP.

Валидация входа
Все входные данные проходят через Pydantic:

Строки с min_length / max_length

Enum для experience, status

Числа с ge / le

Секреты
.env — не коммитится

.env.example — только заглушки

В коде нет хардкода токенов

Ротация токена бота при компрометации

HTTPS
Production: Let's Encrypt на Wispbyte + Cloudflare

Webhook MAX: только HTTPS на 443, валидный TLS

Сертификаты Минцифры для API MAX (автоматически через run_both.py)

Логирование
Все запросы к /webhook/max логируются с payload (без PII).
Ошибки — с traceback. PII не пишется в логи.

text

---

## `docs/api.md`

```markdown
# API Reference

**Base URL:** `https://mytestmaxbot.wisp.uno/api/v1`  
**Swagger:** `/docs`  
**OpenAPI JSON:** `/openapi.json`

## Аутентификация

Все защищённые эндпоинты требуют один из заголовков:

| Заголовок | Описание |
|---|---|
| `X-Max-Init-Data` | Строка `initData` от MAX Bridge |
| `Authorization: MaxInit <data>` | Альтернативный формат |
| `X-Max-User-Id` | Только dev (при `ALLOW_INSECURE_INIT_DATA=true`) |

## Users

### POST /users/onboarding

Создать или обновить профиль.

**Body:**
```json
{
  "max_user_id": "161808638",
  "full_name": "Валерий",
  "desired_position": "Аналитик данных",
  "region": "Москва",
  "experience": "none",
  "skills": ["excel", "python"],
  "consent_pd": true
}
Response 201:

json
{
  "id": 1,
  "max_user_id": "161808638",
  "full_name": "Валерий",
  "desired_position": "Аналитик данных",
  "region": "Москва",
  "experience": "none",
  "skills": ["excel", "python"],
  "created_at": "2026-09-26T13:56:21Z",
  "consent_pd_given_at": "2026-09-26T13:56:21Z",
  "employer_opt_in": false
}
GET /users/me
Текущий профиль.

PATCH /users/me/skills
Body:

json
{ "skills": ["excel", "python", "sql"] }
POST /users/me/employer-opt-in
Body:

json
{ "employer_opt_in": true }
DELETE /users/me
Полное удаление профиля (152-ФЗ).

Career
GET /skills/gap
Skill gap анализ.

Response:

json
{
  "position": "Аналитик данных",
  "region": "Москва",
  "vacancies_analyzed": 30,
  "source": "trudvsem",
  "matched": [{"skill": "excel", "demand": 15, "demand_share": 0.5, "importance": "critical"}],
  "missing": [{"skill": "sql", "demand": 25, "demand_share": 0.83, "importance": "critical"}],
  "readiness_score": 45
}
GET /plan
Текущий план.

POST /plan/regenerate
Пересчитать план на основе текущего gap.

POST /plan/steps/{id}/toggle
Отметить шаг выполненным/невыполненным. Начисляет XP.

Vacancies
GET /vacancies/recommendations?limit=8
Рекомендации вакансий.

Resume / ATS
POST /users/me/resume
Multipart form: file (PDF или DOCX).

POST /ats/analyze
Multipart form: file, vacancy_text.

Coach
POST /coach/ask
Body:

json
{ "question": "Зачем мне SQL?" }
Gamification
GET /gamification/progress
Response:

json
{
  "xp": 150,
  "level": "junior",
  "level_label": "Junior",
  "current_threshold": 200,
  "next_threshold": 600,
  "streak_days": 3
}
GET /gamification/achievements
Список полученных достижений.

Compass
GET /compass/graph
Response:

json
{
  "nodes": [{"id": "python", "data": {"label": "python", "status": "done"}}],
  "edges": [{"id": "python->pandas", "source": "python", "target": "pandas"}]
}
Interview
POST /interview/sessions
Начать сессию. Response: первый вопрос.

POST /interview/sessions/{id}/answer
Body:

json
{ "answer": "Когда я работал над проектом..." }
Response:

json
{
  "score": 10,
  "feedback": "Отличная структура!",
  "structure": {"situation": true, "task": true, "action": true, "result": true},
  "next_question": "...",
  "is_finished": false
}
School
GET /school/questions
18 RIASEC-вопросов.

POST /school/evaluate
Body:

json
{ "answers": {"1": 2, "2": 1, ...} }
GET /school/day-in-life?profession=Аналитик данных
Applications
GET /applications
POST /applications
Body:

json
{
  "vacancy_id": "v-1",
  "vacancy_title": "Аналитик данных",
  "company": "Test",
  "remind_in_days": 7
}
Employer API
POST /employer/v1/employers/register
Защищено X-Admin-Secret.

GET /employer/v1/candidates/search
Требует X-API-Key. Возвращает только opt-in кандидатов.

Query:

position (обязательно)

skills (через запятую)

region

limit

GET /employer/v1/candidates/{id}
Simulator
GET /simulator/scenarios
POST /simulator/sessions?scenario_id=data_analyst_day
POST /simulator/sessions/{id}/choose
Body:

json
{ "choice_id": "check_sql" }
POST /simulator/sessions/{id}/apply-to-profile
Применить gaps из симулятора к плану.

Webhook
POST /webhook/max
Принимает события от MAX. Требует заголовок X-Max-Bot-Api-Secret.

Errors
Код	Значение
400	Невалидные данные
401	Нет авторизации
403	Неверный secret / API-key
404	Профиль не найден
409	Конфликт (шаг уже выполнен, подписка существует)
422	Ошибка валидации Pydantic
429	Rate limit
500	Внутренняя ошибка
text

---
