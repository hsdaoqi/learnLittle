import { lazy, Suspense } from 'react'
import { useT } from '../../i18n'
import { useUiStore } from '../../stores/useUiStore'

const ChatPanel = lazy(() => import('../ChatPanel'))

export default function AssistantDrawer() {
  const t = useT()
  const visible = useUiStore((s) => s.assistantVisible)
  const mounted = useUiStore((s) => s.assistantMounted)
  const closeAssistant = useUiStore((s) => s.closeAssistant)

  if (!mounted) return null

  return (
    <aside
      className={`relative z-[90] flex h-full shrink-0 flex-col border-l border-[var(--color-assistant-border)] bg-[var(--color-assistant-bg)] shadow-[var(--color-assistant-shadow)] transition-[width] duration-300 ${
        visible ? 'w-[480px]' : 'w-0 overflow-hidden'
      }`}
    >
      <div className="flex h-full w-[480px] flex-col">
        <div className="flex items-start justify-between border-b border-[var(--color-border)] px-4 py-3">
          <div>
            <h2 className="text-sm font-semibold">{t('assistant.title')}</h2>
            <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">{t('assistant.subtitle')}</p>
          </div>
          <button
            type="button"
            className="text-xs text-[var(--color-text-secondary)]"
            onClick={closeAssistant}
          >
            {t('assistant.close')}
          </button>
        </div>
        <div className="min-h-0 flex-1">
          <Suspense fallback={<p className="p-4 text-sm text-[var(--color-text-tertiary)]">…</p>}>
            <ChatPanel />
          </Suspense>
        </div>
      </div>
    </aside>
  )
}
