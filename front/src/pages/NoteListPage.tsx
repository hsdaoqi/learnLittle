import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { notesApi } from '../api/notes'
import { ApiError } from '../api/client'
import { UNCATEGORIZED_SENTINEL, useCategoryStore } from '../stores/useCategoryStore'
import type { Category, NoteFormat, NoteSummary } from '../types/notes'

function flatten(nodes: Category[], prefix = ''): { id: string; label: string }[] {
  return nodes.flatMap((n) => [
    { id: n.id, label: prefix + n.name },
    ...flatten(n.children, `${prefix}${n.name} / `),
  ])
}

export default function NoteListPage() {
  const navigate = useNavigate()
  const selected = useCategoryStore((s) => s.selectedCategoryId)
  const categories = useCategoryStore((s) => s.categories)
  const fetchCategories = useCategoryStore((s) => s.fetchCategories)
  const [notes, setNotes] = useState<NoteSummary[]>([])
  const [total, setTotal] = useState(0)
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [batchMode, setBatchMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [moveTo, setMoveTo] = useState('')

  const options = useMemo(() => flatten(categories), [categories])

  async function load(currentKeyword = keyword) {
    setLoading(true)
    setError('')
    try {
      const data = await notesApi.list({
        page: 1,
        page_size: 50,
        keyword: currentKeyword || undefined,
        category_id:
          selected && selected !== UNCATEGORIZED_SENTINEL ? selected : undefined,
        uncategorized: selected === UNCATEGORIZED_SENTINEL,
      })
      setNotes(data.items)
      setTotal(data.total)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    setSelectedIds(new Set())
    void load('')
  }, [selected])

  async function handleCreate(format: NoteFormat) {
    const created = await notesApi.create({
      title: '未命名笔记',
      content: '',
      format,
      category_id:
        selected && selected !== UNCATEGORIZED_SENTINEL ? selected : null,
    })
    await fetchCategories()
    navigate(`/notes/${created.id}`)
  }

  async function handleDelete(id: string) {
    if (!window.confirm('移入回收站？')) return
    await notesApi.remove(id)
    await fetchCategories()
    await load()
  }

  async function togglePin(note: NoteSummary) {
    await notesApi.update(note.id, { is_pinned: !note.is_pinned })
    await load()
  }

  function toggleSelect(id: string) {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  async function runBatch(operation: 'delete' | 'pin' | 'unpin' | 'move') {
    const ids = Array.from(selectedIds)
    if (ids.length === 0) return
    if (operation === 'delete' && !window.confirm(`把 ${ids.length} 篇移入回收站？`)) return
    await notesApi.batch({
      note_ids: ids,
      operation,
      target_category_id: operation === 'move' ? moveTo || null : undefined,
    })
    setSelectedIds(new Set())
    await fetchCategories()
    await load()
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <h1 className="text-base font-semibold">笔记</h1>
        <span className="text-xs text-gray-400">{total} 篇</span>
        <input
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') void load(keyword)
          }}
          placeholder="搜索标题或内容"
          className="ml-auto w-56 rounded-md border border-gray-300 px-3 py-1.5 text-sm outline-none focus:border-indigo-500"
        />
        <button
          onClick={() => {
            setBatchMode((v) => !v)
            setSelectedIds(new Set())
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
        >
          {batchMode ? '退出批量' : '批量'}
        </button>
        <button
          onClick={() => void handleCreate('md')}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700"
        >
          新建 Markdown
        </button>
        <button
          onClick={() => void handleCreate('txt')}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
        >
          新建纯文本
        </button>
        <button
          onClick={() => navigate('/templates')}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50"
        >
          模板
        </button>
      </div>

      {batchMode && (
        <div className="flex flex-wrap items-center gap-2 border-b border-gray-100 bg-gray-50 px-4 py-2 text-sm">
          <span className="text-gray-500">已选 {selectedIds.size} 篇</span>
          <button className="rounded px-2 py-1 text-indigo-600" onClick={() => void runBatch('pin')}>
            置顶
          </button>
          <button className="rounded px-2 py-1 text-indigo-600" onClick={() => void runBatch('unpin')}>
            取消置顶
          </button>
          <select
            value={moveTo}
            onChange={(e) => setMoveTo(e.target.value)}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            <option value="">未分类</option>
            {options.map((opt) => (
              <option key={opt.id} value={opt.id}>
                {opt.label}
              </option>
            ))}
          </select>
          <button className="rounded px-2 py-1 text-indigo-600" onClick={() => void runBatch('move')}>
            移动
          </button>
          <button className="rounded px-2 py-1 text-red-500" onClick={() => void runBatch('delete')}>
            删除
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}
        {loading && <p className="text-sm text-gray-400">加载中…</p>}
        {!loading && notes.length === 0 && (
          <p className="text-sm text-gray-400">还没有笔记，点右上角新建一篇。</p>
        )}
        <ul className="space-y-2">
          {notes.map((note) => (
            <li
              key={note.id}
              className="flex items-start justify-between rounded-xl bg-white p-4 shadow-card"
            >
              {batchMode && (
                <input
                  type="checkbox"
                  className="mt-1 mr-3"
                  checked={selectedIds.has(note.id)}
                  onChange={() => toggleSelect(note.id)}
                />
              )}
              <button
                className="min-w-0 flex-1 text-left"
                onClick={() => (batchMode ? toggleSelect(note.id) : navigate(`/notes/${note.id}`))}
              >
                <div className="flex items-center gap-2">
                  {note.is_pinned && (
                    <span className="text-xs text-amber-500">置顶</span>
                  )}
                  <span className="rounded bg-gray-100 px-1.5 py-0.5 text-[10px] uppercase text-gray-500">
                    {note.format === 'txt' ? 'TXT' : 'MD'}
                  </span>
                  <h2 className="truncate font-medium">{note.title || '未命名笔记'}</h2>
                </div>
                <p className="mt-1 text-xs text-gray-400">
                  {new Date(note.updated_at).toLocaleString('zh-CN')}
                  {note.tags && note.tags.length > 0 ? ` · ${note.tags.join(' / ')}` : ''}
                </p>
              </button>
              {!batchMode && (
                <div className="ml-3 flex shrink-0 gap-1">
                  <button
                    className="rounded px-2 py-1 text-xs text-gray-500 hover:bg-gray-100"
                    onClick={() => void togglePin(note)}
                  >
                    {note.is_pinned ? '取消置顶' : '置顶'}
                  </button>
                  <button
                    className="rounded px-2 py-1 text-xs text-red-500 hover:bg-red-50"
                    onClick={() => void handleDelete(note.id)}
                  >
                    删除
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
