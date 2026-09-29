import { useEffect, useState } from 'react'
import { UNCATEGORIZED_SENTINEL, useCategoryStore } from '../stores/useCategoryStore'
import type { Category } from '../types/notes'
import { ApiError } from '../api/client'

function TreeNode({
  node,
  depth,
}: {
  node: Category
  depth: number
}) {
  const selected = useCategoryStore((s) => s.selectedCategoryId)
  const selectCategory = useCategoryStore((s) => s.selectCategory)
  const renameCategory = useCategoryStore((s) => s.renameCategory)
  const deleteCategory = useCategoryStore((s) => s.deleteCategory)
  const createCategory = useCategoryStore((s) => s.createCategory)
  const [open, setOpen] = useState(true)
  const [renaming, setRenaming] = useState(false)
  const [name, setName] = useState(node.name)
  const [adding, setAdding] = useState(false)
  const [childName, setChildName] = useState('')
  const [error, setError] = useState('')

  async function submitRename() {
    const trimmed = name.trim()
    if (!trimmed || trimmed === node.name) {
      setRenaming(false)
      setName(node.name)
      return
    }
    try {
      await renameCategory(node.id, trimmed)
      setRenaming(false)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '重命名失败')
    }
  }

  async function submitChild() {
    const trimmed = childName.trim()
    if (!trimmed) {
      setAdding(false)
      return
    }
    try {
      await createCategory(trimmed, node.id)
      setChildName('')
      setAdding(false)
      setOpen(true)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '创建失败')
    }
  }

  async function handleDelete() {
    if (!window.confirm(`删除分类「${node.name}」？子分类会提升到上一级，笔记变为未分类。`)) return
    try {
      await deleteCategory(node.id)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '删除失败')
    }
  }

  const active = selected === node.id

  return (
    <div>
      <div
        className={`group flex items-center gap-1 rounded-md px-2 py-1 text-sm ${
          active ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        style={{ paddingLeft: `${8 + depth * 12}px` }}
      >
        {node.children.length > 0 ? (
          <button
            className="w-4 text-xs text-gray-400"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? '折叠' : '展开'}
          >
            {open ? '▾' : '▸'}
          </button>
        ) : (
          <span className="w-4" />
        )}

        {renaming ? (
          <input
            autoFocus
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={submitRename}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void submitRename()
              if (e.key === 'Escape') {
                setRenaming(false)
                setName(node.name)
              }
            }}
            className="min-w-0 flex-1 rounded border border-indigo-300 px-1 py-0.5 text-sm"
          />
        ) : (
          <button
            className="min-w-0 flex-1 truncate text-left"
            onClick={() => selectCategory(node.id)}
          >
            {node.icon ? `${node.icon} ` : ''}
            {node.name}
            <span className="ml-1 text-xs text-gray-400">{node.note_count}</span>
          </button>
        )}

        <div className="hidden gap-0.5 group-hover:flex">
          {depth < 2 && (
            <button
              title="新建子分类"
              className="rounded px-1 text-xs text-gray-500 hover:bg-white"
              onClick={() => setAdding(true)}
            >
              +
            </button>
          )}
          <button
            title="重命名"
            className="rounded px-1 text-xs text-gray-500 hover:bg-white"
            onClick={() => setRenaming(true)}
          >
            改
          </button>
          <button
            title="删除"
            className="rounded px-1 text-xs text-red-500 hover:bg-white"
            onClick={() => void handleDelete()}
          >
            删
          </button>
        </div>
      </div>

      {error && <p className="px-3 py-0.5 text-xs text-red-500">{error}</p>}

      {adding && (
        <div style={{ paddingLeft: `${20 + depth * 12}px` }} className="py-1">
          <input
            autoFocus
            value={childName}
            placeholder="子分类名"
            onChange={(e) => setChildName(e.target.value)}
            onBlur={() => void submitChild()}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void submitChild()
              if (e.key === 'Escape') setAdding(false)
            }}
            className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>
      )}

      {open &&
        node.children.map((child) => <TreeNode key={child.id} node={child} depth={depth + 1} />)}
    </div>
  )
}

export default function CategoryTree() {
  const categories = useCategoryStore((s) => s.categories)
  const uncategorizedCount = useCategoryStore((s) => s.uncategorizedCount)
  const selected = useCategoryStore((s) => s.selectedCategoryId)
  const loading = useCategoryStore((s) => s.loading)
  const error = useCategoryStore((s) => s.error)
  const fetchCategories = useCategoryStore((s) => s.fetchCategories)
  const selectCategory = useCategoryStore((s) => s.selectCategory)
  const createCategory = useCategoryStore((s) => s.createCategory)
  const [addingRoot, setAddingRoot] = useState(false)
  const [rootName, setRootName] = useState('')

  useEffect(() => {
    void fetchCategories()
  }, [fetchCategories])

  async function submitRoot() {
    const trimmed = rootName.trim()
    if (!trimmed) {
      setAddingRoot(false)
      return
    }
    try {
      await createCategory(trimmed, null)
      setRootName('')
      setAddingRoot(false)
    } catch {
      setAddingRoot(false)
    }
  }

  return (
    <aside className="flex h-full w-60 shrink-0 flex-col border-r border-[var(--color-border)] bg-[var(--color-sidebar-bg)]">
      <div className="flex items-center justify-between px-3 py-3">
        <span className="text-sm font-semibold">分类</span>
        <button
          className="rounded px-2 text-sm text-indigo-600 hover:bg-indigo-50"
          onClick={() => setAddingRoot(true)}
        >
          + 新建
        </button>
      </div>

      <button
        className={`mx-2 rounded-md px-2 py-1.5 text-left text-sm ${
          selected === null ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        onClick={() => selectCategory(null)}
      >
        全部笔记
      </button>
      <button
        className={`mx-2 mb-2 rounded-md px-2 py-1.5 text-left text-sm ${
          selected === UNCATEGORIZED_SENTINEL ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        onClick={() => selectCategory(UNCATEGORIZED_SENTINEL)}
      >
        未分类
        <span className="ml-1 text-xs text-gray-400">{uncategorizedCount}</span>
      </button>

      {addingRoot && (
        <div className="px-3 pb-2">
          <input
            autoFocus
            value={rootName}
            placeholder="新分类名"
            onChange={(e) => setRootName(e.target.value)}
            onBlur={() => void submitRoot()}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void submitRoot()
              if (e.key === 'Escape') setAddingRoot(false)
            }}
            className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>
      )}

      <div className="flex-1 overflow-y-auto pb-4">
        {loading && <p className="px-3 text-xs text-gray-400">加载中…</p>}
        {error && (
          <p className="px-3 text-xs text-red-500">
            {error}
            <button className="ml-1 underline" onClick={() => void fetchCategories()}>
              重试
            </button>
          </p>
        )}
        {categories.map((node) => (
          <TreeNode key={node.id} node={node} depth={0} />
        ))}
      </div>
    </aside>
  )
}
