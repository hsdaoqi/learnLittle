import { useMemo } from 'react'
import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { parseSearchResults } from '../../utils/noteSearchParser'
import { parseReferencedNotes } from '../../utils/noteReferenceParser'
import SearchResultCards from './SearchResultCards'
import ReferencedNoteCards from './ReferencedNoteCards'

function MarkdownBlock({ content }: { content: string }) {
  return <Markdown remarkPlugins={[remarkGfm]}>{content}</Markdown>
}

export default function MessageContent({
  content,
  role,
}: {
  content: string
  role: string
}) {
  const referenceBlock = useMemo(
    () => (role === 'user' ? parseReferencedNotes(content) : null),
    [content, role],
  )
  const searchBlock = useMemo(
    () => (referenceBlock || role === 'user' ? null : parseSearchResults(content)),
    [content, referenceBlock, role],
  )

  if (referenceBlock) {
    return (
      <div>
        {referenceBlock.prefix.trim() && (
          <div className="whitespace-pre-wrap">{referenceBlock.prefix}</div>
        )}
        <ReferencedNoteCards notes={referenceBlock.notes} />
      </div>
    )
  }
  if (!searchBlock) {
    return <div className="whitespace-pre-wrap">{content}</div>
  }
  return (
    <div>
      {searchBlock.prefix.trim() && <MarkdownBlock content={searchBlock.prefix} />}
      <SearchResultCards results={searchBlock.results} />
      {searchBlock.suffix.trim() && <MarkdownBlock content={searchBlock.suffix} />}
    </div>
  )
}
