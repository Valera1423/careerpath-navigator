import { useState } from 'react';
import { Button, Card, Input, Textarea } from '../ui';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';

export function PortfolioTracker() {
  const [projectName, setProjectName] = useState('');
  const [description, setDescription] = useState('');
  const [skills, setSkills] = useState('');
  const [readme, setReadme] = useState('');
  const [bullet, setBullet] = useState('');
  const [busy, setBusy] = useState(false);

  const skillList = skills
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);

  const generate = async () => {
    setBusy(true);
    try {
      const r1 = await fetch(`${API_BASE}/portfolio/readme`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_name: projectName,
          description,
          skills: skillList,
        }),
      });
      const d1 = await r1.json();
      setReadme(d1.readme);

      const r2 = await fetch(`${API_BASE}/portfolio/resume-bullet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_name: projectName, skills: skillList }),
      });
      const d2 = await r2.json();
      setBullet(d2.bullet);
    } finally {
      setBusy(false);
    }
  };

  const copy = (text: string) => {
    void navigator.clipboard.writeText(text);
  };

  return (
    <div className="screen">
      <Card>
        <h3>Портфолио-трекер</h3>
        <Input
          placeholder="Название проекта"
          value={projectName}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setProjectName(e.target.value)}
        />
        <Textarea
          placeholder="Что делает проект, какая задача решается"
          value={description}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
          rows={3}
        />
        <Input
          placeholder="Стек через запятую: python, fastapi, postgresql"
          value={skills}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSkills(e.target.value)}
        />
        <Button
          disabled={busy || projectName.length < 2 || description.length < 10}
          onClick={generate}
        >
          {busy ? 'Генерируем…' : 'Сгенерировать README + bullet'}
        </Button>
      </Card>

      {readme && (
        <Card>
          <h3>README для GitHub</h3>
          <pre className="code">{readme}</pre>
          <Button variant="secondary" onClick={() => copy(readme)}>
            Скопировать
          </Button>
        </Card>
      )}

      {bullet && (
        <Card>
          <h3>Строка для резюме</h3>
          <p>{bullet}</p>
          <Button variant="secondary" onClick={() => copy(bullet)}>
            Скопировать
          </Button>
        </Card>
      )}
    </div>
  );
}