import { useEffect, useState } from 'react'
import { chatApi } from '../api/chat'
import { notesApi } from '../api/notes'
import { ApiError } from '../api/client'
import { useT } from '../i18n'
import type { ChatMessage, ChatSession } from '../types/chat'
import type { NoteDetail, NoteSummary } from '../types/notes'
import MessageContent from './chat/MessageContent'
import { composeReferencedMessage } from '../utils/noteReferenceParser'

export default function ChatPanel() {
  const t = useT()
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [sending, setSending] = useState(false)
  const [toolHint, setToolHint] = useState('')
  const [thinkingText, setThinkingText] = useState('')
  const [enableThinking, setEnableThinking] = useState(false)
  const [pickerOpen, setPickerOpen] = useState(false)
  const [noteOptions, setNoteOptions] = useState<NoteSummary[]>([])
  const [picked, setPicked] = useState<NoteSummary[]>([])

  async function loadSessions(selectId?: string | null) {
    const list = await chatApi.sessions()
    setSessions(list)
    const next = selectId ?? activeId ?? list[0]?.id ?? null
    setActiveId(next)
    if (next) setMessages(await chatApi.messages(next))
    else setMessages([])
  }

  useEffect(() => {
    void loadSessions().catch((err) => {
      setError(err instanceof ApiError ? err.message : t('assistant.loadFailed'))
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function openPicker() {
    setPickerOpen(true)
    try {
      const data = await notesApi.list({ page: 1, page_size: 50 })
      setNoteOptions(data.items)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('chat.refFailed'))
    }
  }

  function togglePick(note: NoteSummary) {
    setPicked((prev) =>
      prev.some((item) => item.id === note.id)
        ? prev.filter((item) => item.id !== note.id)
        : [...prev, note],
    )
  }

  async function send() {
    const text = draft.trim()
    if ((!text && picked.length === 0) || sending) return
    setSending(true)
    setError('')
    setThinkingText('')
    setDraft('')
    const selected = picked
    setPicked([])
    setPickerOpen(false)

    let outgoing = text || t('chat.refOnly')
    if (selected.length) {
      const details: NoteDetail[] = []
      for (const item of selected) {
        try {
          details.push(await notesApi.detail(item.id))
        } catch {
          details.push({ ...item, content: '' })
        }
      }
      outgoing = composeReferencedMessage(
        text || t('chat.refOnly'),
        details.map((n) => ({ id: n.id, title: n.title, content: n.content || '' })),
      )
    }

    const localUser: ChatMessage = {
      id: Date.now(),
      session_id: activeId || '',
      role: 'user',
      content: outgoing,
      created_at: new Date().toISOString(),
    }
    const localAssistant: ChatMessage = {
      id: Date.now() + 1,
      session_id: activeId || '',
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, localUser, localAssistant])
    let sessionId = activeId
    try {
      await chatApi.query(
        outgoing,
        activeId,
        {
          onMeta: (meta) => {
            sessionId = meta.session_id
            setActiveId(meta.session_id)
          },
          onThinking: (event) => {
            setThinkingText(event.content)
          },
          onToolStart: (event) => {
            setToolHint(t('assistant.toolRunning') + event.name)
          },
          onToolEnd: () => {
            setToolHint('')
          },
          onToken: (chunk) => {
            setThinkingText('')
            setMessages((prev) => {
              const copy = [...prev]
              const last = copy[copy.length - 1]
              if (last?.role === 'assistant') {
                copy[copy.length - 1] = { ...last, content: last.content + chunk }
              }
              return copy
            })
          },
          onError: (content) => {
            setError(content)
          },
          onDone: (done) => {
            sessionId = done.session_id
            setActiveId(done.session_id)
            if (done.title) {
              setSessions((prev) =>
                prev.map((item) =>
                  item.id === done.session_id ? { ...item, title: done.title as string } : item,
                ),
              )
            }
          },
        },
        { enableThinking },
      )
      await loadSessions(sessionId)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('assistant.sendFailed'))
    } finally {
      setToolHint('')
      setThinkingText('')
      setSending(false)
    }
  }

  async function removeSession(id: string) {
    if (!window.confirm(t('assistant.deleteConfirm'))) return
    await chatApi.remove(id)
    const next = activeId === id ? null : activeId
    setActiveId(next)
    await loadSessions(next)
  }

  return (
    <div className="flex h-full min-h-0">
      <aside className="w-44 shrink-0 overflow-y-auto border-r border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="flex items-center justify-between px-3 py-3">
          <span className="text-sm font-semibold">{t('assistant.sessions')}</span>
          <button
            className="text-xs text-[var(--color-accent)]"
            onClick={() => {
              setActiveId(null)
              setMessages([])
            }}
          >
            {t('assistant.new')}
          </button>
        </div>
        <ul>
          {sessions.map((s) => (
            <li
              key={s.id}
              className={`flex items-center px-3 py-2 text-sm ${
                activeId === s.id ? 'bg-[var(--color-accent-bg)]' : ''
              }`}
            >
              <button className="min-w-0 flex-1 truncate text-left" onClick={() => void loadSessions(s.id)}>
                {s.title}
              </button>
              <button
                className="ml-1 text-xs text-[var(--color-danger)]"
                onClick={() => void removeSession(s.id)}
              >
                {t('assistant.delete')}
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="flex min-w-0 flex-1 flex-col">
        {error && <p className="px-4 pt-3 text-sm text-[var(--color-danger)]">{error}</p>}
        {(toolHint || thinkingText) && (
          <p className="px-4 pt-2 text-xs text-[var(--color-text-secondary)]">
            {toolHint || thinkingText}
          </p>
        )}
        <div className="flex-1 space-y-3 overflow-y-auto p-4">
          {messages.length === 0 && (
            <p className="text-sm text-[var(--color-text-tertiary)]">{t('assistant.empty')}</p>
          )}
          {messages.map((m) => (
            <div
              key={m.id}
              className={`max-w-[90%] rounded-xl px-4 py-3 text-sm ${
                m.role === 'user'
                  ? 'ml-auto bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                  : 'bg-[var(--color-surface)] shadow-card'
              }`}
            >
              <MessageContent content={m.content} role={m.role} />
            </div>
          ))}
        </div>
        {picked.length > 0 && (
          <div className="flex flex-wrap gap-1 border-t border-[var(--color-border)] px-3 pt-2">
            {picked.map((note) => (
              <button
                key={note.id}
                type="button"
                className="rounded-full bg-[var(--color-accent-bg)] px-2 py-0.5 text-xs"
                onClick={() => togglePick(note)}
              >
                {note.title} ×
              </button>
            ))}
          </div>
        )}
        {pickerOpen && (
          <div className="max-h-40 overflow-y-auto border-t border-[var(--color-border)] bg-[var(--color-sidebar-bg)] p-2">
            {noteOptions.length === 0 ? (
              <p className="px-2 text-xs text-[var(--color-text-secondary)]">{t('chat.noNotes')}</p>
            ) : (
              noteOptions.map((note) => (
                <button
                  key={note.id}
                  type="button"
                  onClick={() => togglePick(note)}
                  className={`mb-1 block w-full truncate rounded px-2 py-1 text-left text-xs ${
                    picked.some((item) => item.id === note.id)
                      ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                      : 'hover:bg-[var(--color-accent-bg)]'
                  }`}
                >
                  {note.title}
                </button>
              ))
            )}
          </div>
        )}
        <form
          className="flex gap-2 border-t border-[var(--color-border)] bg-[var(--color-surface)] p-3"
          onSubmit={(e) => {
            e.preventDefault()
            void send()
          }}
        >
          <button
            type="button"
            onClick={() => (pickerOpen ? setPickerOpen(false) : void openPicker())}
            className="rounded-md border border-[var(--color-border)] px-2 py-2 text-xs"
          >
            {t('chat.refNote')}
          </button>
          <label className="flex shrink-0 items-center gap-1 text-xs text-[var(--color-text-secondary)]">
            <input
              type="checkbox"
              checked={enableThinking}
              onChange={(e) => setEnableThinking(e.target.checked)}
            />
            {t('assistant.thinkingMode')}
          </label>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={t('assistant.placeholder')}
            className="flex-1 rounded-md border border-[var(--color-border)] bg-[var(--color-surface)] px-3 py-2 text-sm outline-none focus:border-[var(--color-accent)]"
          />
          <button
            type="submit"
            disabled={sending}
            className="rounded-md bg-[var(--color-accent)] px-4 py-2 text-sm text-[var(--color-on-accent)] hover:opacity-90 disabled:opacity-50"
          >
            {sending ? t('assistant.sending') : t('assistant.send')}
          </button>
        </form>
      </section>
    </div>
  )
}
