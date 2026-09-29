import { createPortal } from 'react-dom'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useT } from '../../i18n'

export default function NotePreviewModal({
  title,
  content,
  onClose,
}: {
  title: string
  content: string
  onClose: () => void
}) {
  const t = useT()
  return createPortal(
    <div
      className="fixed inset-0 z-[200] flex items-center justify-center bg-black/40 p-4"
      onClick={onClose}
    >
      <div
        className="flex max-h-[80vh] w-[560px] max-w-[92vw] flex-col rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] shadow-lg"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-3 border-b border-[var(--color-border)] px-5 py-4">
          <h3 className="truncate text-base font-semibold">{title}</h3>
          <button
            type="button"
            className="shrink-0 text-sm text-[var(--color-text-secondary)]"
            onClick={onClose}
          >
            {t('assistant.close')}
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4 text-sm">
          {content ? (
            <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
          ) : (
            <p className="text-[var(--color-text-secondary)]">{t('chat.previewEmpty')}</p>
          )}
        </div>
      </div>
    </div>,
    document.body,
  )
}
