import { useEffect, useRef, useState } from 'react'
import { notesApi } from '../api/notes'

export default function CompletionTextarea({
  value, onChange, enabled,
}: { value: string; onChange: (value: string) => void; enabled: boolean }) {
  const input = useRef<HTMLTextAreaElement>(null)
  const [focused, setFocused] = useState(false)
  const [composing, setComposing] = useState(false)
  const [atEnd, setAtEnd] = useState(false)
  const [suggestion, setSuggestion] = useState<{ source: string; text: string } | null>(null)
  const [scrollTop, setScrollTop] = useState(0)
  const [width, setWidth] = useState(0)
  const revision = useRef(0)
  const text = enabled && focused && !composing && atEnd && suggestion?.source === value
    ? suggestion.text : ''

  useEffect(() => {
    const element = input.current
    if (!element) return
    const observer = new ResizeObserver(() => setWidth(element.clientWidth))
    observer.observe(element)
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    const current = ++revision.current
    if (!enabled || !focused || composing || !atEnd || value.trim().length < 10) return
    let active = true
    const timer = window.setTimeout(() => {
      void notesApi.autocomplete(value, value.length).then((data) => {
        if (active && current === revision.current) {
          setSuggestion({ source: value, text: data.completion || '' })
        }
      }).catch(() => {
        if (active) setSuggestion(null)
      })
    }, 900)
    return () => { active = false; window.clearTimeout(timer) }
  }, [value, enabled, focused, composing, atEnd])

  function invalidate() {
    revision.current += 1
    setSuggestion(null)
  }

  function updateCaret(element: HTMLTextAreaElement) {
    setAtEnd(element.selectionStart === element.value.length && element.selectionEnd === element.value.length)
  }

  return (
    <div className="note-completion relative h-full min-h-0 min-w-0 w-full overflow-hidden border-r border-[var(--color-border)] bg-[var(--color-surface)]">
      <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="whitespace-pre-wrap break-words p-6 font-mono text-sm leading-7"
          style={{ width, transform: `translateY(-${scrollTop}px)`, overflowWrap: 'break-word' }}>
          <span className="invisible">{value}</span>
          <span className="text-[var(--color-text-tertiary)]">{text}</span>
        </div>
      </div>
      <textarea ref={input} value={value} aria-label="笔记正文" placeholder="开始记录…"
        onChange={(event) => {
          invalidate()
          onChange(event.target.value)
          setAtEnd(event.target.selectionStart === event.target.value.length
            && event.target.selectionEnd === event.target.value.length)
        }}
        onFocus={(event) => { setFocused(true); updateCaret(event.currentTarget) }}
        onBlur={() => { invalidate(); setFocused(false) }}
        onSelect={(event) => updateCaret(event.currentTarget)}
        onCompositionStart={() => { invalidate(); setComposing(true) }}
        onCompositionEnd={() => setComposing(false)}
        onScroll={(event) => setScrollTop(event.currentTarget.scrollTop)}
        onKeyDown={(event) => {
          if (event.nativeEvent.isComposing || composing) return
          if (event.key === 'Escape') invalidate()
          if (event.key === 'Tab' && !event.shiftKey && text) {
            event.preventDefault()
            onChange(value + text)
            invalidate()
          }
        }}
        className="relative h-full w-full resize-none border-0 p-6 font-mono text-sm leading-7 outline-none"
        style={{ background: 'transparent', overflowWrap: 'break-word' }} />
    </div>
  )
}
