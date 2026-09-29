import { lazy, Suspense, useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { notesApi } from '../api/notes'
import { ApiError } from '../api/client'
import TagInput from '../components/TagInput'
import { useCategoryStore } from '../stores/useCategoryStore'
import type { Category } from '../types/notes'

const MarkdownPreview = lazy(() => import('../components/MarkdownPreview'))

function flatten(nodes: Category[], prefix = ''): { id: string; label: string }[] {
  return nodes.flatMap((n) => [
    { id: n.id, label: prefix + n.name },
    ...flatten(n.children, `${prefix}${n.name} / `),
  ])
}

export default function NoteEditorPage() {
  const { noteId } = useParams()
  const navigate = useNavigate()
  const categories = useCategoryStore((s) => s.categories)
  const fetchCategories = useCategoryStore((s) => s.fetchCategories)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [categoryId, setCategoryId] = useState<string>('')
  const [saving, setSaving] = useState(false)
  const [savedAt, setSavedAt] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [loaded, setLoaded] = useState(false)
  const [showPreview, setShowPreview] = useState(true)
  const [format, setFormat] = useState<'md' | 'txt'>('md')
  const [aiBusy, setAiBusy] = useState(false)

  useEffect(() => {
    if (!noteId) return
    notesApi
      .detail(noteId)
      .then((note) => {
        setTitle(note.title)
        setContent(note.content)
        setTags(note.tags ?? [])
        setCategoryId(note.category_id ?? '')
        setFormat(note.format === 'txt' ? 'txt' : 'md')
        setShowPreview(note.format !== 'txt')
        setLoaded(true)
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : '加载失败'))
  }, [noteId])

  const save = useCallback(async () => {
    if (!noteId) return
    setSaving(true)
    setError('')
    try {
      await notesApi.update(noteId, {
        title: title.trim() || '未命名笔记',
        content,
        tags,
        category_id: categoryId || null,
      })
      setSavedAt(new Date().toLocaleTimeString('zh-CN'))
      await fetchCategories()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '保存失败')
    } finally {
      setSaving(false)
    }
  }, [noteId, title, content, tags, categoryId, fetchCategories])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault()
        void save()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [save])

  async function handleDelete() {
    if (!noteId || !window.confirm('移入回收站？')) return
    await notesApi.remove(noteId)
    await fetchCategories()
    navigate('/')
  }

  async function runWrite(mode: 'continue' | 'expand' | 'summary') {
    setAiBusy(true)
    setError('')
    try {
      const data = await notesApi.writeAssistant(content, mode)
      if (mode === 'summary') setContent((data.result || '').trim() || content)
      else if (data.result) setContent((content ? `${content}\n\n` : '') + data.result)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'AI 辅助失败')
    } finally {
      setAiBusy(false)
    }
  }

  async function runAutoTag() {
    setAiBusy(true)
    setError('')
    try {
      const data = await notesApi.autoTag(title, content)
      if (data.tags.length) {
        setTags(Array.from(new Set([...tags, ...data.tags])))
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '打标签失败')
    } finally {
      setAiBusy(false)
    }
  }

  const options = flatten(categories)

  if (!loaded && !error) {
    return <p className="p-6 text-sm text-gray-400">加载中…</p>
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex flex-wrap items-center gap-3 border-b border-gray-200 bg-white px-4 py-3">
        <Link to="/" className="text-sm text-gray-500 hover:text-gray-800">
          ← 返回
        </Link>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="min-w-40 flex-1 border-none text-base font-medium outline-none"
          placeholder="标题"
        />
        <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-500">
          {format === 'txt' ? '纯文本' : 'Markdown'}
        </span>
        <select
          value={categoryId}
          onChange={(e) => setCategoryId(e.target.value)}
          className="rounded-md border border-gray-300 px-2 py-1 text-sm"
        >
          <option value="">未分类</option>
          {options.map((opt) => (
            <option key={opt.id} value={opt.id}>
              {opt.label}
            </option>
          ))}
        </select>
        {format !== 'txt' && (
          <button
            onClick={() => setShowPreview((v) => !v)}
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-50"
          >
            {showPreview ? '隐藏预览' : '显示预览'}
          </button>
        )}
        <button
          onClick={() => void save()}
          disabled={saving}
          className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          {saving ? '保存中…' : '保存'}
        </button>
        <button
          onClick={async () => {
            if (!noteId) return
            try {
              await notesApi.exportEmail(noteId, { format })
              setSavedAt('已发到邮箱')
            } catch (err) {
              setError(err instanceof ApiError ? err.message : '发送失败')
            }
          }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
        >
          发到邮箱
        </button>
        <button
          onClick={() => void handleDelete()}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-red-500 hover:bg-red-50"
        >
          删除
        </button>
      </div>

      <div className="flex items-center gap-3 border-b border-gray-100 bg-white px-4 py-2">
        <TagInput tags={tags} onChange={setTags} />
        <button
          disabled={aiBusy}
          onClick={() => void runWrite('continue')}
          className="shrink-0 rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
        >
          续写
        </button>
        <button
          disabled={aiBusy}
          onClick={() => void runWrite('expand')}
          className="shrink-0 rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
        >
          扩写
        </button>
        <button
          disabled={aiBusy}
          onClick={() => void runWrite('summary')}
          className="shrink-0 rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
        >
          摘要
        </button>
        <button
          disabled={aiBusy}
          onClick={() => void runAutoTag()}
          className="shrink-0 rounded px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
        >
          自动标签
        </button>
        {savedAt && <span className="shrink-0 text-xs text-gray-400">已保存 {savedAt}</span>}
      </div>

      {error && <p className="px-4 py-2 text-sm text-red-500">{error}</p>}

      <div className={`min-h-0 flex-1 ${format !== 'txt' && showPreview ? 'grid grid-cols-2' : 'flex'}`}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={format === 'txt' ? '纯文本笔记… Ctrl+S 保存' : '用 Markdown 写笔记… Ctrl+S 保存'}
          className="h-full min-h-0 w-full resize-none border-r border-gray-200 bg-white p-6 font-mono text-sm outline-none"
        />
        {format !== 'txt' && showPreview && (
          <div className="h-full overflow-y-auto bg-gray-50 p-6">
            <Suspense fallback={<p className="text-sm text-gray-400">预览加载中…</p>}>
              <MarkdownPreview content={content} />
            </Suspense>
          </div>
        )}
      </div>
    </div>
  )
}
