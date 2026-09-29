import { NavLink, useNavigate } from 'react-router-dom'
import { authApi } from '../../api/auth'
import { useT } from '../../i18n'
import { useAuthStore } from '../../stores/useAuthStore'
import { useUiStore } from '../../stores/useUiStore'

const items = [
  { to: '/', key: 'nav.notes' as const, end: true, mark: '笔' },
  { to: '/review', key: 'nav.review' as const, mark: '忆' },
  { to: '/templates', key: 'nav.templates' as const, mark: '模' },
  { to: '/knowledge', key: 'nav.knowledge' as const, mark: '库' },
  { to: '/recycle-bin', key: 'nav.recycle' as const, mark: '收' },
  { to: '/profile', key: 'nav.profile' as const, mark: '我' },
]

export default function IconRail() {
  const t = useT()
  const navigate = useNavigate()
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
    <nav className="relative z-[60] flex h-full w-14 shrink-0 flex-col items-center gap-2 border-r border-[var(--color-border)] bg-[var(--color-sidebar-bg)] py-3">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          title={t(item.key)}
          className={({ isActive }) =>
            `flex h-10 w-10 items-center justify-center rounded-lg text-xs ${
              isActive
                ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]'
            }`
          }
        >
          {item.mark}
        </NavLink>
      ))}
      <button
        type="button"
        title={t('nav.chat')}
        onClick={toggleAssistant}
        className={`flex h-10 w-10 items-center justify-center rounded-lg text-xs ${
          assistantVisible
            ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
            : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]'
        }`}
      >
        问
      </button>
      <button
        type="button"
        title={t('nav.logout')}
        onClick={() => void handleLogout()}
        className="mt-auto flex h-10 w-10 items-center justify-center rounded-lg text-xs text-[var(--color-text-secondary)] hover:bg-[var(--color-accent-bg)]"
      >
        出
      </button>
    </nav>
  )
}
