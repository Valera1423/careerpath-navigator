import { useRef, useState } from 'react';
import { api } from '../api/client';
import { Button, Card } from '../ui';

interface Props {
  onUploaded: (added: string[]) => void;
}

export function ResumeUpload({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [added, setAdded] = useState<string[] | null>(null);

  const handleFile = async (file: File) => {
    setBusy(true);
    setError(null);
    setAdded(null);
    try {
      const res = await api.uploadResume(file);
      setAdded(res.added_skills);
      onUploaded(res.added_skills);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Ошибка загрузки');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <h3>Загрузить резюме</h3>
      <p className="muted small">
        Поддерживаются PDF и DOCX. Мы автоматически извлечём навыки и добавим их в профиль.
      </p>
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        style={{ display: 'none' }}
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) void handleFile(f);
        }}
      />
      <Button
        onClick={() => inputRef.current?.click()}
        disabled={busy}
        variant="secondary"
      >
        {busy ? 'Разбираем…' : 'Выбрать файл'}
      </Button>
      {error && <p className="error">{error}</p>}
      {added && added.length > 0 && (
        <p className="muted small">
          Добавлено навыков: {added.length} — {added.join(', ')}
        </p>
      )}
      {added && added.length === 0 && (
        <p className="muted small">Новых навыков не найдено — они уже были в профиле.</p>
      )}
    </Card>
  );
}