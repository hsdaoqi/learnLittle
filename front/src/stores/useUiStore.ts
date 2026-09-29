import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark'
export type Locale = 'zh' | 'en'

interface UiState {
  theme: Theme
  locale: Locale
  assistantVisible: boolean
  assistantMounted: boolean
  searchOpen: boolean
  setTheme: (theme: Theme) => void
  setLocale: (locale: Locale) => void
  toggleTheme: () => void
  toggleLocale: () => void
  openAssistant: () => void
  closeAssistant: () => void
  toggleAssistant: () => void
  openSearch: () => void
  closeSearch: () => void
}

export function applyTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme
}

export const useUiStore = create<UiState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      locale: 'zh',
      assistantVisible: false,
      assistantMounted: false,
      searchOpen: false,
      setTheme: (theme) => {
        applyTheme(theme)
        set({ theme })
      },
      setLocale: (locale) => {
        document.documentElement.lang = locale === 'zh' ? 'zh-CN' : 'en'
        set({ locale })
      },
      toggleTheme: () => get().setTheme(get().theme === 'light' ? 'dark' : 'light'),
      toggleLocale: () => get().setLocale(get().locale === 'zh' ? 'en' : 'zh'),
      openAssistant: () => set({ assistantVisible: true, assistantMounted: true }),
      closeAssistant: () => set({ assistantVisible: false }),
      toggleAssistant: () => {
        const visible = !get().assistantVisible
        set({ assistantVisible: visible, assistantMounted: visible || get().assistantMounted })
      },
      openSearch: () => set({ searchOpen: true }),
      closeSearch: () => set({ searchOpen: false }),
    }),
    {
      name: 'learnlittle-ui',
      partialize: (state) => ({ theme: state.theme, locale: state.locale }),
    },
  ),
)
