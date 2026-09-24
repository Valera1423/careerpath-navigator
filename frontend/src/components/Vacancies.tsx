import { useState } from 'react';
import { api } from '../api/client';
import type { RecommendationsResponse } from '../types';
import { Button } from '../ui';
import { DataBadge } from './DataBadge';
import { EmptyState } from '../ui/EmptyState';
import { showToast } from '../ui/Toast';

interface Props {
  data: RecommendationsResponse | null;
}

export function Vacancies({ data }: Props) {
  const [sent, setSent] = useState<Record<string, boolean>>({});
  const [busy, setBusy] = useState<string | null>(null);

  const apply = async (
    vacancyId: string,
    title: string,
    url: string | null,
    company: string,
  ) => {
    setBusy(vacancyId);
    try {
      await api.createApplication({
        vacancy_id: vacancyId,
        vacancy_title: title,
        vacancy_url: url,
        company,
        remind_in_days: 7,
      });
      setSent((s) => ({ ...s, [vacancyId]: true }));
      showToast('Отклик сохранён. Напомним через 7 дней.', 'success');
    } catch (e) {
      showToast(e instanceof Error ? e.message : 'Ошибка', 'error');
    } finally {
      setBusy(null);
    }
  };

  if (!data) {
    return <p className="muted">Загрузка вакансий…</p>;
  }

  if (data.items.length === 0) {
    return (
      <EmptyState
        icon="🔍"
        title="Вакансий не найдено"
        description="Попробуйте расширить регион или изменить целевую должность."
        action={
          <button className="chip chip--active" onClick={() => location.reload()}>
            Обновить
          </button>
        }
      />
    );
  }

  return (
    <div className="screen">
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <h3>Вакансии</h3>
        <DataBadge source={data.source} count={data.items.length} />
      </div>

      {data.source === 'fallback' && (
        <div className="notice">
          ⚠️ API «Работа России» недоступен. Показаны тестовые вакансии —
          они демонстрируют работу подбора, но не отражают актуальный рынок.
        </div>
      )}

      {data.items.map((v) => (
        <div key={v.id} className="card vacancy">
          <div className="vacancy__head">
            <strong>{v.title}</strong>
            <span className="badge badge--match">{v.match_score}%</span>
          </div>
          <p className="muted small">
            {v.company} · {v.region}
          </p>
          {v.salary && <p className="salary">{v.salary}</p>}
          {v.matched_skills.length > 0 && (
            <p className="muted small">Совпало: {v.matched_skills.join(', ')}</p>
          )}
          <div className="row">
            {v.url && (
              <a
                className="link"
                href={v.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Открыть →
              </a>
            )}
            <Button
              variant={sent[v.id] ? 'secondary' : 'primary'}
              disabled={sent[v.id] || busy === v.id}
              onClick={() => apply(v.id, v.title, v.url, v.company)}
            >
              {sent[v.id]
                ? '✓ Отклик сохранён'
                : busy === v.id
                ? '…'
                : 'Откликнулся'}
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}