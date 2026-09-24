import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { api } from './api/client';
import { ApiError } from './utils/api';
import { Applications } from './components/Applications';
import { AtsAnalyzer } from './components/AtsAnalyzer';
import { CareerCompass } from './components/CareerCompass';
import { CoachChat } from './components/CoachChat';
import { Dashboard } from './components/Dashboard';
import { EmployerSandbox } from './components/EmployerSandbox';
import { ErrorBoundary } from './components/ErrorBoundary';
import { InterviewSimulator } from './components/InterviewSimulator';
import { Leaderboard } from './components/Leaderboard';
import { MarketDashboard } from './components/MarketDashboard';
import { Onboarding } from './components/Onboarding';
import { PlanView } from './components/PlanView';
import { SchoolMode } from './components/SchoolMode';
import { Settings } from './components/Settings';
import { Simulator } from './components/Simulator';
import { Vacancies } from './components/Vacancies';
import { getMaxUserId, getMaxUserName, initMax } from './max/bridge';
import { showToast, ToastContainer } from './ui/Toast';
import type {
  PlanResponse,
  RecommendationsResponse,
  SkillGapResponse,
  UserProfile,
} from './types';

type Tab =
  | 'dashboard'
  | 'plan'
  | 'vacancies'
  | 'applications'
  | 'interview'
  | 'market'
  | 'coach'
  | 'compass'
  | 'school'
  | 'simulator'
  | 'ats'
  | 'leaderboard'
  | 'employer'
  | 'settings';

type Status = 'loading' | 'onboarding' | 'ready' | 'error';

export default function App() {
  const { t } = useTranslation('common');
  const maxUserId = getMaxUserId();

  const [status, setStatus] = useState<Status>('loading');
  const [tab, setTab] = useState<Tab>('dashboard');
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [gap, setGap] = useState<SkillGapResponse | null>(null);
  const [plan, setPlan] = useState<PlanResponse | null>(null);
  const [vacancies, setVacancies] = useState<RecommendationsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [regenerating, setRegenerating] = useState(false);

  const loadData = useCallback(async () => {
    const [g, p, v] = await Promise.all([
      api.gap(),
      api.plan(),
      api.recommendations(),
    ]);
    setGap(g);
    setPlan(p);
    setVacancies(v);
  }, []);

  useEffect(() => {
    initMax();
    (async () => {
      try {
        const me = await api.me();
        setProfile(me);
        setStatus('ready');
        await loadData();
      } catch (e: unknown) {
        if (e instanceof ApiError && e.status === 404) {
          setStatus('onboarding');
        } else {
          setError(e instanceof Error ? e.message : 'Ошибка загрузки');
          setStatus('error');
        }
      }
    })();
  }, [loadData]);

  const handleOnboardingDone = async (p: UserProfile) => {
    setProfile(p);
    setStatus('ready');
    try {
      await api.regeneratePlan();
      await loadData();
    } catch (e: unknown) {
      showToast(
        e instanceof Error ? e.message : 'Не удалось построить план',
        'error',
      );
    }
  };

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      const fresh = await api.regeneratePlan();
      setPlan(fresh);
      setGap(await api.gap());
      showToast('План обновлён', 'success');
    } catch (e: unknown) {
      showToast(e instanceof Error ? e.message : 'Ошибка', 'error');
    } finally {
      setRegenerating(false);
    }
  };

  const handleToggle = async (stepId: number) => {
    if (!plan) return;
    setPlan({
      ...plan,
      steps: plan.steps.map((s) =>
        s.id === stepId ? { ...s, is_done: !s.is_done } : s,
      ),
    });
    try {
      await api.toggleStep(stepId);
      setPlan(await api.plan());
    } catch {
      setPlan(await api.plan());
    }
  };

  const reloadProfile = async () => {
    const me = await api.me();
    setProfile(me);
    await loadData();
  };

  if (status === 'loading') {
    return <div className="screen center">{t('loading')}</div>;
  }

  if (status === 'error') {
    return <div className="screen center error">{error}</div>;
  }

  if (status === 'onboarding') {
    return (
      <Onboarding
        maxUserId={maxUserId}
        defaultName={getMaxUserName()}
        onDone={handleOnboardingDone}
      />
    );
  }

  if (!profile) return null;

  return (
    <div className="app">
      <ErrorBoundary>
        {tab === 'dashboard' && (
          <Dashboard
            profile={profile}
            gap={gap}
            plan={plan}
            onRegenerate={handleRegenerate}
            regenerating={regenerating}
            onProfileUpdated={reloadProfile}
          />
        )}
        {tab === 'plan' && <PlanView plan={plan} onToggle={handleToggle} />}
        {tab === 'vacancies' && <Vacancies data={vacancies} />}
        {tab === 'applications' && <Applications />}
        {tab === 'interview' && <InterviewSimulator />}
        {tab === 'market' && <MarketDashboard />}
        {tab === 'coach' && <CoachChat />}
        {tab === 'compass' && <CareerCompass />}
        {tab === 'school' && (
          <SchoolMode profile={profile} onProfileChange={setProfile} />
        )}
        {tab === 'simulator' && <Simulator onProfileUpdated={reloadProfile} />}
        {tab === 'ats' && <AtsAnalyzer />}
        {tab === 'leaderboard' && <Leaderboard />}
        {tab === 'employer' && <EmployerSandbox />}
        {tab === 'settings' && (
          <Settings profile={profile} onProfileChange={setProfile} />
        )}
      </ErrorBoundary>

      <ToastContainer />

      <nav className="tabbar" aria-label="Основная навигация">
        <button
          className={tab === 'dashboard' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('dashboard')}
        >
          {t('tabs.dashboard')}
        </button>
        <button
          className={tab === 'plan' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('plan')}
        >
          {t('tabs.plan')}
        </button>
        <button
          className={tab === 'vacancies' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('vacancies')}
        >
          {t('tabs.vacancies')}
        </button>
        <button
          className={tab === 'simulator' ? 'tab tab--active' : 'tab'}
          onClick={() => setTab('simulator')}
        >
          {t('tabs.simulator')}
        </button>
        <button
          className={tab === 'settings' ? 'tab tab--active' : 'tab'}
          onClick={() =>
            setTab(tab === 'settings' ? 'dashboard' : 'settings')
          }
          aria-label="Настройки"
        >
          ⚙
        </button>
      </nav>
    </div>
  );
}