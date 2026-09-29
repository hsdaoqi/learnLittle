import { useEffect } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import CategoryTree from '../components/CategoryTree'
import AssistantDrawer from '../components/layout/AssistantDrawer'
import GlobalSearchModal from '../components/layout/GlobalSearchModal'
import IconRail from '../components/layout/IconRail'
import TopBar from '../components/layout/TopBar'
import { useUiStore } from '../stores/useUiStore'

export default function MainLayout() {
  const location = useLocation()
  const showCategoryTree =
    !location.pathname.startsWith('/knowledge') &&
    location.pathname !== '/profile' &&
    location.pathname !== '/review'
  const assistantVisible = useUiStore((s) => s.assistantVisible)
  const searchOpen = useUiStore((s) => s.searchOpen)

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        useUiStore.getState().openSearch()
        return
      }
      if (event.key === 'Escape') {
        if (useUiStore.getState().searchOpen) {
          useUiStore.getState().closeSearch()
          return
        }
        useUiStore.getState().closeAssistant()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-[var(--color-bg)] text-[var(--color-text)]">
      <TopBar />
      <div className="flex min-h-0 flex-1">
        <IconRail />
        {showCategoryTree && <CategoryTree />}
        <main className="min-w-0 flex-1 bg-[var(--color-bg)]">
          <Outlet />
        </main>
        <AssistantDrawer />
      </div>
      {searchOpen && <GlobalSearchModal />}
      {assistantVisible && (
        <button
          type="button"
          aria-label="close assistant"
          className="fixed inset-0 z-[80] bg-black/20 md:hidden"
          onClick={() => useUiStore.getState().closeAssistant()}
        />
      )}
    </div>
  )
}
