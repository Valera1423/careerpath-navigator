import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { SkillGapResponse } from '../types';

export function MarketComparison({ gap }: { gap: SkillGapResponse }) {
  const all = [...gap.matched, ...gap.missing].slice(0, 10);
  const data = all.map((i) => ({
    skill: i.skill.replace('_', ' '),
    demand: Math.round(i.demand_share * 100),
    have: gap.matched.some((m) => m.skill === i.skill)
      ? Math.round(i.demand_share * 100)
      : 0,
  }));

  if (data.length === 0) return null;

  return (
    <div className="card">
      <h3>Ты vs рынок</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="skill" angle={-30} textAnchor="end" height={60} interval={0} />
          <YAxis unit="%" />
          <Tooltip />
          <Legend />
          <Bar dataKey="demand" name="Требуют вакансии" fill="#c7d2fe" />
          <Bar dataKey="have" name="Есть у тебя" fill="#2f6feb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}