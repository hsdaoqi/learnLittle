import { request } from './client'

export interface UsageSummary {
  days: number
  total_calls: number
  total_prompt_tokens: number
  total_completion_tokens: number
  total_tokens: number
  total_cost_cny: number
  avg_latency_ms: number
  by_stage: { stage: string | null; calls: number; prompt_tokens: number; completion_tokens: number }[]
  by_model: { model: string | null; calls: number; cost_cny: number }[]
}

export const usageApi = {
  summary(days = 30) {
    return request<UsageSummary>('/usage/summary', { params: { days } })
  },
}
