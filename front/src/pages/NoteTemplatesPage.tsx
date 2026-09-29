import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { templateApi, type NoteTemplate } from '../api/templates'
import { ApiError } from '../api/client'
import { useCategoryStore } from '../stores/useCategoryStore'

export default function NoteTemplatesPage() {
  const navigate = useNavigate()
  const fetchCategories = useCategoryStore((s) => s.fetchCategories)
  const [templates, setTemplates] = useState<NoteTemplate[]>([])
  const [name, setName] = useState('')
  const [markdown, setMarkdown] = useState('## 标题\n\n')
  const [error, setError] = useState('')

  async function load() {
    try {
      const data = await templateApi.list()
      setTemplates(data.templates)
      setError('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '加载失败')
    }
  }

  useEffect(() => {
    void load()
  }, [])

  async function handleCreate() {
    if (!name.trim()) return
    await templateApi.create({
      name: name.trim(),
      content_structure: { markdown },
    })
    setName('')
    setMarkdown('## 标题\n\n')
    await load()
  }

  async function handleApply(id: number) {
    const created = await templateApi.apply(id)
    await fetchCategories()
    navigate(`/notes/${created.id}`)
  }

  async function handleDelete(id: number) {
    if (!window.confirm('删除这个模板？')) return
    await templateApi.remove(id)
    await load()
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-gray-200 bg-white px-4 py-3">
        <h1 className="text-base font-semibold">笔记模板</h1>
        <p className="mt-1 text-xs text-gray-400">保存常用骨架，套用后直接进入编辑器。</p>
      </div>
      <div className="grid min-h-0 flex-1 gap-4 overflow-y-auto p-4 md:grid-cols-2">
        <div className="rounded-xl bg-white p-4 shadow-card">
          <h2 className="mb-3 text-sm font-medium">新建模板</h2>
          {error && <p className="mb-2 text-sm text-red-500">{error}</p>}
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="模板名称"
            className="mb-2 w-full rounded-md border border-gray-300 px-3 py-1.5 text-sm outline-none"
          />
          <textarea
            value={markdown}
            onChange={(e) => setMarkdown(e.target.value)}
            className="mb-3 h-48 w-full resize-none rounded-md border border-gray-300 p-3 font-mono text-sm outline-none"
          />
          <button
            onClick={() => void handleCreate()}
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white hover:bg-indigo-700"
          >
            保存模板
          </button>
        </div>
        <ul className="space-y-2">
          {templates.length === 0 && (
            <li className="text-sm text-gray-400">还没有模板。</li>
          )}
          {templates.map((tpl) => (
            <li key={tpl.id} className="rounded-xl bg-white p-4 shadow-card">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{tpl.name}</p>
                  {tpl.category && (
                    <p className="text-xs text-gray-400">{tpl.category}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    className="text-xs text-indigo-600"
                    onClick={() => void handleApply(tpl.id)}
                  >
                    套用
                  </button>
                  <button
                    className="text-xs text-red-500"
                    onClick={() => void handleDelete(tpl.id)}
                  >
                    删除
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
