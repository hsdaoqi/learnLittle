import type { ReactNode } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './layouts/MainLayout'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import NoteListPage from './pages/NoteListPage'
import ChatPage from './pages/ChatPage'
import KnowledgeBasePage from './pages/KnowledgeBasePage'
import RecycleBinPage from './pages/RecycleBinPage'
import NoteTemplatesPage from './pages/NoteTemplatesPage'
import DailyReviewPage from './pages/DailyReviewPage'
import RegisterPage from './pages/RegisterPage'
import { useAuthStore } from './stores/useAuthStore'

function RequireAuth({ children }: { children: ReactNode }) {
  const accessToken = useAuthStore((s) => s.accessToken)
  if (!accessToken) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <MainLayout />
          </RequireAuth>
        }
      >
        <Route element={<NoteListPage />}>
          <Route index element={null} />
          <Route path="notes/:noteId" element={null} />
        </Route>
        <Route path="recycle-bin" element={<RecycleBinPage />} />
        <Route path="templates" element={<NoteTemplatesPage />} />
        <Route path="review" element={<DailyReviewPage />} />
        <Route path="knowledge" element={<KnowledgeBasePage />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="profile" element={<HomePage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
