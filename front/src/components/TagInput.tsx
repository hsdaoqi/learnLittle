import { useState, type KeyboardEvent } from 'react'

export default function TagInput({
  tags,
  onChange,
}: {
  tags: string[]
  onChange: (tags: string[]) => void
}) {
  const [draft, setDraft] = useState('')

  function add(raw: string) {
    const tag = raw.trim()
    if (!tag || tags.includes(tag)) {
      setDraft('')
      return
    }
    onChange([...tags, tag])
    setDraft('')
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault()
      add(draft)
    } else if (e.key === 'Backspace' && draft === '' && tags.length > 0) {
      onChange(tags.slice(0, -1))
    }
  }

  return (
    <div className="flex min-w-0 flex-1 flex-wrap items-center gap-1 rounded-md border border-gray-300 px-2 py-1">
      {tags.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700"
        >
          {tag}
          <button
            type="button"
            className="text-indigo-400 hover:text-indigo-700"
            onClick={() => onChange(tags.filter((t) => t !== tag))}
            aria-label={`删除标签 ${tag}`}
          >
            ×
          </button>
        </span>
      ))}
      <input
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={onKeyDown}
        onBlur={() => add(draft)}
        placeholder={tags.length === 0 ? '回车添加标签' : ''}
        className="min-w-24 flex-1 border-none bg-transparent py-0.5 text-sm outline-none"
      />
    </div>
  )
}
