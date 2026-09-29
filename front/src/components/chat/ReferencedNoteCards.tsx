import { useState } from 'react'
import { noteExcerpt } from '../../utils/noteSearchParser'
import type { ReferencedNote } from '../../utils/noteReferenceParser'
import NotePreviewModal from './NotePreviewModal'

export default function ReferencedNoteCards({ notes }: { notes: ReferencedNote[] }) {
  const [preview, setPreview] = useState<ReferencedNote | null>(null)
  return (
    <div className="my-3 flex flex-col gap-2">
      {notes.map((note, idx) => (
        <button
          type="button"
          key={note.id ?? `${note.title}-${idx}`}
          onClick={() => setPreview(note)}
          className="flex w-full items-start gap-3 rounded-md border border-[var(--color-border)] bg-[var(--color-card)] p-3 text-left hover:bg-[var(--color-accent-bg)]"
        >
          <span className="mt-0.5 text-sm">📄</span>
          <span className="min-w-0 flex-1">
            <span className="block truncate text-sm font-semibold">{note.title}</span>
            {note.content && (
              <span className="mt-1 block text-xs text-[var(--color-text-secondary)]">
                {noteExcerpt(note.content, 50)}
              </span>
            )}
          </span>
        </button>
      ))}
      {preview && (
        <NotePreviewModal
          title={preview.title}
          content={preview.content}
          onClose={() => setPreview(null)}
        />
      )}
    </div>
  )
}
