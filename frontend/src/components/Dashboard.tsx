import { useTranslation } from 'react-i18next';
import type { PlanResponse, SkillGapResponse, UserProfile } from '../types';
import { EmptyState } from '../ui/EmptyState';
import { SkeletonCard } from '../ui/Skeleton';
import { ForecastCard } from './ForecastCard';
import { MarketComparison } from './MarketComparison';
import { ResumeUpload } from './ResumeUpload';
import { Tamagotchi } from './Tamagotchi';

interface Props {
  profile: UserProfile;
  gap: SkillGapResponse | null;
  plan: PlanResponse | null;
  onRegenerate: () => void;
  regenerating: boolean;
  onProfileUpdated: () => void;
}

export function Dashboard({
  profile,
  gap,
  plan,
  onRegenerate,
  regenerating,
  onProfileUpdated,
}: Props) {
  const { t } = useTranslation('dashboard');

  const importanceLabel = (key: string) =>
    t(`importance.${key}`, { defaultValue: key });

  return (
    <div className="screen">
      <header className="header">
        <h2>{profile.desired_position}</h2>
        <p className="muted">
          {profile.region || 'Регион не указан'} · опыт: {profile.experience}
        </p>
      </header>

      <Tamagotchi />

      <div className="card">
        <div className="score">
          <span className="score__value">{gap?.readiness_score ?? '—'}%</span>
          <span className="muted">{t('readiness')}</span>
        </div>
        <div className="progress">
          <div
            className="progress__bar"
            style={{ width: `${plan?.progress_percent ?? 0}%` }}
          />
        </div>
        <p className="muted">
          {t('plan_progress', {
            done: plan?.done ?? 0,
            total: plan?.total ?? 0,
          })}
        </p>
        <button
          className="btn btn--ghost"
          onClick={onRegenerate}
          disabled={regenerating}
        >
          {regenerating ? t('regenerating') : t('regenerate')}
        </button>
      </div>

      {!gap && <SkeletonCard />}

      {gap && gap.missing.length === 0 && (
        <EmptyState
          icon="🎉"
          title={t('missing_title')}
          description={t('missing_empty')}
        />
      )}

      {gap && gap.missing.length > 0 && (
        <div className="card">
          <h3>{t('missing_title')}</h3>
          <ul className="gap-list">
            {gap.missing.slice(0, 8).map((i) => (
              <li key={i.skill}>
                <span className="skill">{i.skill.replace('_', ' ')}</span>
                <span className={`badge badge--${i.importance}`}>
                  {importanceLabel(i.importance)}
                </span>
                <span className="muted small">
                  {t('share_of_vacancies', {
                    percent: Math.round(i.demand_share * 100),
                  })}
                </span>
              </li>
            ))}
          </ul>
          <p className="muted small">
            {t('analyzed', {
              count: gap.vacancies_analyzed,
              source:
                gap.source === 'trudvsem'
                  ? t('source_trudvsem')
                  : t('source_fallback'),
            })}
          </p>
        </div>
      )}

      {gap && <MarketComparison gap={gap} />}
      <ForecastCard />
      <ResumeUpload onUploaded={onProfileUpdated} />
    </div>
  );
}