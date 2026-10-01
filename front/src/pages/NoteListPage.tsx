import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { CheckSquare, ChevronLeft, ChevronRight, FileText, Folder, LayoutGrid, LayoutTemplate, PenLine, Plus, Search, Star, Trash2, X } from 'lucide-react'
import CategoryTree from '../components/CategoryTree'
import NoteEditorPage from './NoteEditorPage'
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
  const { noteId } = useParams()
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
  const [treeOpen, setTreeOpen] = useState(false)
  const [treeCollapsed, setTreeCollapsed] = useState(false)
  const [listCollapsed, setListCollapsed] = useState(false)
  const [createOpen, setCreateOpen] = useState(false)
  const [sort, setSort] = useState('updated')
  const [compact, setCompact] = useState(false)
  const [creating, setCreating] = useState(false)

  const options = useMemo(() => flatten(categories), [categories])
  const selectedLabel = selected === UNCATEGORIZED_SENTINEL ? '未分类' : options.find((c) => c.id === selected)?.label.split(' / ').at(-1) || '全部笔记'
  const sortedNotes = useMemo(() => [...notes].sort((a, b) => {
    if (a.is_pinned !== b.is_pinned) return a.is_pinned ? -1 : 1
    if (sort === 'title') return a.title.localeCompare(b.title, 'zh-CN')
    return new Date(sort === 'created' ? b.created_at : b.updated_at).getTime() - new Date(sort === 'created' ? a.created_at : a.updated_at).getTime()
  }), [notes, sort])

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
    setKeyword('')
    setTreeOpen(false)
    void load('')
  }, [selected])

  async function handleCreate(format: NoteFormat) {
    if (creating) return
    setCreating(true)
    setCreateOpen(false)
    try {
      const created = await notesApi.create({
        title: '未命名笔记',
        content: '',
        format,
        category_id:
          selected && selected !== UNCATEGORIZED_SENTINEL ? selected : null,
      })
      await fetchCategories()
      navigate(`/notes/${created.id}`)
      await load()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '创建失败')
    } finally {
      setCreating(false)
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('移入回收站？')) return
    await notesApi.remove(id)
    if (noteId === id) navigate('/')
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
    if (operation === 'delete' && noteId && ids.includes(noteId)) navigate('/')
    setSelectedIds(new Set())
    await fetchCategories()
    await load()
  }

  return (
    <div className="notes-workspace">
      {treeOpen && <button className="category-backdrop" aria-label="关闭分类" onClick={() => setTreeOpen(false)} />}
      <div className={`category-slot ${treeCollapsed ? 'is-collapsed' : ''} ${treeOpen ? 'is-open' : ''}`}>
        <CategoryTree onCollapse={() => { setTreeCollapsed(true); setTreeOpen(false) }} />
        <button className="collapsed-strip" title="展开分类" aria-label="展开分类" onClick={() => setTreeCollapsed(false)}><ChevronRight size={16} /><Folder size={16} /><span>分类管理</span></button>
      </div>
      <section className={`notes-list-panel ${noteId ? 'has-detail' : ''} ${listCollapsed ? 'is-collapsed' : ''}`}>
        <button className="collapsed-strip" title="展开笔记列表" aria-label="展开笔记列表" onClick={() => setListCollapsed(false)}><ChevronRight size={16} /><FileText size={16} /><span>笔记列表</span></button>
        <div className="notes-list-inner">
      <div className="notes-list-toolbar">
        <button className="icon-button mobile-categories" title="分类管理" onClick={() => { setTreeCollapsed(false); setTreeOpen(true) }}><Folder size={16} /></button>
        <h1>{selectedLabel}</h1>
        <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="笔记排序" title="笔记排序">
          <option value="updated">最近修改</option><option value="created">创建时间</option><option value="title">标题</option>
        </select>
        <button className={`icon-button ${compact ? 'is-active' : ''}`} title="切换列表密度" aria-label="切换列表密度" aria-pressed={compact} onClick={() => setCompact((v) => !v)}><LayoutGrid size={15} /></button>
        <button title={batchMode ? '退出批量' : '批量选择'} aria-label={batchMode ? '退出批量' : '批量选择'} className={`icon-button ${batchMode ? 'is-active' : ''}`} onClick={() => { setBatchMode((v) => !v); setSelectedIds(new Set()) }}>
          {batchMode ? <X size={15} /> : <CheckSquare size={15} />}
        </button>
        <div className="create-menu">
          <button title="新建笔记" aria-label="新建笔记" aria-expanded={createOpen} className="icon-button is-active" disabled={creating} onClick={() => setCreateOpen((v) => !v)}><Plus size={17} /></button>
          {createOpen && <><button className="menu-dismiss" aria-label="关闭新建菜单" onClick={() => setCreateOpen(false)} /><div className="dropdown-menu">
            <button onClick={() => void handleCreate('md')}><FileText size={16} />新建 Markdown</button>
            <button onClick={() => void handleCreate('txt')}><FileText size={16} />新建纯文本</button>
            <button onClick={() => navigate('/templates')}><LayoutTemplate size={16} />从模板创建</button>
          </div></>}
        </div>
        <button className="icon-button collapse-list" title="收起笔记列表" onClick={() => setListCollapsed(true)}><ChevronLeft size={15} /></button>
      </div>
      <div className="notes-search">
        <Search size={14} />
        <input
          aria-label="搜索标题或内容"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') void load(keyword)
          }}
          placeholder="搜索标题或内容"
          className="min-w-0 flex-1 bg-transparent text-xs outline-none"
        />
        <span className="count-badge">{total}</span>
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

      <div className={`notes-scroll ${compact ? 'compact' : ''}`}>
        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}
        {loading && <p className="text-sm text-gray-400">加载中…</p>}
        {!loading && notes.length === 0 && (
          <div className="empty-state"><FileText size={36} /><p>{keyword ? '没有找到相关笔记' : '暂无笔记'}</p><button className="primary-button" disabled={creating} onClick={() => void handleCreate('md')}>新建笔记</button></div>
        )}
        <ul className="space-y-3">
          {sortedNotes.map((note) => (
            <li
              key={note.id}
              className={`note-card ${noteId === note.id || selectedIds.has(note.id) ? 'is-selected' : ''}`}
            >
              {batchMode && (
                <input
                  type="checkbox"
                  aria-label={`选择 ${note.title}`}
                  className="absolute right-3 top-3"
                  checked={selectedIds.has(note.id)}
                  onChange={() => toggleSelect(note.id)}
                />
              )}
              <button
                className="note-card-body"
                onClick={() => (batchMode ? toggleSelect(note.id) : navigate(`/notes/${note.id}`))}
              >
                <div className="note-card-heading">
                  <h2 className="truncate font-medium">{note.title || '未命名笔记'}</h2>
                  <span className={`format-badge ${note.format === 'txt' ? 'is-txt' : ''}`}>{note.format === 'txt' ? 'TXT' : 'MD'}</span>
                </div>
                {!!note.tags?.length && <div className="note-tags">{note.tags.slice(0, 3).map((tag) => <span key={tag}>{tag}</span>)}</div>}
                <p className="note-card-meta">{options.find((c) => c.id === note.category_id)?.label.split(' / ').at(-1) || '未分类'} · {new Date(note.updated_at).toLocaleDateString('zh-CN')}</p>
              </button>
              {!batchMode && (
                <div className="note-card-actions">
                  <button
                    title={note.is_pinned ? '取消置顶' : '置顶'}
                    aria-label={note.is_pinned ? '取消置顶' : '置顶'}
                    className={`icon-button ${note.is_pinned ? 'is-pinned' : ''}`}
                    onClick={() => void togglePin(note)}
                  >
                    <Star size={14} fill={note.is_pinned ? 'currentColor' : 'none'} />
                  </button>
                  <button
                    title="删除笔记"
                    aria-label="删除笔记"
                    className="icon-button danger"
                    onClick={() => void handleDelete(note.id)}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
        </div>
      </section>
      <section className={`note-detail-panel ${noteId ? 'has-detail' : ''}`}>
        {noteId ? <NoteEditorPage key={noteId} onSaved={() => void load()} /> : <div className="note-preview-empty"><PenLine size={48} strokeWidth={1.3} /><p>选择一个笔记开始查看</p></div>}
      </section>
    </div>
  )
}
