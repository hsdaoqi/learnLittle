import { useState } from 'react'
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react'

interface SidebarItem {
  id: string
  title: string
  meta?: string
}

export default function SectionSidebar({
  title, items, onSelect,
}: { title: string; items: SidebarItem[]; onSelect: (id: string) => void }) {
  const [collapsed, setCollapsed] = useState(false)
  return (
    <aside className={`section-sidebar ${collapsed ? 'is-collapsed' : ''}`}>
      {collapsed ? (
        <button className="collapsed-strip" title={`展开${title}`} aria-label={`展开${title}`} onClick={() => setCollapsed(false)}>
          <ChevronRight size={16} /><FileText size={16} /><span>{title}</span>
        </button>
      ) : (
        <>
          <div className="section-sidebar-heading"><h2>{title}</h2><button className="icon-button" title={`收起${title}`} onClick={() => setCollapsed(true)}><ChevronLeft size={17} /></button></div>
          <div className="section-sidebar-list">
            {items.length === 0 ? <div className="empty-state"><FileText size={32} /><p>暂无内容</p></div> : items.map((item) => (
              <button key={item.id} className="section-sidebar-row" onClick={() => onSelect(item.id)}>
                <FileText size={16} /><span><strong>{item.title}</strong><small>{item.meta}</small></span>
              </button>
            ))}
          </div>
        </>
      )}
    </aside>
  )
}
