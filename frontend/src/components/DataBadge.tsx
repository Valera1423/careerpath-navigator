interface Props {
  source: 'trudvsem' | 'fallback' | string;
  count?: number;
}

/**
 * Индикатор источника данных.
 *
 * Разделяет реальные данные (trudvsem), модельные (fallback) и
 * собственные данные продукта, чтобы пользователь понимал
 * происхождение информации (ТЗ стр. 18 п. 3).
 */
export function DataBadge({ source, count }: Props) {
  const config: Record<string, { label: string; cls: string; hint: string }> = {
    trudvsem: {
      label: 'Реальные данные',
      cls: 'badge--match',
      hint: 'Источник: открытые данные «Работа России» (trudvsem.ru)',
    },
    fallback: {
      label: 'Демо-данные',
      cls: 'badge--important',
      hint: 'API «Работа России» недоступен. Показаны заранее подготовленные тестовые вакансии.',
    },
  };

  const item = config[source] ?? {
    label: 'Источник: ' + source,
    cls: 'badge--kind',
    hint: '',
  };

  return (
    <span className={`badge ${item.cls}`} title={item.hint}>
      {item.label}
      {typeof count === 'number' ? ` · ${count}` : ''}
    </span>
  );
}