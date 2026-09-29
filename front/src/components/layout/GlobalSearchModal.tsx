import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { notesApi } from '../../api/notes'
import { chatApi } from '../../api/chat'
import { knowledgeApi } from '../../api/knowledge'
import { ApiError } from '../../api/client'
import { useT } from '../../i18n'
import { useUiStore } from '../../stores/useUiStore'
import type { NoteSummary } from '../../types/notes'
import type { ChatSession } from '../../types/chat'
import type { KnowledgeDocument } from '../../types/knowledge'

type SearchTab = 'notes' | 'sessions' | 'knowledge'

export default function GlobalSearchModal() {
  const t = useT()
  const navigate = useNavigate()
  const closeSearch = useUiStore((s) => s.closeSearch)
  const openAssistant = useUiStore((s) => s.openAssistant)
  const inputRef = useRef<HTMLInputElement>(null)
  const [tab, setTab] = useState<SearchTab>('notes')
  const [query, setQuery] = useState('')
  const [debounced, setDebounced] = useState('')
  const [searching, setSearching] = useState(false)
  const [error, setError] = useState('')
  const [notes, setNotes] = useState<NoteSummary[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])

  useEffect(() => {
    inputRef.current?.focus()
    void chatApi.sessions().then(setSessions).catch(() => {})
    void knowledgeApi
      .list()
      .then((data) => setDocuments(data.documents))
      .catch(() => {})
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(query.trim()), 300)
    return () => window.clearTimeout(timer)
  }, [query])

  useEffect(() => {
    if (tab !== 'notes') return
    if (!debounced) {
      setNotes([])
      setSearching(false)
      setError('')
      return
    }
    let cancelled = false
    setSearching(true)
    notesApi
      .search(debounced, 20)
      .then((data) => {
        if (!cancelled) {
          setNotes(data.results.map((hit) => hit.note))
          setError('')
        }
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : t('search.failed'))
      })
      .finally(() => {
        if (!cancelled) setSearching(false)
      })
    return () => {
      cancelled = true
    }
    // t 每次渲染都是新函数，不能进依赖，否则会反复 POST /note/search
  }, [tab, debounced])

  const q = query.trim().toLowerCase()
  const filteredSessions = sessions.filter((item) => item.title.toLowerCase().includes(q))
  const filteredDocs = documents.filter((item) => item.filename.toLowerCase().includes(q))
  const empty =
    (tab === 'notes' && notes.length === 0) ||
    (tab === 'sessions' && filteredSessions.length === 0) ||
    (tab === 'knowledge' && filteredDocs.length === 0)

  function go(path: string) {
    closeSearch()
    navigate(path)
  }

  const tabs: { key: SearchTab; label: string }[] = [
    { key: 'notes', label: t('search.tab.notes') },
    { key: 'sessions', label: t('search.tab.sessions') },
    { key: 'knowledge', label: t('search.tab.knowledge') },
  ]

  return (
    <div
      className="fixed inset-0 z-[120] flex items-start justify-center bg-black/20 pt-24"
      onClick={closeSearch}
    >
      <div
        className="w-[560px] max-w-[90vw] overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] shadow-card"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 border-b border-[var(--color-border)] px-4 py-3">
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={t('search.placeholder')}
            className="flex-1 bg-transparent text-sm outline-none"
          />
          <button
            type="button"
            className="text-xs text-[var(--color-text-secondary)]"
            onClick={closeSearch}
          >
            Esc
          </button>
        </div>
        <div className="flex gap-1 border-b border-[var(--color-border)] px-4 py-2">
          {tabs.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => setTab(item.key)}
              className={`rounded-full px-3 py-1 text-xs ${
                tab === item.key
                  ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                  : 'text-[var(--color-text-secondary)]'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
        <div className="max-h-[360px] overflow-y-auto">
          {error && <p className="px-4 py-3 text-sm text-red-500">{error}</p>}
          {searching && tab === 'notes' && (
            <p className="px-4 pt-3 text-xs text-[var(--color-text-tertiary)]">
              {t('search.searching')}
            </p>
          )}
          {!q ? (
            <p className="py-10 text-center text-sm text-[var(--color-text-tertiary)]">
              {t('search.hint')}
            </p>
          ) : empty ? (
            <p className="py-10 text-center text-sm text-[var(--color-text-tertiary)]">
              {t('search.empty')}
            </p>
          ) : tab === 'notes' ? (
            notes.map((note) => (
              <button
                key={note.id}
                type="button"
                className="block w-full px-4 py-3 text-left hover:bg-[var(--color-bg)]"
                onClick={() => go(`/notes/${note.id}`)}
              >
                <p className="truncate text-sm font-medium">{note.title || '未命名笔记'}</p>
                <p className="mt-0.5 text-xs text-[var(--color-text-tertiary)]">
                  {note.format === 'txt' ? 'TXT' : 'MD'}
                </p>
              </button>
            ))
          ) : tab === 'sessions' ? (
            filteredSessions.map((session) => (
              <button
                key={session.id}
                type="button"
                className="block w-full px-4 py-3 text-left hover:bg-[var(--color-bg)]"
                onClick={() => {
                  closeSearch()
                  openAssistant()
                }}
              >
                <p className="truncate text-sm font-medium">{session.title || '新对话'}</p>
              </button>
            ))
          ) : (
            filteredDocs.map((doc) => (
              <button
                key={doc.id}
                type="button"
                className="block w-full px-4 py-3 text-left hover:bg-[var(--color-bg)]"
                onClick={() => go('/knowledge')}
              >
                <p className="truncate text-sm font-medium">{doc.filename}</p>
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
