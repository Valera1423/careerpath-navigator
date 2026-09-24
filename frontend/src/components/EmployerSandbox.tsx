import { useState } from 'react';
import { Card, Input, Title } from '../ui';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';

interface Candidate {
  candidate_id: string;
  region: string | null;
  experience: string;
  desired_position: string;
  match_score: number;
  matched_skills: string[];
  skills: { name: string; verified: boolean; evidence: string | null }[];
  plan_progress: string | null;
  verified_count: number;
  total_skills: number;
}

export function EmployerSandbox() {
  const [apiKey, setApiKey] = useState('');
  const [position, setPosition] = useState('Аналитик данных');
  const [skills, setSkills] = useState('sql, python');
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = async () => {
    if (!apiKey.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_BASE}/employer/v1/candidates/search?position=${encodeURIComponent(position)}&skills=${encodeURIComponent(skills)}`,
        { headers: { 'X-API-Key': apiKey } },
      );
      if (!res.ok) {
        setError(`Ошибка ${res.status}: ${res.statusText}`);
        setCandidates([]);
        return;
      }
      const data = await res.json();
      setCandidates(data.items ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="screen">
      <Title>Employer API — песочница</Title>

      {/* ТЗ стр. 8 п.4 — не имитируйте интеграции, явно помечайте демо-данные */}
      <div className="notice">
        🔬 <strong>Демо-контур для хакатона.</strong> В MVP нет реальных
        интеграций с HR-системами. Поиск кандидатов работает на данных
        мини-приложения (студенты с включённым opt-in). Адрес, OpenAPI и
        контракт описаны в <code>openapi.json</code> и{' '}
        <code>DATA-API.yaml</code> в корне репозитория.
      </div>

      <p className="muted">
        Получите ключ через{' '}
        <code>POST /employer/v1/employers/register</code> (требует{' '}
        <code>X-Admin-Secret</code>).
      </p>

      <Card>
        <h3>Параметры запроса</h3>
        <Input
          placeholder="API-ключ (cp_...)"
          value={apiKey}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setApiKey(e.target.value)}
        />
        <Input
          placeholder="Должность"
          value={position}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPosition(e.target.value)}
        />
        <Input
          placeholder="Навыки через запятую"
          value={skills}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
        />
        <button className="btn" onClick={search} disabled={loading || !apiKey.trim()}>
          {loading ? 'Ищем…' : 'Найти кандидатов'}
        </button>
        {error && <p className="error">{error}</p>}
      </Card>

      {candidates.length > 0 && (
        <Card>
          <h3>Найдено: {candidates.length}</h3>
          <p className="muted small">
            ФИО, контакты и точный ID не передаются. Регион округлён до
            федерального округа, идентификатор — необратимый хэш.
          </p>
          {candidates.map((c) => (
            <div key={c.candidate_id} className="candidate">
              <div className="candidate__head">
                <strong>{c.desired_position}</strong>
                <span className="badge badge--match">{c.match_score}%</span>
              </div>
              <p className="muted small">
                ID: {c.candidate_id} · Регион: {c.region ?? '—'} · Опыт: {c.experience}
              </p>
              <p className="muted small">
                Верифицировано: {c.verified_count} из {c.total_skills}
              </p>
              <div className="chips">
                {c.skills.map((s) => (
                  <span
                    key={s.name}
                    className={s.verified ? 'chip chip--verified' : 'chip'}
                    title={s.evidence ?? 'Не подтверждено'}
                  >
                    {s.verified ? '✓ ' : ''}{s.name}
                  </span>
                ))}
              </div>
              <p className="muted small">Прогресс плана: {c.plan_progress ?? '—'}</p>
            </div>
          ))}
        </Card>
      )}

      {candidates.length === 0 && !loading && !error && apiKey && (
        <Card>
          <p className="muted">
            Кандидаты не найдены. Убедитесь, что студенты включили opt-in
            в настройках мини-приложения.
          </p>
        </Card>
      )}
    </div>
  );
}