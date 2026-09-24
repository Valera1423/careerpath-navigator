import { useEffect, useState } from 'react';

type ToastKind = 'info' | 'success' | 'error';
interface Toast { id: number; text: string; kind: ToastKind }

let counter = 0;
const listeners: Array<(t: Toast) => void> = [];

export function showToast(text: string, kind: ToastKind = 'info'): void {
  const t: Toast = { id: ++counter, text, kind };
  listeners.forEach((fn) => fn(t));
}

export function ToastContainer() {
  const [items, setItems] = useState<Toast[]>([]);

  useEffect(() => {
    const onToast = (t: Toast) => {
      setItems((prev) => [...prev, t]);
      setTimeout(() => setItems((prev) => prev.filter((x) => x.id !== t.id)), 3500);
    };
    listeners.push(onToast);
    return () => {
      const idx = listeners.indexOf(onToast);
      if (idx >= 0) listeners.splice(idx, 1);
    };
  }, []);

  return (
    <div className="toast-container" role="status" aria-live="polite">
      {items.map((t) => (
        <div key={t.id} className={`toast toast--${t.kind}`}>
          {t.text}
        </div>
      ))}
    </div>
  );
}
