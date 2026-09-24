import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { LeaderboardEntry } from '../types';
import { Card, Title } from '../ui';

const MEDALS = ['🥇', '🥈', '🥉'];

export function Leaderboard() {
  const [items, setItems] = useState<LeaderboardEntry[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.leaderboard(20).then(setItems).catch((e) => setError(String(e)));
  }, []);

  if (error) return <p className="error">{error}</p>;

  return (
    <div className="screen">
      <Title>Лидерборд</Title>
      {items.length === 0 && (
        <Card>
          <p className="muted">
            Пока никого нет. Выполняйте шаги плана и зарабатывайте XP — попадёте
            в топ.
          </p>
        </Card>
      )}
      {items.map((row) => (
        <div key={row.rank} className="leader-row">
          <span className="leader-row__rank">
            {MEDALS[row.rank - 1] ?? `#${row.rank}`}
          </span>
          <span className="leader-row__name">{row.display_name}</span>
          <span className="leader-row__level muted small">{row.level}</span>
          <span className="leader-row__xp">{row.xp} XP</span>
        </div>
      ))}
    </div>
  );
}