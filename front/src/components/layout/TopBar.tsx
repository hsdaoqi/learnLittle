import VisualIcon from '../VisualIcon'
import { Languages, Moon, Sun } from 'lucide-react'
import { Link } from 'react-router-dom'
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
    <header className="app-topbar relative z-[100] flex h-14 shrink-0 items-center justify-between border-b border-[var(--color-topbar-border)] bg-[var(--color-topbar-bg)] px-4">
      <div className="flex items-center gap-2">
        <div className="brand-mark flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--color-accent)] text-sm font-bold text-[var(--color-on-accent)]">
          云
        </div>
        <span className="text-base font-semibold text-[var(--color-text)]">{t('app.name')}</span>
      </div>

      <div className="mx-4 max-w-md flex-1">
        <button
          type="button"
          onClick={openSearch}
          className="flex h-9 w-full items-center gap-2 rounded-lg border border-[var(--color-search-border)] bg-[var(--color-search-bg)] px-3 text-left text-sm text-[var(--color-text-tertiary)]"
        >
          <VisualIcon name="search" size={16} className="shrink-0" />
          <span className="truncate">{t('search.placeholder')}</span>
        </button>
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={toggleTheme}
          title={theme === 'light' ? t('topbar.theme.dark') : t('topbar.theme.light')}
          aria-label={theme === 'light' ? t('topbar.theme.dark') : t('topbar.theme.light')}
          className="icon-button"
        >
          {theme === 'light' ? <Moon size={17} /> : <Sun size={17} />}
        </button>
        <button
          type="button"
          onClick={toggleLocale}
          title={locale === 'zh' ? t('topbar.lang.en') : t('topbar.lang.zh')}
          aria-label={locale === 'zh' ? t('topbar.lang.en') : t('topbar.lang.zh')}
          className="icon-button"
        >
          <Languages size={17} />
        </button>
        <button
          type="button"
          onClick={toggleAssistant}
          aria-pressed={assistantVisible}
          className={`assistant-toggle flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm ${
            assistantVisible
              ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
              : 'border border-[var(--color-border)] text-[var(--color-text-secondary)]'
          }`}
        >
          <img src="/avatars/xiaoyunyun.png" alt="" className="h-5 w-5 rounded-full object-cover" />
          {t('topbar.assistant')}
        </button>
        {user && (
          <Link to="/profile" title={t('profile.title')} className="user-link flex items-center gap-2 text-sm text-[var(--color-text-secondary)]">
            {user.avatar ? (
              <img src={user.avatar} alt="" className="h-7 w-7 rounded-full object-cover" />
            ) : (
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-[var(--color-accent-bg)] text-xs text-[var(--color-accent)]">
                {user.username.slice(0, 1).toUpperCase()}
              </span>
            )}
            <span className="hidden lg:inline">{user.username}</span>
          </Link>
        )}
      </div>
    </header>
  )
}
