import { useEffect, useState } from 'react';
import { useMachine } from '@xstate/react';
import { api } from '../api/client';
import { simulatorMachine } from '../machines/simulatorMachine';
import type { ScenarioSummary } from '../types';
import { Button, Card, Title } from '../ui';

interface Props {
  onProfileUpdated: () => void;
}

export function Simulator({ onProfileUpdated }: Props) {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [state, send] = useMachine(simulatorMachine);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.simulatorScenarios().then(setScenarios);
  }, []);

  const start = async (scenarioId: string) => {
    setBusy(true);
    try {
      const res = await api.simulatorStart(scenarioId);
      send({ type: 'START', sessionId: res.session_id, node: res.node });
    } finally {
      setBusy(false);
    }
  };

  const choose = async (choiceId: string) => {
    if (!state.context.sessionId) return;
    setBusy(true);
    try {
      const res = await api.simulatorChoose(state.context.sessionId, choiceId);
      send({
        type: 'CHOOSE',
        choiceId,
        next: res.next,
        feedback: res.feedback,
        isFinished: res.is_finished,
      });
    } finally {
      setBusy(false);
    }
  };

  const applyToProfile = async () => {
    if (!state.context.sessionId) return;
    setBusy(true);
    try {
      const res = await api.simulatorApply(state.context.sessionId);
      alert(res.message);
      onProfileUpdated();
    } finally {
      setBusy(false);
    }
  };

  if (state.matches('idle')) {
    return (
      <div className="screen">
        <Title>Примерочная профессии</Title>
        <p className="muted">
          Проживи один рабочий день в роли — и узнай, какие навыки реально нужны.
        </p>
        {scenarios.map((s) => (
          <Card key={s.id}>
            <strong>{s.role}</strong>
            <p className="muted small">{s.duration_minutes} минут · {s.intro}</p>
            <Button disabled={busy} onClick={() => start(s.id)}>
              Прожить день →
            </Button>
          </Card>
        ))}
      </div>
    );
  }

  const node = state.context.node;
  if (!node) return null;

  if (node.type === 'end') {
    return (
      <div className="screen">
        <Card>
          <h3>
            {node.outcome === 'success' ? '🎉 Отличный день!' : '📝 Есть над чем поработать'}
          </h3>
          <p>{node.text}</p>
          {node.summary && <p className="muted">{node.summary}</p>}
          {state.context.feedback && (
            <p className="muted small">💬 {state.context.feedback}</p>
          )}
          <Button onClick={applyToProfile} disabled={busy}>
            Добавить пробелы в план
          </Button>
          <Button variant="secondary" onClick={() => send({ type: 'RESET' })}>
            Пройти ещё раз
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="screen">
      <Card>
        <p className="small muted">Шаг {state.context.history.length + 1}</p>
        <p>{node.text}</p>
        {state.context.feedback && (
          <div className="feedback">💡 {state.context.feedback}</div>
        )}
        <div className="choices">
          {node.choices.map((c) => (
            <button
              key={c.id}
              className="choice"
              disabled={busy}
              onClick={() => choose(c.id)}
            >
              {c.text}
            </button>
          ))}
        </div>
      </Card>
    </div>
  );
}