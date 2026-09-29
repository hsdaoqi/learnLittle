import { useT } from '../../i18n'
import { useAuthStore } from '../../stores/useAuthStore'
import { useUiStore } from '../../stores/useUiStore'

export default function TopBar() {
  const t = useT()
  const user = useAuthStore((s) => s.user)
  const theme = useUiStore((s) => s.theme)
  const locale = useUiStore((s) => s.locale)
  const assistantVisible = useUiStore((s) => s.assistantVisible)
  const toggleTheme = useUiStore((s) => s.toggleTheme)
  const toggleLocale = useUiStore((s) => s.toggleLocale)
  const toggleAssistant = useUiStore((s) => s.toggleAssistant)
  const openSearch = useUiStore((s) => s.openSearch)

  return (
    <header className="relative z-[100] flex h-14 shrink-0 items-center justify-between border-b border-[var(--color-topbar-border)] bg-[var(--color-topbar-bg)] px-4">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-accent)] text-sm font-bold text-[var(--color-on-accent)]">
          L
        </div>
        <span className="text-base font-semibold text-[var(--color-text)]">{t('app.name')}</span>
      </div>

      <div className="mx-4 max-w-md flex-1">
        <button
          type="button"
          onClick={openSearch}
          className="flex h-9 w-full items-center gap-2 rounded-lg border border-[var(--color-search-border)] bg-[var(--color-search-bg)] px-3 text-left text-sm text-[var(--color-text-tertiary)]"
        >
          <span className="truncate">{t('search.placeholder')}</span>
          <span className="ml-auto hidden text-[10px] sm:inline">Ctrl+K</span>
        </button>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggleTheme}
          className="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-[var(--color-text-secondary)]"
        >
          {theme === 'light' ? t('topbar.theme.dark') : t('topbar.theme.light')}
        </button>
        <button
          type="button"
          onClick={toggleLocale}
          className="rounded-md border border-[var(--color-border)] px-2 py-1 text-xs text-[var(--color-text-secondary)]"
        >
          {locale === 'zh' ? t('topbar.lang.en') : t('topbar.lang.zh')}
        </button>
        <button
          type="button"
          onClick={toggleAssistant}
          className={`rounded-md px-3 py-1.5 text-sm ${
            assistantVisible
              ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
              : 'border border-[var(--color-border)] text-[var(--color-text-secondary)]'
          }`}
        >
          {t('topbar.assistant')}
        </button>
        {user && (
          <span className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
            {user.avatar ? (
              <img src={user.avatar} alt="" className="h-7 w-7 rounded-full object-cover" />
            ) : (
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-accent-bg)] text-xs text-[var(--color-accent)]">
                {user.username.slice(0, 1).toUpperCase()}
              </span>
            )}
            {user.username}
          </span>
        )}
      </div>
    </header>
  )
}
