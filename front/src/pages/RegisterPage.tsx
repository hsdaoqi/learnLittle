import { GeometricBackground, IllustrationScene } from '../components/IllustrationScene'
import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authApi } from '../api/auth'
import { ApiError } from '../api/client'
import { useT } from '../i18n'

export default function RegisterPage() {
  const t = useT()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authApi.register({
        username,
        password,
        email: email || undefined,
        verification_code: email ? code : undefined,
      })
      // 注册成功后跳登录页，由用户主动登录
      navigate('/login', { replace: true, state: { registered: username } })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : '注册失败，请稍后重试')
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
        <h1 className="mb-1 text-2xl font-bold">{t('auth.register')}</h1>
        <p className="mb-6 text-sm text-[var(--color-text-secondary)]">{t('auth.registerHint')}</p>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">{t('auth.username')}</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              maxLength={50}
              pattern="[A-Za-z0-9_]+"
              title="只能包含字母、数字和下划线"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder="字母 / 数字 / 下划线"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">{t('auth.password')}</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder="至少 8 位，须包含字母和数字"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">
              {t('auth.email')}
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              placeholder="可选；填写则需验证码"
            />
          </div>
          {email && (
            <div>
              <label className="mb-1 block text-sm font-medium">验证码</label>
              <div className="flex gap-2">
                <input
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  maxLength={6}
                  className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm outline-none"
                  placeholder="6 位数字"
                />
                <button
                  type="button"
                  disabled={sending}
                  className="rounded-md border border-gray-300 px-3 py-2 text-sm"
                  onClick={async () => {
                    setSending(true)
                    setError('')
                    try {
                      await authApi.sendCode(email)
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '发送失败')
                    } finally {
                      setSending(false)
                    }
                  }}
                >
                  {sending ? '发送中' : '发送验证码'}
                </button>
              </div>
            </div>
          )}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-indigo-600 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? t('auth.registering') : t('auth.register')}
          </button>
        </form>

        <p className="mt-4 text-center text-sm text-gray-500">
          {t('auth.hasAccount')}
          <Link to="/login" className="text-[var(--color-accent)] hover:underline">
            {t('auth.login')}
          </Link>
        </p>
      </div>
      </div>
    </div>
  )
}
