export interface ReferencedNote {
  id?: string
  title: string
  content: string
}

export interface ParsedReferenceBlock {
  prefix: string
  notes: ReferencedNote[]
  suffix: string
}

const CONTEXT_MARKER = '以下是用户引用的笔记'
const REF_BLOCK_RE = /<referenced_notes>\s*([\s\S]*?)\s*<\/referenced_notes>/
const ID_LINE_RE = /ID[:：]\s*([A-Za-z0-9_-]+)\s*\|\s*标题[:：]\s*(.+)/
const NOTE_HEADER_RE = /【(?:笔记|卡片(?:\s*\d+)?)\s*[｜|：:]\s*([^】]+)】/g

export function parseReferencedNotes(content: string): ParsedReferenceBlock | null {
  const refMatch = REF_BLOCK_RE.exec(content)
  if (!refMatch) return null

  const idEntries: { id: string; title: string }[] = []
  for (const line of refMatch[1].split('\n')) {
    const m = line.trim().match(ID_LINE_RE)
    if (m) idEntries.push({ id: m[1], title: m[2].trim() })
  }

  const contextStart = content.indexOf(CONTEXT_MARKER)
  if (contextStart < 0) return null

  const prefix = content
    .slice(0, contextStart)
    .replace(/\s*[-—–]+\s*$/, '')
    .trim()
  const contextSection = content.slice(contextStart + CONTEXT_MARKER.length, refMatch.index)
  const headers: { title: string; start: number; end: number }[] = []
  NOTE_HEADER_RE.lastIndex = 0
  let hm: RegExpExecArray | null
  while ((hm = NOTE_HEADER_RE.exec(contextSection)) !== null) {
    const title = hm[1].trim()
    if (title) headers.push({ title, start: hm.index, end: hm.index + hm[0].length })
  }

  const notes: ReferencedNote[] = []
  headers.forEach((h, idx) => {
    const body = contextSection
      .slice(h.end, idx + 1 < headers.length ? headers[idx + 1].start : contextSection.length)
      .replace(/^\n+/, '')
      .trim()
    const idEntry =
      idEntries.find((e) => e.title === h.title) ??
      (idEntries.length === headers.length ? idEntries[idx] : undefined)
    notes.push({ ...(idEntry ? { id: idEntry.id } : {}), title: h.title, content: body })
  })
  if (notes.length === 0) return null
  return { prefix, notes, suffix: content.slice(refMatch.index + refMatch[0].length) }
}

export function composeReferencedMessage(
  question: string,
  notes: { id: string; title: string; content: string }[],
): string {
  if (!notes.length) return question
  const cards = notes
    .map((n, i) => `【卡片 ${i + 1}｜${n.title}】\n${n.content}`)
    .join('\n\n')
  const meta = notes.map((n) => `- ID: ${n.id} | 标题: ${n.title}`).join('\n')
  return (
    `${question}\n\n---\n以下是用户引用的笔记卡片：\n\n${cards}\n\n` +
    `<referenced_notes>\n${meta}\n</referenced_notes>`
  )
}
