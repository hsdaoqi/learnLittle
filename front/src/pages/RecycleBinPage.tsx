import { useEffect, useState } from 'react'
import { notesApi } from '../api/notes'
import { categoryApi } from '../api/category'
import { ApiError } from '../api/client'
import { useCategoryStore } from '../stores/useCategoryStore'
import type { DeletedCategory, NoteSummary } from '../types/notes'
import { RotateCcw, Trash2 } from 'lucide-react'
import SectionSidebar from '../components/layout/SectionSidebar'

export default function RecycleBinPage() {
  const fetchCategories = useCategoryStore((s) => s.fetchCategories)
  const [tab, setTab] = useState<'notes' | 'categories'>('notes')
  const [notes, setNotes] = useState<NoteSummary[]>([])
  const [categories, setCategories] = useState<DeletedCategory[]>([])
  const [error, setError] = useState('')

  async function load() {
    try {
      const [noteList, catBin] = await Promise.all([
        notesApi.recycleBin(),
        categoryApi.recycleBin(),
      ])
      setNotes(noteList)
      setCategories(catBin.categories)
      setError('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function restoreNote(id: string) {
    await notesApi.restore(id)
    await fetchCategories()
    await load()
  }

  async function wipeNote(id: string) {
    if (!window.confirm('彻底删除后无法恢复，确定吗？')) return
    await notesApi.permanentDelete(id)
    await load()
  }

  async function restoreCategory(id: string) {
    await categoryApi.restore(id)
    await fetchCategories()
    await load()
  }

  async function wipeCategory(id: string) {
    if (!window.confirm('彻底删除分类后无法恢复，确定吗？')) return
    await categoryApi.permanentDelete(id)
    await fetchCategories()
    await load()
  }

  const empty =
    (tab === 'notes' && notes.length === 0) || (tab === 'categories' && categories.length === 0)

  return (
    <div className="section-workspace">
    <SectionSidebar title="回收站" items={notes.map((note) => ({ id: note.id, title: note.title || '未命名笔记', meta: typeof note.days_remaining === 'number' ? `剩余 ${note.days_remaining} 天` : undefined }))} onSelect={(id) => { setTab('notes'); requestAnimationFrame(() => document.getElementById(`deleted-${id}`)?.scrollIntoView({ block: 'center' })) }} />
    <div className="recycle-page min-w-0 flex-1 overflow-y-auto p-6">
      <h1 className="mb-4 text-base font-semibold">回收站</h1>
      <div className="recycle-tabs mb-4 flex gap-2" role="tablist">
        <button
          role="tab"
          aria-selected={tab === 'notes'}
          className={`rounded-md px-3 py-1.5 text-sm ${
            tab === 'notes'
              ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
              : 'border border-[var(--color-border)]'
          }`}
          onClick={() => setTab('notes')}
        >
          笔记 {notes.length}
        </button>
        <button
          role="tab"
          aria-selected={tab === 'categories'}
          className={`rounded-md px-3 py-1.5 text-sm ${
            tab === 'categories'
              ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
              : 'border border-[var(--color-border)]'
          }`}
          onClick={() => setTab('categories')}
        >
          分类 {categories.length}
        </button>
      </div>
      {error && <p className="mb-3 text-sm text-red-500">{error}</p>}
      {empty && <div className="empty-state"><Trash2 size={40} strokeWidth={1.5} /><p>回收站为空</p></div>}

      {tab === 'notes' && (
        <ul className="space-y-2">
          {notes.map((note) => (
            <li
              key={note.id}
              id={`deleted-${note.id}`}
              className="flex items-center justify-between rounded-xl bg-[var(--color-surface)] p-4 shadow-card"
            >
              <div>
                <p className="font-medium">{note.title || '未命名笔记'}</p>
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  {new Date(note.updated_at).toLocaleString('zh-CN')}
                  {typeof note.days_remaining === 'number' ? ` · 剩余 ${note.days_remaining} 天` : ''}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  className="icon-button"
                  title="恢复笔记"
                  aria-label="恢复笔记"
                  onClick={() => void restoreNote(note.id)}
                >
                  <RotateCcw size={16} />
                </button>
                <button
                  className="icon-button danger"
                  title="彻底删除笔记"
                  aria-label="彻底删除笔记"
                  onClick={() => void wipeNote(note.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {tab === 'categories' && (
        <ul className="space-y-2">
          {categories.map((cat) => (
            <li
              key={cat.id}
              className="flex items-center justify-between rounded-xl bg-[var(--color-surface)] p-4 shadow-card"
            >
              <div>
                <p className="font-medium">{cat.name}</p>
                <p className="text-xs text-[var(--color-text-tertiary)]">
                  剩余 {cat.days_remaining} 天
                  {cat.descendant_count ? ` · ${cat.descendant_count} 个子孙` : ''}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  className="icon-button"
                  title="恢复分类"
                  aria-label="恢复分类"
                  onClick={() => void restoreCategory(cat.id)}
                >
                  <RotateCcw size={16} />
                </button>
                <button
                  className="icon-button danger"
                  title="彻底删除分类"
                  aria-label="彻底删除分类"
                  onClick={() => void wipeCategory(cat.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
    </div>
  )
}
