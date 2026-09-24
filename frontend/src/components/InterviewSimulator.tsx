import { useEffect, useRef, useState } from 'react';
import { api } from '../api/client';
import { useVoiceInput } from '../hooks/useVoiceInput';
import { Button, Card, Textarea, Title } from '../ui';
import type { InterviewQuestion } from '../types';

const QUESTION_TIME_SECONDS = 120;

export function InterviewSimulator() {
  const [session, setSession] = useState<InterviewQuestion | null>(null);
  const [current, setCurrent] = useState<string>('');
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);
  const [score, setScore] = useState<number | null>(null);
  const [structure, setStructure] = useState<Record<string, boolean> | null>(null);
  const [done, setDone] = useState(false);
  const [totalScore, setTotalScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(QUESTION_TIME_SECONDS);
  const [busy, setBusy] = useState(false);

  const voice = useVoiceInput('ru-RU');
  const timerRef = useRef<number | null>(null);

  // Таймер активен, пока сессия идёт
  useEffect(() => {
    if (!session || done) return;
    if (timerRef.current) window.clearInterval(timerRef.current);

    setTimeLeft(QUESTION_TIME_SECONDS);
    timerRef.current = window.setInterval(() => {
      setTimeLeft((t) => (t > 0 ? t - 1 : 0));
    }, 1000);

    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, [session, current, done]);

  const start = async () => {
    setBusy(true);
    try {
      const s = await api.interviewStart();
      setSession(s);
      setCurrent(s.question);
      setDone(false);
      setTotalScore(0);
      setFeedback(null);
      setScore(null);
      setStructure(null);
      setAnswer('');
    } finally {
      setBusy(false);
    }
  };

  const submit = async () => {
    if (!session) return;
    setBusy(true);
    try {
      const res = await api.interviewAnswer(session.session_id, answer);
      setScore(res.score);
      setFeedback(res.feedback);
      setStructure(res.structure);
      setTotalScore((t) => t + res.score);
      setAnswer('');

      if (res.is_finished) {
        setDone(true);
        setCurrent('');
      } else {
        setTimeout(() => {
          setCurrent(res.next_question ?? '');
          setFeedback(null);
          setScore(null);
          setStructure(null);
        }, 2500);
      }
    } finally {
      setBusy(false);
    }
  };

  // Стартовый экран
  if (!session) {
    return (
      <div className="screen">
        <Title>Симулятор собеседования</Title>
        <Card>
          <p className="muted">
            5 вопросов по вашей роли. На каждый — 2 минуты. Оценка по STAR-методу:
            Situation · Task · Action · Result.
          </p>
          <Button onClick={start} disabled={busy}>
            {busy ? 'Готовим…' : 'Начать'}
          </Button>
        </Card>
      </div>
    );
  }

  // Финальный экран
  if (done) {
    const percent = Math.round((totalScore / (session.total * 10)) * 100);
    return (
      <div className="screen">
        <Card>
          <h3>Сессия завершена</h3>
          <p className="score__value">{percent}%</p>
          <p className="muted">
            Итоговый балл: {totalScore} из {session.total * 10}
          </p>
          <Button onClick={start}>Пройти снова</Button>
        </Card>
      </div>
    );
  }

  const mm = String(Math.floor(timeLeft / 60)).padStart(2, '0');
  const ss = String(timeLeft % 60).padStart(2, '0');
  const timeColor = timeLeft < 20 ? '#b3261e' : undefined;

  return (
    <div className="screen">
      <Card>
        <div className="interview-header">
          <span className="small muted">
            Вопрос {session.question_index + 1} из {session.total}
          </span>
          <span className="timer" style={{ color: timeColor }}>{mm}:{ss}</span>
        </div>
        <p className="interview-question">{current}</p>

        {!feedback && (
          <>
            <Textarea
              placeholder="Ваш ответ. Опишите ситуацию, задачу, что вы сделали и какой получился результат."
              value={voice.isListening ? voice.transcript : answer}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setAnswer(e.target.value)}
              rows={6}
              disabled={voice.isListening}
            />
            <div className="row">
              {voice.supported && (
                <Button
                  variant="secondary"
                  aria-label={voice.isListening ? 'Остановить запись' : 'Голосовой ввод'}
                  onClick={voice.isListening ? voice.stop : voice.start}
                >
                  {voice.isListening ? '⏹ Остановить' : '🎤 Голосом'}
                </Button>
              )}
              <Button
                onClick={submit}
                disabled={busy || answer.length < 5}
              >
                {busy ? 'Проверяем…' : 'Ответить'}
              </Button>
            </div>
          </>
        )}

        {feedback && (
          <div className="feedback feedback--result">
            <div className="feedback__score">
              <strong>{score}</strong>
              <span className="muted"> / 10</span>
            </div>
            <p>{feedback}</p>
            {structure && (
              <div className="star">
                {(['situation', 'task', 'action', 'result'] as const).map((k) => (
                  <span
                    key={k}
                    className={structure[k] ? 'star__item star__item--ok' : 'star__item'}
                  >
                    {k === 'situation' ? 'Ситуация' :
                     k === 'task' ? 'Задача' :
                     k === 'action' ? 'Действие' : 'Результат'}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}