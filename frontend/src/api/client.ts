import { getInitData, getMaxUserId } from '../max/bridge';
import { ApiError, readErrorDetail } from '../utils/api';
import type {
  AchievementData,
  ApplicationData,
  AtsResponse,
  CompassGraph,
  DayInLife,
  ForecastResponse,
  InterviewAnswerResponse,
  InterviewQuestion,
  LeaderboardEntry,
  MarketTrends,
  PlanResponse,
  ProgressData,
  RecommendationsResponse,
  ResumeUploadResponse,
  ScenarioSummary,
  SchoolQuestion,
  SchoolResult,
  SimulatorApplyResponse,
  SimulatorChooseResponse,
  SimulatorStartResponse,
  SkillGapResponse,
  UserProfile,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';

interface RequestOptions extends RequestInit {
  devUserId?: string;
}

/**
 * Определяем заголовки аутентификации:
 * - если MAX Bridge дал initData — используем его (прод)
 * - иначе fallback на dev-идентификатор (backend примет только при
 *   ALLOW_INSECURE_INIT_DATA=true)
 */
function authHeaders(devUserId?: string): Record<string, string> {
  const initData = getInitData();
  if (initData) {
    return { 'X-Max-Init-Data': initData };
  }
  return { 'X-Max-User-Id': devUserId ?? getMaxUserId() };
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { devUserId, headers, ...rest } = options;

  const finalHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...authHeaders(devUserId),
    ...((headers as Record<string, string>) ?? {}),
  };

  const res = await fetch(`${API_BASE}${path}`, { ...rest, headers: finalHeaders });

  if (!res.ok) {
    const detail = await readErrorDetail(res);
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) {
    return undefined as unknown as T;
  }
  return (await res.json()) as T;
}

async function upload<T>(path: string, formData: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
    headers: authHeaders(),
  });
  if (!res.ok) {
    throw new ApiError(res.status, await readErrorDetail(res));
  }
  return res.json() as Promise<T>;
}

