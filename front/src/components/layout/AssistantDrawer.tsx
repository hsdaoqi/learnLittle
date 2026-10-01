import { lazy, Suspense } from 'react'
import { X } from 'lucide-react'
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
      aria-hidden={!visible}
      inert={!visible}
      className={`assistant-drawer fixed bottom-0 right-0 top-14 z-[90] flex w-[480px] max-w-full flex-col overflow-hidden border-l border-[var(--color-assistant-border)] bg-[var(--color-assistant-bg)] shadow-[var(--color-assistant-shadow)] transition-[transform,opacity,visibility] duration-300 ${
        visible ? 'visible translate-x-0 opacity-100' : 'invisible pointer-events-none translate-x-[calc(100%+16px)] opacity-0'
      }`}
    >
      <div className="flex h-full min-w-0 w-full flex-col">
        <div className="assistant-header flex items-center gap-3 px-4 py-3">
          <img src="/avatars/xiaoyunyun.png" alt="" className="h-10 w-10 rounded-full object-cover ring-2 ring-white/30" />
          <div className="flex-1">
            <h2 className="text-base font-semibold">{t('assistant.title')}</h2>
            <p className="mt-0.5 text-xs opacity-80">{t('assistant.subtitle')}</p>
          </div>
          <button
            type="button"
            className="icon-button"
            title={t('assistant.close')}
            aria-label={t('assistant.close')}
            onClick={closeAssistant}
          >
            <X size={18} />
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
