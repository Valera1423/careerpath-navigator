import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { AchievementData, ProgressData } from '../types';
import { Card } from '../ui';

const LEVEL_EMOJI: Record<string, string> = {
  intern: '🐣',
  junior: '🐥',
  middle: '🦅',
  senior: '🦉',
  lead: '🐉',
};

export function Tamagotchi() {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [achievements, setAchievements] = useState<AchievementData[]>([]);

  useEffect(() => {
    void Promise.all([api.progress(), api.achievements()]).then(([p, a]) => {
      setProgress(p);
      setAchievements(a);
    });
  }, []);

  if (!progress) return null;

  const emoji = LEVEL_EMOJI[progress.level] ?? '🐣';
  const pct =
    progress.next_threshold > progress.current_threshold
      ? Math.round(
          (100 * (progress.xp - progress.current_threshold)) /
            (progress.next_threshold - progress.current_threshold),
        )
      : 100;

  return (
    <Card>
      <div className="tamagotchi">
        <div className="tamagotchi__avatar">{emoji}</div>
        <div className="tamagotchi__info">
          <strong>{progress.level_label}</strong>
          <p className="muted small">
            {progress.xp} XP · до следующего: {pct}%
          </p>
        </div>
      </div>
      <div className="progress">
        <div className="progress__bar" style={{ width: `${pct}%` }} />
      </div>
      <p className="muted small">🔥 Streak: {progress.streak_days} дней</p>

      {achievements.length > 0 && (
        <div className="achievements">
          {achievements.map((a) => (
            <div key={a.id} className="achievement" title={a.description}>
              <span className="achievement__icon">🏅</span>
              <span className="achievement__title">{a.title}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}