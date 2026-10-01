import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { reviewApi, type ReviewItem, type ReviewStats } from '../api/review'
import { ApiError } from '../api/client'
import { useT } from '../i18n'

const qualities = [
  { value: 1, labelKey: 'review.q1' as const },
  { value: 2, labelKey: 'review.q2' as const },
  { value: 3, labelKey: 'review.q3' as const },
  { value: 4, labelKey: 'review.q4' as const },
  { value: 5, labelKey: 'review.q5' as const },
]

export default function DailyReviewPage() {
  const t = useT()
  const navigate = useNavigate()
  const [reviews, setReviews] = useState<ReviewItem[]>([])
  const [stats, setStats] = useState<ReviewStats | null>(null)
  const [index, setIndex] = useState(0)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function load() {
    try {
      const [today, numbers] = await Promise.all([reviewApi.today(), reviewApi.stats()])
      setReviews(today.reviews)
      setStats(numbers)
      setIndex(0)
      setError('')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('review.loadFailed'))
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const current = reviews[index]

  async function handleComplete(quality: number) {
    if (!current) return
    setBusy(true)
    try {
      await reviewApi.complete(current.review_id, quality)
      setReviews((prev) => prev.filter((item) => item.review_id !== current.review_id))
      setStats((prev) =>
        prev
          ? {
              ...prev,
              completed_today: prev.completed_today + 1,
              pending_today: Math.max(0, prev.pending_today - 1),
              total_reviews: prev.total_reviews + 1,
              streak_days: Math.max(prev.streak_days, 1),
            }
          : prev,
      )
      setIndex(0)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('review.completeFailed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="review-page flex h-full min-h-0">
      <aside className="w-64 shrink-0 overflow-y-auto border-r border-[var(--color-border)] p-3">
        <h1 className="mb-1 text-sm font-semibold">{t('review.title')}</h1>
        <p className="mb-3 text-xs text-[var(--color-text-secondary)]">
          {t('review.pending')}: {stats?.pending_today ?? reviews.length} · {t('review.streak')}:{' '}
          {stats?.streak_days ?? 0}
        </p>
        {reviews.length === 0 ? (
          <p className="text-xs text-[var(--color-text-secondary)]">{t('review.empty')}</p>
        ) : (
          <ul className="space-y-1">
            {reviews.map((item, i) => (
              <li key={item.review_id}>
                <button
                  type="button"
                  onClick={() => setIndex(i)}
                  className={`w-full rounded-md px-2 py-1.5 text-left text-sm ${
                    i === index
                      ? 'bg-[var(--color-accent)] text-[var(--color-on-accent)]'
                      : 'hover:bg-[var(--color-accent-bg)]'
                  }`}
                >
                  {item.note_title}
                </button>
              </li>
            ))}
          </ul>
        )}
      </aside>
      <section className="min-w-0 flex-1 overflow-y-auto p-6">
        {error && <p className="mb-3 text-sm text-red-500">{error}</p>}
        {stats && (
          <div className="mb-4 flex flex-wrap gap-3 text-xs text-[var(--color-text-secondary)]">
            <span>
              {t('review.completedToday')}: {stats.completed_today}
            </span>
            <span>
              {t('review.total')}: {stats.total_reviews}
            </span>
          </div>
        )}
        {!current ? (
          <p className="text-sm text-[var(--color-text-secondary)]">{t('review.allDone')}</p>
        ) : (
          <div>
            <h2 className="mb-2 text-lg font-semibold">{current.note_title}</h2>
            <p className="mb-4 text-xs text-[var(--color-text-secondary)]">
              {t('review.round')} {current.review_count + 1} · {t('review.interval')}{' '}
              {current.interval_days}
              {t('review.days')}
            </p>
            <pre className="mb-6 whitespace-pre-wrap rounded-lg border border-[var(--color-border)] bg-[var(--color-sidebar-bg)] p-4 text-sm">
              {current.note_content}
            </pre>
            <div className="mb-4 flex flex-wrap gap-2">
              {qualities.map((item) => (
                <button
                  key={item.value}
                  type="button"
                  disabled={busy}
                  onClick={() => void handleComplete(item.value)}
                  className="rounded-md border border-[var(--color-border)] px-3 py-1.5 text-sm hover:bg-[var(--color-accent-bg)] disabled:opacity-50"
                >
                  {t(item.labelKey)}
                </button>
              ))}
            </div>
            <button
              type="button"
              className="text-xs text-[var(--color-text-secondary)] underline"
              onClick={() => navigate(`/notes/${current.note_id}`)}
            >
              {t('review.openNote')}
            </button>
          </div>
        )}
      </section>
    </div>
  )
}
