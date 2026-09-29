import { useEffect } from 'react'
import { Navigate } from 'react-router-dom'
import { useUiStore } from '../stores/useUiStore'

/** 旧 /chat 路由收回笔记页；问答只走右侧浮层。 */
export default function ChatPage() {
  const openAssistant = useUiStore((s) => s.openAssistant)
  useEffect(() => {
    openAssistant()
  }, [openAssistant])
  return <Navigate to="/" replace />
}
