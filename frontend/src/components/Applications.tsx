import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { ApplicationData } from '../types';
import { Button, Card, Title } from '../ui';

const STATUS_LABEL: Record<ApplicationData['status'], string> = {
  applied: 'Отклик отправлен',
  interview: 'Пригласили на интервью',
  offer: 'Оффер',
  rejected: 'Отказ',
};

const STATUS_ORDER: ApplicationData['status'][] = ['applied', 'interview', 'offer', 'rejected'];

export function Applications() {
  const [items, setItems] = useState<ApplicationData[]>([]);
  const [busy, setBusy] = useState(false);

  const reload = () => api.applications().then(setItems);

  useEffect(() => {
    void reload();
  }, []);

  const changeStatus = async (id: number, status: ApplicationData['status']) => {
    setBusy(true);
    try {
      await api.updateApplication(id, { status });
      await reload();
    } finally {
      setBusy(false);
    }
  };

  const remove = async (id: number) => {
    setBusy(true);
    try {
      await api.deleteApplication(id);
      await reload();
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="screen">
      <Title>Мои отклики</Title>
      {items.length === 0 && (
        <Card>
          <p className="muted">
            Здесь будут отклики. Отмечайте их на вкладке «Вакансии» — и мы
            напомним проверить статус.
          </p>
        </Card>
      )}
      {items.map((a) => (
        <Card key={a.id}>
          <div className="vacancy__head">
            <strong>{a.vacancy_title}</strong>
            <span className="badge badge--kind">{STATUS_LABEL[a.status]}</span>
          </div>
          {a.company && <p className="muted small">{a.company}</p>}
          {a.remind_at && (
            <p className="muted small">
              Напоминание: {new Date(a.remind_at).toLocaleDateString('ru-RU')}
            </p>
          )}
          <div className="chips">
            {STATUS_ORDER.filter((s) => s !== a.status).map((s) => (
              <button
                key={s}
                className="chip"
                disabled={busy}
                onClick={() => changeStatus(a.id, s)}
              >
                → {STATUS_LABEL[s]}
              </button>
            ))}
          </div>
          {a.vacancy_url && (
            <a className="link" href={a.vacancy_url} target="_blank" rel="noopener noreferrer">
              Открыть вакансию →
            </a>
          )}
          <Button variant="secondary" onClick={() => remove(a.id)} disabled={busy}>
            Удалить
          </Button>
        </Card>
      ))}
    </div>
  );
}