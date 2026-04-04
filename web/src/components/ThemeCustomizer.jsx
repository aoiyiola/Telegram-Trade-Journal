import { useState, useRef, useEffect } from 'react';
import { PRESET_THEMES } from '../hooks/useTheme';

export default function ThemeCustomizer({ activeThemeId, customAccent, onSelectTheme, onUpdateAccent, onReset }) {
  const [isOpen, setIsOpen] = useState(false);
  const panelRef = useRef(null);

  // Close panel when clicking outside
  useEffect(() => {
    function handleOutsideClick(e) {
      if (panelRef.current && !panelRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleOutsideClick);
    }
    return () => document.removeEventListener('mousedown', handleOutsideClick);
  }, [isOpen]);

  const activeTheme = PRESET_THEMES.find((t) => t.id === activeThemeId) || PRESET_THEMES[0];
  const displayAccent = customAccent || activeTheme.colors.accent;

  return (
    <div className="relative" ref={panelRef}>
      {/* Toggle button */}
      <button
        onClick={() => setIsOpen((v) => !v)}
        title="Customize theme"
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--color-bg-tertiary)] hover:opacity-80 transition-opacity border border-[var(--color-border)] text-[var(--color-text)]"
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {/* Palette icon */}
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <circle cx="13.5" cy="6.5" r="1" fill="currentColor" />
          <circle cx="17.5" cy="10.5" r="1" fill="currentColor" />
          <circle cx="8.5" cy="7.5" r="1" fill="currentColor" />
          <circle cx="6.5" cy="12.5" r="1" fill="currentColor" />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10c.926 0 1.71-.384 2.012-1.037.317-.682.076-1.508-.55-2.088-.946-.881-.39-2.375.81-2.375H16c3.314 0 6-2.686 6-6 0-4.97-4.477-8.5-10-8.5z"
          />
        </svg>
        <span className="text-sm font-medium hidden sm:inline">Theme</span>
        {/* Active colour swatch */}
        <span
          className="w-3 h-3 rounded-full border border-white/20"
          style={{ backgroundColor: displayAccent }}
        />
      </button>

      {/* Dropdown panel */}
      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-72 rounded-xl shadow-2xl border border-[var(--color-border)] bg-[var(--color-bg-secondary)] z-50 p-4"
          role="dialog"
          aria-label="Theme customiser"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-[var(--color-text)]">Customise Dashboard</h3>
            <button
              onClick={() => setIsOpen(false)}
              className="text-[var(--color-text-muted)] hover:text-[var(--color-text)] transition-colors"
              aria-label="Close"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Preset themes */}
          <p className="text-xs text-[var(--color-text-muted)] uppercase font-semibold mb-2 tracking-wide">
            Preset Themes
          </p>
          <div className="grid grid-cols-1 gap-2 mb-4">
            {PRESET_THEMES.map((theme) => (
              <button
                key={theme.id}
                onClick={() => onSelectTheme(theme.id)}
                className={`flex items-center gap-3 w-full px-3 py-2 rounded-lg border transition-all text-left ${
                  activeThemeId === theme.id
                    ? 'border-[var(--color-accent)] bg-[var(--color-bg-tertiary)]'
                    : 'border-[var(--color-border)] hover:bg-[var(--color-bg-tertiary)]'
                }`}
              >
                {/* Colour swatches preview */}
                <div className="flex gap-1 shrink-0">
                  {[theme.colors.bgPrimary, theme.colors.bgSecondary, theme.colors.accent].map((c, i) => (
                    <span
                      key={i}
                      className="w-4 h-4 rounded-full border border-white/10"
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
                <div className="flex-1 min-w-0">
                  <span className="text-sm font-medium text-[var(--color-text)] block truncate">{theme.name}</span>
                  <span className="text-xs text-[var(--color-text-muted)] block truncate">{theme.description}</span>
                </div>
                {activeThemeId === theme.id && (
                  <svg className="w-4 h-4 text-[var(--color-accent)] shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>

          {/* Custom accent colour */}
          <p className="text-xs text-[var(--color-text-muted)] uppercase font-semibold mb-2 tracking-wide">
            Custom Accent Colour
          </p>
          <div className="flex items-center gap-3 mb-4">
            <label className="relative cursor-pointer">
              <span className="sr-only">Pick accent colour</span>
              <input
                type="color"
                value={displayAccent}
                onChange={(e) => onUpdateAccent(e.target.value)}
                className="w-10 h-10 rounded-lg border-2 border-[var(--color-border)] cursor-pointer bg-transparent p-0.5"
                style={{ colorScheme: 'dark' }}
              />
            </label>
            <span className="text-sm font-mono text-[var(--color-text-muted)]">{displayAccent}</span>
            {customAccent && (
              <button
                onClick={() => onSelectTheme(activeThemeId)}
                className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] ml-auto underline"
              >
                Reset accent
              </button>
            )}
          </div>

          {/* Reset all */}
          <button
            onClick={() => { onReset(); setIsOpen(false); }}
            className="w-full text-center text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)] py-2 border border-[var(--color-border)] rounded-lg transition-colors"
          >
            Reset to default
          </button>

          <p className="text-xs text-[var(--color-text-muted)] mt-3 text-center">
            Your preference is saved automatically
          </p>
        </div>
      )}
    </div>
  );
}
