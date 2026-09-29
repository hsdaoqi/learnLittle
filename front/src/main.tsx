import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { applyTheme, useUiStore } from './stores/useUiStore'
import './index.css'

function applyUi(state: { theme: 'light' | 'dark'; locale: 'zh' | 'en' }) {
  applyTheme(state.theme)
  document.documentElement.lang = state.locale === 'zh' ? 'zh-CN' : 'en'
}

applyUi(useUiStore.getState())
useUiStore.persist.onFinishHydration(() => applyUi(useUiStore.getState()))

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
)
