import { useState } from 'react';
import { api } from '../api/client';
import { Button, Card, Input, Title } from '../ui';

interface Message {
  role: 'user' | 'coach';
  text: string;
}

export function CoachChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const question = input.trim();
    setMessages((m) => [...m, { role: 'user', text: question }]);
    setInput('');
    setBusy(true);
    try {
      const res = await api.coachAsk(question);
      setMessages((m) => [...m, { role: 'coach', text: res.answer }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="screen">
      <Title>Карьерный коуч</Title>
      {messages.length === 0 && (
        <Card>
          <p className="muted small">
            Спросите про любой навык из своего gap-анализа: зачем он нужен,
            с чего начать, сколько времени займёт. Примеры:
          </p>
          <div className="chips">
            {['Зачем мне SQL?', 'С чего начать в Python?', 'Что такое статистика для аналитика?'].map(
              (q) => (
                <button key={q} className="chip" onClick={() => setInput(q)}>
                  {q}
                </button>
              ),
            )}
          </div>
        </Card>
      )}

      {messages.map((m, i) => (
        <div key={i} className={`message message--${m.role}`}>
          {m.text}
        </div>
      ))}

      <div className="row">
        <Input
          placeholder="Ваш вопрос"
          value={input}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setInput(e.target.value)}
          onKeyDown={(e: React.KeyboardEvent) => e.key === 'Enter' && send()}
        />
        <Button onClick={send} disabled={busy || !input.trim()}>
          {busy ? '…' : '→'}
        </Button>
      </div>
    </div>
  );
}