import { useTranslation } from 'react-i18next';
import { useTheme, type Theme } from '../hooks/useTheme';
import { api } from '../api/client';
import type { UserProfile } from '../types';
import { Button, Card, Title } from '../ui';
import { showToast } from '../ui/Toast';

interface Props {
  profile: UserProfile;
  onProfileChange: (p: UserProfile) => void;
}

export function Settings({ profile, onProfileChange }: Props) {
  const { t, i18n } = useTranslation('settings');
  const common = useTranslation('common').t;
  const { theme, setTheme } = useTheme();

  const changeLang = (lang: string) => {
    void i18n.changeLanguage(lang);
  };

  const toggleOptIn = async () => {
    const next = !profile.employer_opt_in;
    const updated = await api.setEmployerOptIn(next);
    onProfileChange(updated);
    showToast(next ? 'Передача данных включена' : 'Передача данных отключена', 'success');
  };

  const deleteAccount = async () => {
    if (!window.confirm(t('delete_confirm'))) return;
    await api.deleteAccount();
    localStorage.clear();
    location.reload();
  };

  return (
    <div className="screen">
      <Title>{t('title')}</Title>

      <Card>
        <h3>{t('language')}</h3>
        <div className="chips">
          <button
            className={i18n.language === 'ru' ? 'chip chip--active' : 'chip'}
            onClick={() => changeLang('ru')}
          >
            Русский
          </button>
          <button
            className={i18n.language === 'en' ? 'chip chip--active' : 'chip'}
            onClick={() => changeLang('en')}
          >
            English
          </button>
        </div>
      </Card>

      <Card>
        <h3>{t('theme')}</h3>
        <div className="chips">
          {(['light', 'dark', 'system'] as Theme[]).map((th) => (
            <button
              key={th}
              className={theme === th ? 'chip chip--active' : 'chip'}
              onClick={() => setTheme(th)}
            >
              {t(`theme_${th}`)}
            </button>
          ))}
        </div>
      </Card>

      <Card>
        <h3>{t('employer_opt_in')}</h3>
        <p className="muted small">{t('employer_opt_in_hint')}</p>
        <Button variant={profile.employer_opt_in ? 'secondary' : 'primary'} onClick={toggleOptIn}>
          {profile.employer_opt_in ? 'Отключить' : 'Включить'}
        </Button>
      </Card>

      <Card>
        <h3>{t('delete_account')}</h3>
        <p className="muted small">{t('delete_account_hint')}</p>
        <Button variant="secondary" onClick={deleteAccount}>
          {common('actions.delete')}
        </Button>
      </Card>
    </div>
  );
}