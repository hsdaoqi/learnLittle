import { zh } from './zh'
import { en } from './en'
import { useUiStore, type Locale } from '../stores/useUiStore'

const dictionaries = { zh, en } as const

export type MessageKey = keyof typeof zh

export function t(key: MessageKey, locale?: Locale): string {
  const lang = locale ?? useUiStore.getState().locale
  return dictionaries[lang][key] || dictionaries.zh[key] || key
}

export function useT() {
  const locale = useUiStore((s) => s.locale)
  return (key: MessageKey) => t(key, locale)
}
