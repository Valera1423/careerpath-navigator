import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { ForecastResponse } from '../types';
import { Card } from '../ui';

const TREND_ICON: Record<string, string> = {
  growing: '📈',
  declining: '📉',
  stable: '➡️',
};

export function ForecastCard() {
  const [data, setData] = useState<ForecastResponse | null>(null);

  useEffect(() => {
    api.forecast(6).then(setData).catch(() => undefined);
  }, []);

  if (!data || data.items.length === 0) return null;

  return (
    <Card>
      <h3>Прогноз на {data.horizon_months} мес.</h3>
      <p className="muted small">
        Оценка спроса на навыки на основе исторических данных.
      </p>
      <ul className="forecast">
        {data.items.slice(0, 5).map((i) => (
          <li key={i.skill}>
            <span className="forecast__icon">{TREND_ICON[i.trend] ?? '➡️'}</span>
            <span className="forecast__skill">{i.skill.replace('_', ' ')}</span>
            <span className="muted small">
              {i.current} → {i.predicted} ({i.change_pct > 0 ? '+' : ''}{i.change_pct}%)
            </span>
          </li>
        ))}
      </ul>
    </Card>
  );
}