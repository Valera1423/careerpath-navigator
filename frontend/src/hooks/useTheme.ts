import { useCallback, useEffect, useState } from 'react';

export type Theme = 'light' | 'dark' | 'system';

const STORAGE_KEY = 'careerpath.theme';

function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  if (theme === 'system') {
    root.removeAttribute('data-theme');
  } else {
    root.setAttribute('data-theme', theme);
  }
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem(STORAGE_KEY) as Theme) ?? 'system',
  );

  useEffect(() => {
    applyTheme(theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const setTheme = useCallback((next: Theme) => setThemeState(next), []);

  return { theme, setTheme };
}