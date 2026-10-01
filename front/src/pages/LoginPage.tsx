import { GeometricBackground, IllustrationScene } from '../components/IllustrationScene'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { ApiError } from '../api/client'
import { useT } from '../i18n'
import { useAuthStore } from '../stores/useAuthStore'

export default function LoginPage() {
  const t = useT()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const tokens = await authApi.login({ username, password })
      useAuthStore.getState().setTokens(tokens.access_token, tokens.refresh_token)
      useAuthStore.getState().setUser(await authApi.me())
      navigate('/', { replace: true })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '登录失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-decoration" aria-hidden="true"><GeometricBackground /></div>
      <div className="auth-illustration" aria-hidden="true"><IllustrationScene /></div>
      <div className="auth-form-area">
      <div className="auth-card">
        <div className="auth-brand"><span>云</span>{t('app.name')}</div>
        <h1 className="mb-1 text-2xl font-bold">{t('auth.login')}</h1>
        <p className="mb-6 text-sm text-[var(--color-text-secondary)]">{t('auth.loginHint')}</p>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="login-username" className="mb-1 block text-sm font-medium">{t('auth.username')}</label>
            <input
              id="login-username"
              autoComplete="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder={t('auth.usernamePlaceholder')}
            />
          </div>
          <div>
            <label htmlFor="login-password" className="mb-1 block text-sm font-medium">{t('auth.password')}</label>
            <input
              id="login-password"
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder=""
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? t('auth.loggingIn') : t('auth.login')}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          {t('auth.noAccount')}
          <Link to="/register" className="text-[var(--color-accent)] hover:underline">
            {t('auth.register')}
          </Link>
        </p>
      </div>
      </div>
    </div>
  )
}
