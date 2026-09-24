import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { useVoiceInput } from '../hooks/useVoiceInput';
import type { Experience, UserProfile } from '../types';
import { Button, Card, Input, Select, Tag, Title } from '../ui';
import { showToast } from '../ui/Toast';
import { ConsentCheckbox } from './ConsentModal';
import { LegalPage } from './LegalPage';

const SUGGESTED_SKILLS = [
  'python', 'sql', 'excel', 'javascript', 'typescript', 'react',
  'git', 'docker', 'statistics', 'figma', 'english', 'communication',
];

interface Props {
  maxUserId: string;
  defaultName: string | null;
  onDone: (profile: UserProfile) => void;
}

export function Onboarding({ maxUserId, defaultName, onDone }: Props) {
  const { t } = useTranslation('onboarding');

  const [step, setStep] = useState(0);
  const [position, setPosition] = useState('');
  const [region, setRegion] = useState('');
  const [experience, setExperience] = useState<Experience>('none');
  const [skills, setSkills] = useState<string[]>([]);
  const [custom, setCustom] = useState('');
  const [consent, setConsent] = useState(false);
  const [showLegal, setShowLegal] = useState<null | 'terms' | 'privacy'>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const voice = useVoiceInput('ru-RU');

  const toggleSkill = (s: string) =>
    setSkills((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s],
    );

  const addCustom = () => {
    const v = custom.trim().toLowerCase();
    if (v && !skills.includes(v)) setSkills((p) => [...p, v]);
    setCustom('');
    voice.reset();
  };

  const submit = async () => {
    if (!consent) {
      setError(t('consent_required'));
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const profile = await api.onboarding({
        max_user_id: maxUserId,
        full_name: defaultName,
        desired_position: position.trim(),
        region: region.trim() || null,
        experience,
        skills,
        consent_pd: consent,
      });
      onDone(profile);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Не удалось сохранить профиль';
      setError(msg);
      showToast(msg, 'error');
    } finally {
      setBusy(false);
    }
  };

  if (showLegal) {
    return <LegalPage kind={showLegal} onClose={() => setShowLegal(null)} />;
  }

  return (
    <div className="screen">
      <Title>{t('title')}</Title>
      <p className="muted">{t('step', { current: step + 1, total: 3 })}</p>

      {step === 0 && (
        <Card>
          <h3>{t('position_title')}</h3>
          <Input
            placeholder={t('position_placeholder')}
            value={position}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setPosition(e.target.value)
            }
          />
          <Input
            placeholder={t('region_placeholder')}
            value={region}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setRegion(e.target.value)
            }
          />
          <Button
            disabled={position.trim().length < 2}
            onClick={() => setStep(1)}
          >
            {t('next', { ns: 'common', defaultValue: 'Далее' })}
          </Button>
        </Card>
      )}

      {step === 1 && (
        <Card>
          <h3>{t('experience_title')}</h3>
          <Select
            value={experience}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) =>
              setExperience(e.target.value as Experience)
            }
          >
            <option value="none">{t('experience_none')}</option>
            <option value="internship">{t('experience_internship')}</option>
            <option value="junior">{t('experience_junior')}</option>
          </Select>
          <div className="row">
            <Button variant="secondary" onClick={() => setStep(0)}>
              {t('back', { ns: 'common', defaultValue: 'Назад' })}
            </Button>
            <Button onClick={() => setStep(2)}>
              {t('next', { ns: 'common', defaultValue: 'Далее' })}
            </Button>
          </div>
        </Card>
      )}

      {step === 2 && (
        <Card>
          <h3>{t('skills_title')}</h3>
          <p className="muted small">{t('skills_hint')}</p>

          <div className="chips">
            {SUGGESTED_SKILLS.map((s) => (
              <Tag
                key={s}
                onClick={() => toggleSkill(s)}
                className={skills.includes(s) ? 'chip chip--active' : 'chip'}
              >
                {s}
              </Tag>
            ))}
          </div>

          <div className="row">
            <Input
              placeholder={t('custom_skill')}
              value={voice.isListening ? voice.transcript : custom}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setCustom(e.target.value)
              }
              disabled={voice.isListening}
              onKeyDown={(e: React.KeyboardEvent) =>
                e.key === 'Enter' && addCustom()
              }
            />
            {voice.supported && (
              <Button
                variant="secondary"
                aria-label={
                  voice.isListening ? 'Остановить запись' : 'Голосовой ввод'
                }
                onClick={voice.isListening ? voice.stop : voice.start}
              >
                {voice.isListening ? '⏹' : '🎤'}
              </Button>
            )}
            <Button variant="secondary" onClick={addCustom}>
              +
            </Button>
          </div>

          {skills.length > 0 && (
            <div className="chips">
              {skills.map((s) => (
                <span key={s} className="chip chip--active">
                  {s}
                </span>
              ))}
            </div>
          )}

          <ConsentCheckbox
            checked={consent}
            onChange={setConsent}
            onOpenTerms={() => setShowLegal('privacy')}
          />

          {error && <p className="error">{error}</p>}

          <div className="row">
            <Button variant="secondary" onClick={() => setStep(1)}>
              {t('back', { ns: 'common', defaultValue: 'Назад' })}
            </Button>
            <Button disabled={busy || !consent} onClick={submit}>
              {busy ? t('saving') : t('build_plan')}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}