import { useRef, useState } from 'react';
import { api } from '../api/client';
import type { AtsResponse } from '../types';
import { Button, Card, Textarea, Title } from '../ui';

export function AtsAnalyzer() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [vacancy, setVacancy] = useState('');
  const [result, setResult] = useState<AtsResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      setResult(await api.atsAnalyze(file, vacancy));
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка');
    } finally {
      setBusy(false);
    }
  };

  const scoreColor =
    result && result.score >= 70 ? '#1f7a3d' : result && result.score >= 40 ? '#8a6100' : '#b3261e';

  return (
    <div className="screen">
      <Title>ATS-анализ резюме</Title>
      <Card>
        <p className="muted small">
          Загрузите резюме и вставьте текст вакансии — проверим проходимость
          автоматического отбора.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          style={{ display: 'none' }}
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <Button variant="secondary" onClick={() => inputRef.current?.click()}>
          {file ? file.name : 'Выбрать резюме (PDF/DOCX)'}
        </Button>
        <Textarea
          placeholder="Вставьте текст вакансии"
          value={vacancy}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setVacancy(e.target.value)}
          rows={5}
        />
        <Button
          disabled={busy || !file || vacancy.length < 20}
          onClick={analyze}
        >
          {busy ? 'Анализируем…' : 'Проверить'}
        </Button>
        {error && <p className="error">{error}</p>}
      </Card>

      {result && (
        <Card>
          <div className="ats-score" style={{ color: scoreColor }}>
            <span className="ats-score__value">{result.score}</span>
            <span className="muted small"> из 100</span>
          </div>

          {result.matched_keywords.length > 0 && (
            <>
              <h4>Совпало</h4>
              <div className="chips">
                {result.matched_keywords.map((s) => (
                  <span key={s} className="chip chip--active">{s}</span>
                ))}
              </div>
            </>
          )}

          {result.missing_keywords.length > 0 && (
            <>
              <h4>Не хватает</h4>
              <div className="chips">
                {result.missing_keywords.map((s) => (
                  <span key={s} className="chip">{s}</span>
                ))}
              </div>
            </>
          )}

          {result.format_issues.length > 0 && (
            <>
              <h4>Проблемы форматирования</h4>
              <ul>
                {result.format_issues.map((i) => (
                  <li key={i} className="small">{i}</li>
                ))}
              </ul>
            </>
          )}

          {result.section_warnings.length > 0 && (
            <>
              <h4>Отсутствуют секции</h4>
              <ul>
                {result.section_warnings.map((i) => (
                  <li key={i} className="small">{i}</li>
                ))}
              </ul>
            </>
          )}
        </Card>
      )}
    </div>
  );
}