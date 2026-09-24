import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { MarketTrends } from '../types';
import { Card, Title } from '../ui';

interface BarProps {
  value: number;
  max: number;
}

function HBar({ value, max }: BarProps) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="hbar">
      <div className="hbar__fill" style={{ width: `${pct}%` }} />
    </div>
  );
}

export function MarketDashboard() {
  const [data, setData] = useState<MarketTrends | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        setData(await api.marketTrends(30));
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <p className="muted">Считаем тренды…</p>;
  if (error) return <p className="error">{error}</p>;
  if (!data) return null;

  const maxSkill = Math.max(1, ...data.top_skills.map((s) => s.count));

  return (
    <div className="screen">
      <Title>Рынок за {data.period_days} дней</Title>

      <Card>
        <h3>Топ-10 навыков</h3>
        {data.top_skills.length === 0 && (
          <p className="muted">Пока нет данных — нажмите «Пересчитать план» на главной, чтобы заполнить кэш.</p>
        )}
        {data.top_skills.map((s) => (
          <div key={s.skill} className="skill-row">
            <span className="skill-row__name">{s.skill}</span>
            <HBar value={s.count} max={maxSkill} />
            <span className="skill-row__count">{s.count}</span>
          </div>
        ))}
      </Card>

      <Card>
        <h3>Зарплаты</h3>
        {data.salaries.sample > 0 ? (
          <>
            <p className="salary">{data.salaries.avg?.toLocaleString('ru-RU')} ₽ в среднем</p>
            <p className="muted small">
              Диапазон: {data.salaries.min?.toLocaleString('ru-RU')} —{' '}
              {data.salaries.max?.toLocaleString('ru-RU')} ₽ (по {data.salaries.sample} вакансиям)
            </p>
          </>
        ) : (
          <p className="muted small">Нет данных о зарплатах</p>
        )}
      </Card>

      <Card>
        <h3>Топ-5 компаний</h3>
        {data.top_companies.length === 0 && <p className="muted small">Нет данных</p>}
        <ul className="companies">
          {data.top_companies.map((c) => (
            <li key={c.company}>
              <span>{c.company}</span>
              <span className="muted small">{c.vacancies}</span>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}