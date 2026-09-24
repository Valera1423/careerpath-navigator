import type { ReactNode } from 'react';

interface Props {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}

export function EmptyState({ icon = '📭', title, description, action }: Props) {
  return (
    <div className="card empty-state">
      <div className="empty-state__icon">{icon}</div>
      <strong>{title}</strong>
      {description && <p className="muted small">{description}</p>}
      {action && <div className="empty-state__action">{action}</div>}
    </div>
  );
}
