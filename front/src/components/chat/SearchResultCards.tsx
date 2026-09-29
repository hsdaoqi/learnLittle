import { useEffect, useState } from 'react'
import { notesApi } from '../../api/notes'
import type { NoteDetail, NoteSummary } from '../../types/notes'
import { noteExcerpt, type ParsedSearchResult } from '../../utils/noteSearchParser'
import NotePreviewModal from './NotePreviewModal'

const detailCache = new Map<string, Promise<NoteDetail>>()

function fetchCachedNote(id: string): Promise<NoteDetail> {
  let pending = detailCache.get(id)
  if (!pending) {
    pending = notesApi.detail(id)
    pending.catch(() => {
      detailCache.delete(id)
    })
    detailCache.set(id, pending)
  }
  return pending
}

function matchNote(list: NoteSummary[], rawTitle: string): NoteSummary | undefined {
  const title = rawTitle.trim()
  return (
    list.find((n) => n.title.trim() === title) ||
    list.find(
      (n) =>
        n.title.trim().toLowerCase().includes(title.toLowerCase()) ||
        title.toLowerCase().includes(n.title.trim().toLowerCase()),
    )
  )
}

interface Enriched {
  raw: ParsedSearchResult
  note: NoteDetail | null
}

export default function SearchResultCards({ results }: { results: ParsedSearchResult[] }) {
  const [items, setItems] = useState<Enriched[]>(() => results.map((raw) => ({ raw, note: null })))
  const [preview, setPreview] = useState<Enriched | null>(null)
  const signature = results.map((r) => `${r.noteId ?? ''}#${r.title}`).join('|')

  useEffect(() => {
    let cancelled = false
    void (async () => {
      const withId = results.filter((r) => r.noteId)
      const withoutId = results.filter((r) => !r.noteId)
      const idNotes = new Map<string, NoteDetail>()
      await Promise.all(
        withId.map(async (r) => {
          try {
            idNotes.set(r.noteId!, await fetchCachedNote(r.noteId!))
          } catch {
            /* keep text fallback */
          }
        }),
      )
      let listNotes: NoteSummary[] = []
      if (withoutId.length > 0) {
        try {
          listNotes = (await notesApi.list({ page: 1, page_size: 100 })).items
        } catch {
          /* keep text fallback */
        }
      }
      if (cancelled) return
      setItems(
        results.map((raw) => {
          const byId = raw.noteId ? idNotes.get(raw.noteId) : undefined
          const matched = byId || matchNote(listNotes, raw.title)
          return { raw, note: (matched as NoteDetail | undefined) ?? null }
        }),
      )
    })()
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature])

  return (
    <div className="my-3 flex flex-col gap-2">
      {items.map((item) => {
        const title = item.note?.title ?? item.raw.title
        const excerpt = item.note
          ? noteExcerpt(item.note.content || item.raw.excerpt, 50)
          : noteExcerpt(item.raw.excerpt, 50)
        return (
          <button
            type="button"
            key={`${item.note?.id ?? ''}-${item.raw.title}`}
            onClick={() => setPreview(item)}
            className="flex w-full items-start gap-3 rounded-md border border-[var(--color-border)] bg-[var(--color-card)] p-3 text-left hover:bg-[var(--color-accent-bg)]"
          >
            <span className="mt-0.5 text-sm">📄</span>
            <span className="min-w-0 flex-1">
              <span className="block truncate text-sm font-semibold">{title}</span>
              {excerpt && (
                <span className="mt-1 block text-xs text-[var(--color-text-secondary)]">{excerpt}</span>
              )}
            </span>
          </button>
        )
      })}
      {preview && (
        <NotePreviewModal
          title={preview.note?.title ?? preview.raw.title}
          content={preview.note?.content || preview.raw.excerpt}
          onClose={() => setPreview(null)}
        />
      )}
    </div>
  )
}