export const api = {
  // --- Users ---
  onboarding: (payload: {
    max_user_id: string;
    full_name?: string | null;
    desired_position: string;
    region?: string | null;
    experience: 'none' | 'internship' | 'junior';
    skills: string[];
    consent_pd: boolean;
  }) =>
    request<UserProfile>('/users/onboarding', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  me: () => request<UserProfile>('/users/me'),

  updateSkills: (skills: string[]) =>
    request<UserProfile>('/users/me/skills', {
      method: 'PATCH',
      body: JSON.stringify({ skills }),
    }),

  setEmployerOptIn: (employer_opt_in: boolean) =>
    request<UserProfile>('/users/me/employer-opt-in', {
      method: 'POST',
      body: JSON.stringify({ employer_opt_in }),
    }),

  // 152-ФЗ ст.9 ч.6 — несовершеннолетние
  confirmAge: (birth_year: number, is_minor_declared = false) =>
    request<UserProfile>('/users/me/age-confirmation', {
      method: 'POST',
      body: JSON.stringify({ birth_year, is_minor_declared }),
    }),

  setGuardianConsent: (guardian_name: string, consent_pd_guardian: boolean) =>
    request<UserProfile>('/users/me/guardian-consent', {
      method: 'POST',
      body: JSON.stringify({ guardian_name, consent_pd_guardian }),
    }),

  deleteAccount: () => request<void>('/users/me', { method: 'DELETE' }),

  // --- Career ---
  gap: () => request<SkillGapResponse>('/skills/gap'),

  plan: () => request<PlanResponse>('/plan'),

  regeneratePlan: () => request<PlanResponse>('/plan/regenerate', { method: 'POST' }),

  toggleStep: (stepId: number) =>
    request<PlanResponse['steps'][number]>(`/plan/steps/${stepId}/toggle`, {
      method: 'POST',
    }),

  recommendations: (limit = 8) =>
    request<RecommendationsResponse>(`/vacancies/recommendations?limit=${limit}`),

  // --- Resume / ATS ---
  uploadResume: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return upload<ResumeUploadResponse>('/users/me/resume', form);
  },

  atsAnalyze: (file: File, vacancyText: string) => {
    const form = new FormData();
    form.append('file', file);
    form.append('vacancy_text', vacancyText);
    return upload<AtsResponse>('/ats/analyze', form);
  },

  // --- Portfolio ---
  portfolioReadme: (payload: {
    project_name: string;
    description: string;
    skills: string[];
  }) =>
    request<{ readme: string }>('/portfolio/readme', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  portfolioBullet: (payload: {
    project_name: string;
    skills: string[];
    outcome?: string;
  }) =>
    request<{ bullet: string }>('/portfolio/resume-bullet', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  // --- Market ---
  marketTrends: (days = 30) =>
    request<MarketTrends>(`/market/trends?days=${days}`),

  forecast: (horizon = 6) =>
    request<ForecastResponse>(`/market/forecast?horizon_months=${horizon}`),

  // --- Coach ---
  coachAsk: (question: string) =>
    request<{ answer: string; used_llm: boolean }>('/coach/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),

  // --- Gamification ---
  progress: () => request<ProgressData>('/gamification/progress'),

  achievements: () => request<AchievementData[]>('/gamification/achievements'),

  // --- Compass ---
  compass: () => request<CompassGraph>('/compass/graph'),

  // --- Interview ---
  interviewStart: () =>
    request<InterviewQuestion>('/interview/sessions', { method: 'POST' }),

  interviewAnswer: (sessionId: number, answer: string) =>
    request<InterviewAnswerResponse>(`/interview/sessions/${sessionId}/answer`, {
      method: 'POST',
      body: JSON.stringify({ answer }),
    }),

  // --- School ---
  schoolQuestions: () => request<SchoolQuestion[]>('/school/questions'),

  schoolEvaluate: (answers: Record<number, number>) =>
    request<SchoolResult>('/school/evaluate', {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),

  dayInLife: (profession: string) =>
    request<DayInLife>(
      `/school/day-in-life?profession=${encodeURIComponent(profession)}`,
    ),

  // --- Applications ---
  applications: () => request<ApplicationData[]>('/applications'),

  createApplication: (payload: {
    vacancy_id: string;
    vacancy_title: string;
    vacancy_url?: string | null;
    company?: string | null;
    note?: string | null;
    remind_in_days?: number | null;
  }) =>
    request<ApplicationData>('/applications', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  updateApplication: (
    id: number,
    payload: {
      status?: ApplicationData['status'];
      note?: string;
      remind_in_days?: number;
    },
  ) =>
    request<ApplicationData>(`/applications/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  deleteApplication: (id: number) =>
    request<void>(`/applications/${id}`, { method: 'DELETE' }),

  // --- Leaderboard ---
  leaderboard: (limit = 20) =>
    request<LeaderboardEntry[]>(`/leaderboard?limit=${limit}`),

  // --- Simulator ---
  simulatorScenarios: () =>
    request<ScenarioSummary[]>('/simulator/scenarios'),

  simulatorStart: (scenarioId: string) =>
    request<SimulatorStartResponse>(
      `/simulator/sessions?scenario_id=${encodeURIComponent(scenarioId)}`,
      { method: 'POST' },
    ),

  simulatorChoose: (sessionId: number, choiceId: string) =>
    request<SimulatorChooseResponse>(`/simulator/sessions/${sessionId}/choose`, {
      method: 'POST',
      body: JSON.stringify({ choice_id: choiceId }),
    }),

  simulatorApply: (sessionId: number) =>
    request<SimulatorApplyResponse>(
      `/simulator/sessions/${sessionId}/apply-to-profile`,
      { method: 'POST' },
    ),

  // --- Export ---
  exportPlanPdfUrl: () => `${API_BASE}/export/plan.pdf`,
};