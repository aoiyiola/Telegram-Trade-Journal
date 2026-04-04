import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'trading-journal-theme';

export const PRESET_THEMES = [
  {
    id: 'dark-blue',
    name: 'Dark Blue',
    description: 'Default dark theme with blue accents',
    colors: {
      bgPrimary: '#0f172a',
      bgSecondary: '#1e293b',
      bgTertiary: '#334155',
      border: '#334155',
      accent: '#0ea5e9',
      accentHover: '#0284c7',
      text: '#f1f5f9',
      textMuted: '#94a3b8',
    },
  },
  {
    id: 'dark-green',
    name: 'Dark Green',
    description: 'Dark theme with emerald accents',
    colors: {
      bgPrimary: '#052e16',
      bgSecondary: '#14532d',
      bgTertiary: '#166534',
      border: '#166534',
      accent: '#10b981',
      accentHover: '#059669',
      text: '#ecfdf5',
      textMuted: '#6ee7b7',
    },
  },
  {
    id: 'dark-purple',
    name: 'Dark Purple',
    description: 'Dark theme with violet accents',
    colors: {
      bgPrimary: '#1e1b4b',
      bgSecondary: '#312e81',
      bgTertiary: '#3730a3',
      border: '#4338ca',
      accent: '#818cf8',
      accentHover: '#6366f1',
      text: '#eef2ff',
      textMuted: '#a5b4fc',
    },
  },
  {
    id: 'dark-amber',
    name: 'Dark Amber',
    description: 'Dark theme with warm amber accents',
    colors: {
      bgPrimary: '#1c1008',
      bgSecondary: '#292010',
      bgTertiary: '#3d2f14',
      border: '#78350f',
      accent: '#f59e0b',
      accentHover: '#d97706',
      text: '#fffbeb',
      textMuted: '#fcd34d',
    },
  },
  {
    id: 'midnight',
    name: 'Midnight',
    description: 'Pure black with cyan accents',
    colors: {
      bgPrimary: '#000000',
      bgSecondary: '#0a0a0a',
      bgTertiary: '#1a1a1a',
      border: '#2a2a2a',
      accent: '#22d3ee',
      accentHover: '#06b6d4',
      text: '#f8fafc',
      textMuted: '#64748b',
    },
  },
];

const DEFAULT_THEME = PRESET_THEMES[0];

function applyTheme(colors) {
  const root = document.documentElement;
  root.style.setProperty('--color-bg-primary', colors.bgPrimary);
  root.style.setProperty('--color-bg-secondary', colors.bgSecondary);
  root.style.setProperty('--color-bg-tertiary', colors.bgTertiary);
  root.style.setProperty('--color-border', colors.border);
  root.style.setProperty('--color-accent', colors.accent);
  root.style.setProperty('--color-accent-hover', colors.accentHover);
  root.style.setProperty('--color-text', colors.text);
  root.style.setProperty('--color-text-muted', colors.textMuted);
}

export function useTheme() {
  const [activeThemeId, setActiveThemeId] = useState(DEFAULT_THEME.id);
  const [customAccent, setCustomAccent] = useState(null);

  // Load from localStorage on mount
  useEffect(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed.themeId) setActiveThemeId(parsed.themeId);
        if (parsed.customAccent) setCustomAccent(parsed.customAccent);
      }
    } catch {
      // Ignore malformed saved data
    }
  }, []);

  // Apply theme whenever it changes
  useEffect(() => {
    const preset = PRESET_THEMES.find((t) => t.id === activeThemeId) || DEFAULT_THEME;
    const colors = {
      ...preset.colors,
      ...(customAccent ? { accent: customAccent } : {}),
    };
    applyTheme(colors);
  }, [activeThemeId, customAccent]);

  const selectTheme = useCallback((themeId) => {
    setActiveThemeId(themeId);
    setCustomAccent(null); // reset custom accent when switching preset
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId, customAccent: null }));
  }, []);

  const updateAccent = useCallback(
    (color) => {
      setCustomAccent(color);
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ themeId: activeThemeId, customAccent: color }));
    },
    [activeThemeId],
  );

  const resetTheme = useCallback(() => {
    setActiveThemeId(DEFAULT_THEME.id);
    setCustomAccent(null);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const activeTheme = PRESET_THEMES.find((t) => t.id === activeThemeId) || DEFAULT_THEME;

  return { activeTheme, activeThemeId, customAccent, selectTheme, updateAccent, resetTheme };
}
