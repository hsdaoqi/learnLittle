export interface ParsedSearchResult {
  title: string
  excerpt: string
  noteId?: string
}

export interface ParsedSearchBlock {
  prefix: string
  results: ParsedSearchResult[]
  suffix: string
}

const INTRO_RE =
  /^[ \t]*[^\n]*?(?:找到|搜索|检索|查询|搜到|查到)了?(?:\s*(?:\d+|几)\s*篇|以下)[^\n]*?笔记[^\n]*?[:：]\s*/m
const LIST_PREFIX_RE = /^(\d+[.、)]|[-*])\s*(.+)$/
const TITLE_SEPARATORS = [' - ', ' – ', ' — ', ' − ']

function extractNoteId(text: string): { noteId?: string; cleaned: string } {
  const idMatch = text.match(/\(?ID[:：]\s*([A-Za-z0-9_-]+)\)?/i)
  const cleaned = text
    .replace(/\(?ID[:：]\s*[A-Za-z0-9_-]+\)?/gi, '')
    .replace(/\*\*/g, '')
    .trim()
  return { noteId: idMatch?.[1], cleaned }
}

function parseItemText(raw: string, continuation: string): ParsedSearchResult {
  const { noteId, cleaned } = extractNoteId(raw)
  let title = cleaned
  let excerpt = continuation.trim()
  let sepIdx = -1
  let sepLen = 0
  for (const sep of TITLE_SEPARATORS) {
    const idx = cleaned.lastIndexOf(sep)
    if (idx > sepIdx) {
      sepIdx = idx
      sepLen = sep.length
    }
  }
  if (sepIdx > 0) {
    title = cleaned.slice(0, sepIdx).trim()
    excerpt = excerpt || cleaned.slice(sepIdx + sepLen).trim()
  } else if (!excerpt) {
    const colonIdx = cleaned.search(/[:：]/)
    if (colonIdx > 0) {
      excerpt = cleaned.slice(colonIdx + 1).trim()
      title = cleaned.slice(0, colonIdx).trim()
    }
  }
  return { title, excerpt, ...(noteId ? { noteId } : {}) }
}

export function parseSearchResults(content: string): ParsedSearchBlock | null {
  const introMatch = INTRO_RE.exec(content)
  if (!introMatch) return null

  const countMatch = introMatch[0].match(/(\d+)\s*篇/)
  const hasCount = countMatch !== null
  const maxItems = hasCount ? Math.min(parseInt(countMatch![1], 10), 20) : 20
  const rest = content.slice(introMatch.index + introMatch[0].length)
  const lines = rest.split(/\r?\n/)
  const results: ParsedSearchResult[] = []
  let i = 0
  while (i < lines.length && !lines[i].trim()) i++

  while (i < lines.length && results.length < maxItems) {
    const trimmed = lines[i].trim()
    if (!trimmed) {
      let k = i + 1
      while (k < lines.length && !lines[k].trim()) k++
      if (k < lines.length && results.length > 0 && LIST_PREFIX_RE.test(lines[k].trim())) {
        i = k
        continue
      }
      break
    }
    const prefixMatch = trimmed.match(LIST_PREFIX_RE)
    if (prefixMatch) {
      let j = i + 1
      const excerptLines: string[] = []
      while (j < lines.length) {
        const next = lines[j].trim()
        if (!next || LIST_PREFIX_RE.test(next)) break
        excerptLines.push(next)
        j++
      }
      const item = parseItemText(prefixMatch[2], excerptLines.join(' '))
      if (item.title) results.push(item)
      i = j
    } else {
      const hasSeparator = TITLE_SEPARATORS.some((s) => trimmed.includes(s))
      if (!hasSeparator && !hasCount) {
        const nextNonBlank = lines.slice(i + 1).find((l) => l.trim())
        const listContinues = !!nextNonBlank && LIST_PREFIX_RE.test(nextNonBlank.trim())
        if (!listContinues) break
        if (results.length > 0) {
          const last = results[results.length - 1]
          results[results.length - 1] = {
            ...last,
            excerpt: [last.excerpt, trimmed].filter(Boolean).join(' '),
          }
        }
        i++
        continue
      }
      const item = parseItemText(trimmed, '')
      if (item.title) results.push(item)
      i++
    }
  }

  if (results.length === 0) return null
  return {
    prefix: content.slice(0, introMatch.index) + introMatch[0],
    results,
    suffix: lines.slice(i).join('\n'),
  }
}

export function noteExcerpt(text: string, max = 50): string {
  const collapsed = (text || '').replace(/\s+/g, ' ').trim()
  if (collapsed.length <= max) return collapsed
  return collapsed.slice(0, max) + '…'
}
