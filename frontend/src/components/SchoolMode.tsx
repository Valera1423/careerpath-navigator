import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { DayInLife, SchoolQuestion, SchoolResult, UserProfile } from '../types';
import { Button, Card, Input, Title } from '../ui';
import { showToast } from '../ui/Toast';

type Stage =
  | 'age_gate'
  | 'guardian_consent'
  | 'intro'
  | 'questions'
  | 'result'
  | 'day';

interface Props {
  profile: UserProfile;
  onProfileChange: (p: UserProfile) => void;
}

export function SchoolMode({ profile, onProfileChange }: Props) {
  const [stage, setStage] = useState<Stage>(() => {
    if (!profile.age_confirmed_at) return 'age_gate';
    if (profile.is_minor && !profile.consent_pd_guardian_at) return 'guardian_consent';
    return 'intro';
  });

  const [birthYear, setBirthYear] = useState('');
  const [guardianName, setGuardianName] = useState('');
  const [consentChecked, setConsentChecked] = useState(false);
  const [busy, setBusy] = useState(false);

  const [questions, setQuestions] = useState<SchoolQuestion[]>([]);
  const [idx, setIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [result, setResult] = useState<SchoolResult | null>(null);
  const [day, setDay] = useState<DayInLife | null>(null);

  useEffect(() => {
    if (stage === 'questions') {
      api.schoolQuestions().then(setQuestions).catch(() => undefined);
    }
  }, [stage]);

  const submitAge = async () => {
    const year = Number(birthYear);
    if (!year || year < 1900 || year > new Date().getFullYear()) {
      showToast('Введите корректный год рождения', 'error');
      return;
    }
    setBusy(true);
    try {
      const updated = await api.confirmAge(year);
      onProfileChange(updated);
      if (updated.is_minor && !updated.consent_pd_guardian_at) {
        setStage('guardian_consent');
      } else {
        setStage('intro');
      }
    } catch (e) {
      showToast(e instanceof Error ? e.message : 'Ошибка', 'error');
    } finally {
      setBusy(false);
    }
  };

  const submitGuardian = async () => {
    if (!guardianName.trim() || !consentChecked) {
      showToast('Заполните имя и подтвердите согласие', 'error');
      return;
    }
    setBusy(true);
    try {
      const updated = await api.setGuardianConsent(guardianName.trim(), true);
      onProfileChange(updated);
      showToast('Согласие законного представителя сохранено', 'success');
      setStage('intro');
    } catch (e) {
      showToast(e instanceof Error ? e.message : 'Ошибка', 'error');
    } finally {
      setBusy(false);
    }
  };

  const answer = async (value: 0 | 1 | 2) => {
    if (!questions[idx]) return;
    const updated = { ...answers, [questions[idx].id]: value };
    setAnswers(updated);

    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
    } else {
      const res = await api.schoolEvaluate(updated);
      setResult(res);
      setStage('result');
    }
  };

  const showDay = async (profession: string) => {
    const d = await api.dayInLife(profession);
    setDay(d);
    setStage('day');
  };

  // ---------- Экран 1: подтверждение возраста ----------
  if (stage === 'age_gate') {
    return (
      <div className="screen">
        <Title>Примерочная профессии</Title>
        <Card>
          <p className="muted">
            Раздел «Школьникам» предназначен для учеников 8–11 классов.
            Для соблюдения 152-ФЗ нам нужно знать ваш возраст.
          </p>
          <label className="muted small">
            Год рождения
            <Input
              type="number"
              placeholder="Например, 2009"
              value={birthYear}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setBirthYear(e.target.value)
              }
              min="1900"
              max={new Date().getFullYear()}
            />
          </label>
          <p className="muted small">
            Год рождения не сохраняется в открытом виде — мы храним только
            флаг «младше 18 лет» и дату подтверждения.
          </p>
          <Button onClick={submitAge} disabled={busy}>
            {busy ? 'Проверяем…' : 'Продолжить'}
          </Button>
        </Card>
      </div>
    );
  }

  // ---------- Экран 2: согласие законного представителя ----------
  if (stage === 'guardian_consent') {
    return (
      <div className="screen">
        <Title>Согласие законного представителя</Title>
        <Card>
          <p>
            Вам меньше 18 лет. По статье 9 части 6 ФЗ-152 обработка
            персональных данных несовершеннолетнего возможна только
            с согласия родителя или законного представителя.
          </p>
          <label className="muted small">
            ФИО законного представителя
            <Input
              placeholder="Иванова Мария Петровна"
              value={guardianName}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setGuardianName(e.target.value)
              }
            />
          </label>
          <label className="consent">
            <input
              type="checkbox"
              checked={consentChecked}
              onChange={(e) => setConsentChecked(e.target.checked)}
            />
            <span>
              Я, как законный представитель, даю согласие на обработку
              персональных данных несовершеннолетнего в объёме, необходимом
              для работы раздела «Школьникам».
            </span>
          </label>
          <Button onClick={submitGuardian} disabled={busy || !consentChecked}>
            {busy ? 'Сохраняем…' : 'Дать согласие и продолжить'}
          </Button>
        </Card>
      </div>
    );
  }

  // ---------- Экран 3: интро ----------
  if (stage === 'intro') {
    return (
      <div className="screen">
        <Title>Примерочная профессии</Title>
        <Card>
          <p className="muted">
            18 коротких вопросов. Мы определим твой профиль и покажем
            подходящие направления.
          </p>
          <div className="notice">
            ℹ️ Это профориентационный тест, а не профессиональная
            психологическая диагностика. Результаты — рекомендация,
            обсудите их с родителями, педагогом или психологом.
          </div>
          <Button onClick={() => setStage('questions')}>Начать тест</Button>
        </Card>
      </div>
    );
  }

  // ---------- Экран 4: вопросы ----------
  if (stage === 'questions') {
    const q = questions[idx];
    if (!q) return <p className="muted">Загрузка…</p>;
    const progress = Math.round((idx / questions.length) * 100);
    return (
      <div className="screen">
        <div className="progress">
          <div className="progress__bar" style={{ width: `${progress}%` }} />
        </div>
        <p className="muted small">
          Вопрос {idx + 1} из {questions.length}
        </p>
        <Card>
          <p className="interview-question">{q.text}</p>
          <div className="row">
            <Button variant="secondary" onClick={() => answer(0)}>Нет</Button>
            <Button variant="secondary" onClick={() => answer(1)}>Скорее нет</Button>
            <Button onClick={() => answer(2)}>Да</Button>
          </div>
        </Card>
      </div>
    );
  }

  // ---------- Экран 5: результат ----------
  if (stage === 'result' && result) {
    return (
      <div className="screen">
        <Card>
          <h3>Твой профиль: {result.top_type}</h3>
          <p>{result.description}</p>
          <h4>Подходящие профессии</h4>
          <ul>
            {result.professions.map((p) => (
              <li key={p}>
                {p}{' '}
                <button className="link" onClick={() => showDay(p)}>
                  (примерочная)
                </button>
              </li>
            ))}
          </ul>
          <p className="muted small">
            Результат носит рекомендательный характер. Если вам нужна
            поддержка — обратитесь к школьному психологу или на
            всероссийский детский телефон доверия 8-800-2000-122.
          </p>
        </Card>
      </div>
    );
  }

  // ---------- Экран 6: день из жизни ----------
  if (stage === 'day' && day) {
    return (
      <div className="screen">
        <Card>
          <h3>Один день из жизни: {day.profession}</h3>
          <ol className="timeline">
            {day.timeline.map((t) => (
              <li key={t}>{t}</li>
            ))}
          </ol>
          <Button variant="secondary" onClick={() => setStage('result')}>
            Назад
          </Button>
        </Card>
      </div>
    );
  }

  return null;
}