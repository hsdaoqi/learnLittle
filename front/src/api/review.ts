import { request } from './client'

export interface ReviewItem {
  review_id: number
  note_id: string
  note_title: string
  note_content: string
  review_count: number
  interval_days: number
  next_review_at: string
}

export interface ReviewStats {
  pending_today: number
  total_reviews: number
  completed_today: number
  streak_days: number
}

export const reviewApi = {
  today() {
    return request<{ reviews: ReviewItem[]; count: number }>('/review/today')
  },

  complete(reviewId: number, quality = 3) {
    return request<{
      review_id: number
      next_review_at: string
      interval_days: number
      review_count: number
    }>(`/review/${reviewId}/complete`, {
      method: 'POST',
      params: { quality },
    })
  },

  stats() {
    return request<ReviewStats>('/review/stats')
  },
}
