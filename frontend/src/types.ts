export type Experience = 'none' | 'internship' | 'junior';

export interface UserProfile {
  id: number;
  max_user_id: string;
  full_name: string | null;
  desired_position: string;
  region: string | null;
  experience: Experience;
  skills: string[];
  created_at: string;
  consent_pd_given_at: string | null;
  employer_opt_in: boolean;
  // 152-ФЗ ст.9 ч.6
  is_minor: boolean;
  age_confirmed_at: string | null;
  consent_pd_guardian_at: string | null;
}

export interface SkillGapItem {
  skill: string;
  demand: number;
  demand_share: number;
  importance: 'critical' | 'important' | 'nice-to-have';
}

export interface SkillGapResponse {
  position: string;
  region: string | null;
  vacancies_analyzed: number;
  source: 'trudvsem' | 'fallback';
  matched: SkillGapItem[];
  missing: SkillGapItem[];
  readiness_score: number;
}

export interface PlanStep {
  id: number;
  order_index: number;
  skill: string;
  title: string;
  description: string;
  kind: 'course' | 'project' | 'practice' | string;
  resource_url: string | null;
  is_done: boolean;
  due_date: string | null;
  depends_on: number[];
}

export interface PlanResponse {
  steps: PlanStep[];
  total: number;
  done: number;
  progress_percent: number;
}

export interface Vacancy {
  id: string;
  title: string;
  company: string;
  region: string;
  salary: string | null;
  url: string | null;
  match_score: number;
  matched_skills: string[];
  published_at: string | null;
}

export interface RecommendationsResponse {
  source: 'trudvsem' | 'fallback';
  items: Vacancy[];
}

export interface MarketTrends {
  period_days: number;
  vacancies_analyzed: number;
  top_skills: { skill: string; count: number; share: number }[];
  top_companies: { company: string; vacancies: number }[];
  salaries: {
    min: number | null;
    max: number | null;
    avg: number | null;
    sample: number;
  };
}

export interface ResumeUploadResponse {
  added_skills: string[];
  total_skills: string[];
}

export interface AtsResponse {
  score: number;
  matched_keywords: string[];
  missing_keywords: string[];
  format_issues: string[];
  section_warnings: string[];
}

export interface ProgressData {
  xp: number;
  level: string;
  level_label: string;
  current_threshold: number;
  next_threshold: number;
  streak_days: number;
}

export interface AchievementData {
  id: number;
  code: string;
  title: string;
  description: string;
  unlocked_at: string;
}

export interface ForecastItem {
  skill: string;
  current: number;
  predicted: number;
  trend: 'growing' | 'declining' | 'stable';
  change_pct: number;
}

export interface ForecastResponse {
  horizon_months: number;
  items: ForecastItem[];
}

export interface CompassNode {
  id: string;
  data: { label: string; status: 'done' | 'missing' };
  position: { x: number; y: number };
}

export interface CompassEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
}

export interface CompassGraph {
  nodes: CompassNode[];
  edges: CompassEdge[];
}

export interface InterviewQuestion {
  session_id: number;
  question_index: number;
  total: number;
  question: string;
}

export interface InterviewAnswerResponse {
  score: number;
  feedback: string;
  structure: {
    situation: boolean;
    task: boolean;
    action: boolean;
    result: boolean;
  };
  next_question: string | null;
  is_finished: boolean;
}

export interface SchoolQuestion {
  id: number;
  text: string;
  type: string;
}

export interface SchoolResult {
  scores: Record<string, number>;
  top_type: string;
  professions: string[];
  description: string;
}

export interface DayInLife {
  profession: string;
  timeline: string[];
}

export interface ApplicationData {
  id: number;
  vacancy_id: string;
  vacancy_title: string;
  vacancy_url: string | null;
  company: string | null;
  status: 'applied' | 'interview' | 'offer' | 'rejected';
  applied_at: string;
  remind_at: string | null;
  note: string | null;
}

export interface LeaderboardEntry {
  rank: number;
  display_name: string;
  xp: number;
  level: string;
  streak_days: number;
}

export interface ScenarioSummary {
  id: string;
  role: string;
  duration_minutes: number;
  intro: string;
}

export interface SimulatorChoice {
  id: string;
  text: string;
}

export interface SimulatorNode {
  node_id: string;
  type: 'scenario' | 'end';
  text: string;
  choices: SimulatorChoice[];
  outcome?: string;
  summary?: string;
}

export interface SimulatorStartResponse {
  session_id: number;
  scenario_id: string;
  node: SimulatorNode;
}

export interface SimulatorChooseResponse {
  feedback: string;
  effects: Record<string, unknown>;
  next: SimulatorNode;
  is_finished: boolean;
}

export interface SimulatorApplyResponse {
  added_skills: string[];
  message: string;
}