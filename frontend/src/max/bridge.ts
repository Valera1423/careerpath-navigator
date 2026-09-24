/**
 * Обёртка над MAX Bridge.
 *
 * ВАЖНО:
 * - window.WebApp.initData — строка для серверной валидации.
 * - window.WebApp.initDataUnsafe — только для UI-подсказок (имя, аватар),
 *   НЕ использовать для аутентификации.
 */
interface MaxWebApp {
  initData?: string;
  initDataUnsafe?: {
    user?: { id?: number | string; first_name?: string; last_name?: string };
  };
  ready?: () => void;
  expand?: () => void;
}

declare global {
  interface Window {
    WebApp?: MaxWebApp;
  }
}

const DEV_USER_ID = import.meta.env.VITE_DEV_USER_ID ?? 'dev-user-1';

export function initMax(): void {
  window.WebApp?.ready?.();
  window.WebApp?.expand?.();
}

/** Строка initData для передачи на backend (X-Max-Init-Data). */
export function getInitData(): string | null {
  return window.WebApp?.initData ?? null;
}

/** ID пользователя — ТОЛЬКО для UI-подсказок. */
export function getMaxUserId(): string {
  const id = window.WebApp?.initDataUnsafe?.user?.id;
  return id ? String(id) : DEV_USER_ID;
}

/** Имя пользователя — для UI-подсказок. */
export function getMaxUserName(): string | null {
  const u = window.WebApp?.initDataUnsafe?.user;
  if (!u) return null;
  return [u.first_name, u.last_name].filter(Boolean).join(' ') || null;
}