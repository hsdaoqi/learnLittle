import { useEffect, useState } from 'react'
import { UNCATEGORIZED_SENTINEL, useCategoryStore } from '../stores/useCategoryStore'
import type { Category } from '../types/notes'
import { ApiError } from '../api/client'
import { categoryApi } from '../api/category'
import CategoryManager from './CategoryManager'
import { ChevronDown, ChevronRight, Folder, FolderOpen, Files, Inbox, Plus, Pencil, Trash2, PanelLeftClose, Settings2 } from 'lucide-react'

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
  const [dragOver, setDragOver] = useState(false)
  const categories = useCategoryStore((s) => s.categories)
  const refresh = useCategoryStore((s) => s.fetchCategories)

  async function drop(sourceId: string) {
    function flatten(nodes: Category[]): Category[] {
      return nodes.flatMap((item) => [item, ...flatten(item.children)])
    }
    const source = flatten(categories).find((item) => item.id === sourceId)
    if (!source || source.id === node.id || source.parent_id !== node.parent_id) return
    const siblings = flatten(categories).filter((item) => item.parent_id === node.parent_id)
    const ids = siblings.map((item) => item.id).filter((id) => id !== sourceId)
    ids.splice(ids.indexOf(node.id), 0, sourceId)
    try {
      await categoryApi.reorder(node.parent_id, ids)
      await refresh()
    } catch (err) { setError(err instanceof ApiError ? err.message : '排序失败') }
  }

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
        draggable={!renaming && !adding}
        onDragStart={(e) => { e.stopPropagation(); e.dataTransfer.setData('application/x-category-id', node.id) }}
        onDragOver={(e) => {
          if (e.dataTransfer.types.includes('application/x-category-id')) {
            e.preventDefault(); e.stopPropagation(); setDragOver(true)
          }
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault(); e.stopPropagation(); setDragOver(false)
          void drop(e.dataTransfer.getData('application/x-category-id'))
        }}
        className={`group flex items-center gap-1 rounded-lg px-2 py-2 text-sm ${
          active ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        style={{ paddingLeft: `${8 + depth * 12}px`, boxShadow: dragOver ? 'inset 0 2px var(--color-accent)' : undefined }}
      >
        {node.children.length > 0 ? (
          <button
            className="w-4 text-xs text-gray-400"
            onClick={() => setOpen((v) => !v)}
            aria-label={open ? '折叠' : '展开'}
          >
            {open ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
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
            className="flex min-w-0 flex-1 items-center gap-2 text-left"
            title={node.name}
            onClick={() => selectCategory(node.id)}
          >
            {active ? <FolderOpen size={15} className="shrink-0 text-[var(--color-accent)]" /> : <Folder size={15} className="shrink-0 text-gray-400" />}
            <span className="truncate">{node.name}</span>
            <span className="count-badge ml-auto">{node.note_count}</span>
          </button>
        )}

        <div className="tree-actions flex gap-0.5">
          {depth < 2 && (
            <button
              title="新建子分类"
              className="rounded px-1 text-xs text-gray-500 hover:bg-white"
              onClick={() => setAdding(true)}
            >
              <Plus size={12} />
            </button>
          )}
          <button
            title="重命名"
            className="rounded px-1 text-xs text-gray-500 hover:bg-white"
            onClick={() => setRenaming(true)}
          >
            <Pencil size={12} />
          </button>
          <button
            title="删除"
            className="rounded px-1 text-xs text-red-500 hover:bg-white"
            onClick={() => void handleDelete()}
          >
            <Trash2 size={12} />
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

export default function CategoryTree({ onCollapse }: { onCollapse?: () => void }) {
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
  const [managing, setManaging] = useState(false)

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
    <aside className="category-panel flex h-full w-[220px] shrink-0 flex-col border-r border-[var(--color-border)] bg-[var(--color-sidebar-bg)]">
      <div className="flex h-14 shrink-0 items-center justify-between border-b border-[var(--color-border)] px-4">
        <span className="text-sm font-semibold">分类管理</span>
        <div className="flex items-center gap-1">
        <button className="icon-button" title="移动、合并与排序" aria-label="分类管理"
          onClick={() => setManaging(true)}><Settings2 size={16} /></button>
        <button
          className="icon-button"
          title="新建分类"
          aria-label="新建分类"
          onClick={() => setAddingRoot(true)}
        >
          <Plus size={16} />
        </button>
        {onCollapse && <button className="icon-button" title="收起分类" aria-label="收起分类" onClick={onCollapse}><PanelLeftClose size={16} /></button>}
        </div>
      </div>
      {managing && <CategoryManager onClose={() => setManaging(false)} />}

      <button
        className={`mx-3 mt-3 flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm ${
          selected === null ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        onClick={() => selectCategory(null)}
      >
        <Files size={16} /> 全部笔记
      </button>
      <button
        className={`mx-3 mb-3 mt-1 flex items-center gap-2 rounded-lg px-3 py-2 text-left text-sm ${
          selected === UNCATEGORIZED_SENTINEL ? 'bg-indigo-50 text-indigo-700' : 'hover:bg-gray-100'
        }`}
        onClick={() => selectCategory(UNCATEGORIZED_SENTINEL)}
      >
        <Inbox size={16} /> 未分类
        <span className="count-badge ml-auto">{uncategorizedCount}</span>
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

      <div className="flex-1 overflow-y-auto px-2 pb-4">
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
