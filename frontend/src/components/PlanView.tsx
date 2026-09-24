import type { PlanResponse } from '../types';

interface Props {
  plan: PlanResponse | null;
  onToggle: (stepId: number) => void;
}

const KIND_LABEL: Record<string, string> = {
  course: 'Курс',
  project: 'Проект',
  practice: 'Практика',
};

function dueLabel(due: string | null): { text: string; color: string } | null {
  if (!due) return null;
  const dt = new Date(due);
  const days = Math.ceil((dt.getTime() - Date.now()) / 86_400_000);
  if (days < 0) return { text: `Просрочено на ${-days} дн.`, color: '#b3261e' };
  if (days === 0) return { text: 'Сегодня', color: '#b3261e' };
  if (days <= 3) return { text: `Через ${days} дн.`, color: '#8a6100' };
  return { text: `До ${dt.toLocaleDateString('ru-RU')}`, color: 'var(--muted)' };
}

export function PlanView({ plan, onToggle }: Props) {
  if (!plan || plan.total === 0) {
    return (
      <p className="muted">
        План пока пуст. Нажмите «Пересчитать план» на главном экране.
      </p>
    );
  }

  return (
    <div className="screen">
      {plan.steps.map((s) => {
        const dl = dueLabel((s as unknown as { due_date: string | null }).due_date ?? null);
        return (
          <label key={s.id} className={`step ${s.is_done ? 'step--done' : ''}`}>
            <input
              type="checkbox"
              checked={s.is_done}
              onChange={() => onToggle(s.id)}
              className="step__check"
            />
            <div className="step__body">
              <div className="step__meta">
                <span className="badge badge--kind">{KIND_LABEL[s.kind] ?? s.kind}</span>
                <span className="muted small">{s.skill}</span>
                {dl && (
                  <span className="small" style={{ color: dl.color, marginLeft: 'auto' }}>
                    {dl.text}
                  </span>
                )}
              </div>
              <strong className="step__title">{s.title}</strong>
              <p className="muted small">{s.description}</p>
              {s.resource_url && (
                <a className="link" href={s.resource_url} target="_blank" rel="noopener noreferrer">
                  Открыть материал →
                </a>
              )}
            </div>
          </label>
        );
      })}
    </div>
  );
}