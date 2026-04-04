import ThemeCustomizer from './ThemeCustomizer';

export default function Header({ user, onMenuToggle, themeProps }) {
  return (
    <header className="border-b shadow-2xl" style={{ backgroundColor: 'var(--color-bg-secondary)', borderColor: 'var(--color-border)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Mobile Menu Button */}
            <button
              onClick={onMenuToggle}
              className="lg:hidden p-2 rounded-lg transition-colors"
              style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text)' }}
              aria-label="Toggle menu"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>

            {/* Title */}
            <div>
              <h1 className="text-2xl font-bold" style={{ color: 'var(--color-accent)' }}>
                Trading Journal
              </h1>
              <p className="text-sm hidden sm:block" style={{ color: 'var(--color-text-muted)' }}>
                {user.name && `${user.name} • `}@{user.username || 'Trader'}
              </p>
            </div>
          </div>
          
          {/* Right side: Status + Theme Customizer */}
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-bg-tertiary)' }}>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Status</span>
              <div className="flex items-center gap-2 mt-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-400">Live</span>
              </div>
            </div>

            {/* Theme Customizer */}
            {themeProps && (
              <ThemeCustomizer
                activeThemeId={themeProps.activeThemeId}
                customAccent={themeProps.customAccent}
                onSelectTheme={themeProps.selectTheme}
                onUpdateAccent={themeProps.updateAccent}
                onReset={themeProps.resetTheme}
              />
            )}
          </div>
        </div>
      </div>
    </header>
  )
}
