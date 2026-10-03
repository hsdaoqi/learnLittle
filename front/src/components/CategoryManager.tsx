import { useEffect, useRef, useState } from 'react'
import { ArrowDown, ArrowUp, X } from 'lucide-react'
import { categoryApi } from '../api/category'
import { ApiError } from '../api/client'
import { useCategoryStore } from '../stores/useCategoryStore'
import type { Category } from '../types/notes'

function flatten(nodes: Category[], prefix = ''): (Category & { label: string })[] {
  return nodes.flatMap((node) => [
    { ...node, label: prefix + node.name },
    ...flatten(node.children, `${prefix}${node.name} / `),
  ])
}

export default function CategoryManager({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  const categories = useCategoryStore((s) => s.categories)
  const refresh = useCategoryStore((s) => s.fetchCategories)
  const select = useCategoryStore((s) => s.selectCategory)
  const [ids, setIds] = useState<string[]>([])
  const [operation, setOperation] = useState<'move' | 'merge' | 'delete'>('move')
  const [target, setTarget] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const items = flatten(categories)

  useEffect(() => { dialog.current?.showModal() }, [])

  async function reorder(item: Category, direction: number) {
    const siblings = items.filter((node) => node.parent_id === item.parent_id)
    const index = siblings.findIndex((node) => node.id === item.id)
    const next = index + direction
    if (next < 0 || next >= siblings.length) return
    const ordered = siblings.map((node) => node.id)
    ;[ordered[index], ordered[next]] = [ordered[next], ordered[index]]
    setBusy(true)
    setError('')
    try {
      await categoryApi.reorder(item.parent_id, ordered)
      await refresh()
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '排序失败')
    } finally { setBusy(false) }
  }

  async function apply() {
    if (!ids.length || (operation === 'move' && ids.length !== 1)) return
    if (operation === 'delete' && !window.confirm(`删除所选 ${ids.length} 个分类？`)) return
    setBusy(true)
    setError('')
    try {
      if (operation === 'move') await categoryApi.move(ids[0], target || null)
      else await categoryApi.batch({
        category_ids: ids, operation, merge_target_id: operation === 'merge' ? target : undefined,
      })
      await refresh()
      select(operation === 'merge' ? target : null)
      setIds([])
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '分类操作失败')
      await refresh()
    } finally { setBusy(false) }
  }

  return (
    <dialog ref={dialog} onClose={onClose} onCancel={onClose}
      className="m-auto w-[560px] max-w-[calc(100vw-32px)] rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-0 text-[var(--color-text)] backdrop:bg-black/30">
      <header className="flex items-center justify-between border-b border-[var(--color-border)] px-4 py-3">
        <h2 className="text-base font-semibold">分类管理</h2>
        <button className="icon-button" onClick={onClose} title="关闭" aria-label="关闭"><X size={17} /></button>
      </header>
      <div className="max-h-[50vh] overflow-y-auto p-3">
        {items.map((item) => {
          const siblings = items.filter((node) => node.parent_id === item.parent_id)
          return <div key={item.id} className="flex min-h-10 items-center gap-2 border-b border-[var(--color-border)] px-2">
            <label className="flex min-w-0 flex-1 items-center gap-2 text-sm">
              <input type="checkbox" checked={ids.includes(item.id)} disabled={busy}
                onChange={(e) => setIds((old) => e.target.checked ? [...old, item.id] : old.filter((id) => id !== item.id))} />
              <span className="break-words">{item.label}</span>
            </label>
            <button className="icon-button" title="上移" aria-label={`上移 ${item.name}`}
              disabled={busy || siblings[0]?.id === item.id} onClick={() => void reorder(item, -1)}><ArrowUp size={15} /></button>
            <button className="icon-button" title="下移" aria-label={`下移 ${item.name}`}
              disabled={busy || siblings.at(-1)?.id === item.id} onClick={() => void reorder(item, 1)}><ArrowDown size={15} /></button>
          </div>
        })}
      </div>
      <footer className="flex flex-wrap items-center gap-2 border-t border-[var(--color-border)] p-4">
        <select aria-label="分类操作" value={operation} disabled={busy}
          onChange={(e) => { setOperation(e.target.value as typeof operation); setTarget('') }}
          className="rounded border border-[var(--color-border)] bg-transparent p-2 text-sm">
          <option value="move">移动分类</option><option value="merge">合并分类</option><option value="delete">删除分类</option>
        </select>
        {operation !== 'delete' && <select value={target} onChange={(e) => setTarget(e.target.value)} disabled={busy}
          aria-label="目标分类" className="min-w-0 flex-1 rounded border border-[var(--color-border)] bg-transparent p-2 text-sm">
          <option value="">{operation === 'move' ? '顶级分类' : '选择合并目标'}</option>
          {items.filter((item) => !ids.includes(item.id)).map((item) =>
            <option key={item.id} value={item.id}>{item.label}</option>)}
        </select>}
        <button onClick={() => void apply()}
          disabled={busy || !ids.length || (operation === 'move' && ids.length !== 1) || (operation === 'merge' && !target)}
          className="rounded bg-[var(--color-accent)] px-3 py-2 text-sm text-white disabled:opacity-40">
          {busy ? '处理中' : '确认'}
        </button>
        {error && <p role="alert" className="w-full text-sm text-red-600">{error}</p>}
      </footer>
    </dialog>
  )
}
