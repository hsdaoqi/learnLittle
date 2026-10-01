import VisualIcon from '../VisualIcon'
import { NavLink, useLocation, useNavigate } from 'react-router-dom'
import { authApi } from '../../api/auth'
import { useT } from '../../i18n'
import { useAuthStore } from '../../stores/useAuthStore'
import { useUiStore } from '../../stores/useUiStore'

const items = [
  { to: '/', key: 'nav.notes' as const, end: true, mark: 'note' as const },
  { to: '/review', key: 'nav.review' as const, mark: 'review' as const },
  { to: '/knowledge', key: 'nav.knowledge' as const, mark: 'folder' as const },
  { to: '/templates', key: 'nav.templates' as const, mark: 'template' as const },
  { to: '/recycle-bin', key: 'nav.recycle' as const, mark: 'trash' as const },
]

export default function IconRail() {
  const t = useT()
  const navigate = useNavigate()
  const location = useLocation()
  const clear = useAuthStore((s) => s.clear)
  const assistantVisible = useUiStore((s) => s.assistantVisible)
  const toggleAssistant = useUiStore((s) => s.toggleAssistant)

  async function handleLogout() {
    try {
      await authApi.logout(useAuthStore.getState().refreshToken)
    } catch {
      // ignore
    }
    clear()
    navigate('/login', { replace: true })
  }

  return (
    <nav className="icon-rail relative z-[60] flex h-full w-14 shrink-0 flex-col items-center gap-2 border-r border-[var(--color-border)] bg-[var(--color-sidebar-bg)] py-3">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          title={t(item.key)}
          aria-label={t(item.key)}
          className={({ isActive }) =>
            `flex h-10 w-10 items-center justify-center rounded-lg text-xs ${
              isActive || (item.to === '/' && location.pathname.startsWith('/notes/'))
                ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]'
            }`
          }
        >
          <VisualIcon name={item.mark} />
        </NavLink>
      ))}
      <button
        type="button"
        title={t('nav.chat')}
        aria-label={t('nav.chat')}
        onClick={toggleAssistant}
        className={`flex h-10 w-10 items-center justify-center rounded-lg text-xs ${
          assistantVisible
            ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
            : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]'
        }`}
      >
        <VisualIcon name="chat" />
      </button>
      <button
        type="button"
        title={t('nav.logout')}
        aria-label={t('nav.logout')}
        onClick={() => void handleLogout()}
        className="mt-auto flex h-10 w-10 items-center justify-center rounded-lg text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]"
      >
        <VisualIcon name="logout" />
      </button>
    </nav>
  )
}
