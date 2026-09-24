import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // разогрев до 20 VU
    { duration: '1m',  target: 50 },   // нагрузка 50 VU
    { duration: '30s', target: 0 },    // спад
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% < 500ms
    http_req_failed:   ['rate<0.01'],  // <1% ошибок
  },
};

const BASE = __ENV.BASE_URL || 'http://localhost:8000';

export default function () {
  // 1. Health
  let r = http.get(`${BASE}/health`);
  check(r, { 'health ok': (x) => x.status === 200 });

  // 2. Онбординг (каждый VU — свой пользователь)
  const userId = `load-user-${__VU}-${__ITER}`;
  r = http.post(
    `${BASE}/api/v1/users/onboarding`,
    JSON.stringify({
      max_user_id: userId,
      desired_position: 'Аналитик данных',
      experience: 'none',
      skills: ['excel'],
      consent_pd: true,
    }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  check(r, { 'onboarding 201': (x) => x.status === 201 });

  // 3. Gap-анализ
  r = http.get(`${BASE}/api/v1/skills/gap`, {
    headers: { 'X-Max-User-Id': userId },
  });
  check(r, { 'gap 200': (x) => x.status === 200 });

  // 4. План
  r = http.post(`${BASE}/api/v1/plan/regenerate`, null, {
    headers: { 'X-Max-User-Id': userId },
  });
  check(r, { 'plan 201': (x) => x.status === 201 });

  sleep(1);
}