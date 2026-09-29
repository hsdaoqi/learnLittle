import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi, type DeviceSession } from '../api/auth'
import { usageApi, type UsageSummary } from '../api/usage'
import { ApiError } from '../api/client'
import { getDeviceId } from '../api/device'
import { useT } from '../i18n'
import { useAuthStore } from '../stores/useAuthStore'

export default function HomePage() {
  const t = useT()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const clear = useAuthStore((s) => s.clear)
  const fileRef = useRef<HTMLInputElement>(null)

  const [error, setError] = useState('')
  const [hint, setHint] = useState('')
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [bio, setBio] = useState('')
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [sessions, setSessions] = useState<DeviceSession[]>([])
  const [usage, setUsage] = useState<UsageSummary | null>(null)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    let cancelled = false
    authApi
      .me()
      .then((me) => {
        if (cancelled) return
        setError('')
        setUser(me)
        setBio(me.bio || '')
      })
      .catch((err) => {
        if (cancelled) return
        setError(err instanceof ApiError ? err.message : '加载失败')
      })
    authApi
      .listSessions()
      .then((data) => {
        if (cancelled) return
        setSessions(data.sessions || [])
      })
      .catch(() => {
        if (cancelled) return
        setSessions([])
      })
    usageApi
      .summary()
      .then((data) => {
        if (cancelled) return
        setUsage(data)
      })
      .catch(() => {
        if (cancelled) return
        setUsage(null)
      })
    return () => {
      cancelled = true
    }
  }, [setUser])

  async function reloadMe() {
    const me = await authApi.me()
    setUser(me)
    setBio(me.bio || '')
  }

  async function reloadSessions() {
    const data = await authApi.listSessions()
    setSessions(data.sessions)
  }

  return (
    <div className="h-full overflow-auto p-6">
      <h1 className="mb-6 text-xl font-bold">{t('profile.title')}</h1>

      {error && <div className="mb-4 rounded-md bg-red-50 px-3 py-2 text-sm text-red-600">{error}</div>}
      {hint && <div className="mb-4 rounded-md bg-green-50 px-3 py-2 text-sm text-green-700">{hint}</div>}

      {!user && !error && <div className="text-sm text-gray-500">加载中…</div>}

      {user && (
        <div className="grid max-w-4xl gap-6 lg:grid-cols-2">
          <section className="rounded-xl bg-[var(--color-surface)] p-6 shadow-card">
            <div className="mb-4 flex items-center gap-4">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                className="relative h-16 w-16 overflow-hidden rounded-full bg-[var(--color-accent-bg)] text-lg font-semibold text-[var(--color-accent)]"
                title={t('profile.uploadAvatar')}
              >
                {user.avatar ? (
                  <img src={user.avatar} alt="" className="h-full w-full object-cover" />
                ) : (
                  user.username.slice(0, 1).toUpperCase()
                )}
              </button>
              <div>
                <p className="font-medium">{user.username}</p>
                <p className="text-xs text-[var(--color-text-secondary)]">{t('profile.avatarHint')}</p>
                <button
                  type="button"
                  className="mt-1 text-xs text-[var(--color-accent)]"
                  onClick={() => fileRef.current?.click()}
                  disabled={uploading}
                >
                  {t('profile.uploadAvatar')}
                </button>
              </div>
              <input
                ref={fileRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                className="hidden"
                onChange={async (event) => {
                  const file = event.target.files?.[0]
                  event.target.value = ''
                  if (!file) return
                  setError('')
                  setHint('')
                  setUploading(true)
                  try {
                    await authApi.uploadAvatar(file)
                    await reloadMe()
                    setHint('头像已更新')
                  } catch (err) {
                    setError(err instanceof ApiError ? err.message : '上传失败')
                  } finally {
                    setUploading(false)
                  }
                }}
              />
            </div>

            <dl className="space-y-3 text-sm">
              <div className="flex">
                <dt className="w-24 shrink-0 text-[var(--color-text-secondary)]">{t('profile.username')}</dt>
                <dd className="font-medium">{user.username}</dd>
              </div>
              <div className="flex">
                <dt className="w-24 shrink-0 text-[var(--color-text-secondary)]">{t('profile.email')}</dt>
                <dd>
                  {user.email ?? t('profile.unbound')}
                  {user.email_verified ? t('profile.verified') : ''}
                </dd>
              </div>
              <div className="flex">
                <dt className="w-24 shrink-0 text-[var(--color-text-secondary)]">{t('profile.status')}</dt>
                <dd>{user.status}</dd>
              </div>
              <div className="flex">
                <dt className="w-24 shrink-0 text-[var(--color-text-secondary)]">{t('profile.userId')}</dt>
                <dd className="break-all font-mono text-xs">{user.uuid}</dd>
              </div>
              <div className="flex">
                <dt className="w-24 shrink-0 text-[var(--color-text-secondary)]">{t('profile.createdAt')}</dt>
                <dd>{new Date(user.created_at).toLocaleString()}</dd>
              </div>
            </dl>

            <div className="mt-4 space-y-2 border-t border-[var(--color-border)] pt-4">
              <p className="text-sm font-medium">{t('profile.bio')}</p>
              <textarea
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                maxLength={500}
                rows={3}
                placeholder={t('profile.bioPlaceholder')}
                className="w-full rounded-md border px-3 py-1.5 text-sm"
              />
              <button
                type="button"
                className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white"
                onClick={async () => {
                  setError('')
                  setHint('')
                  try {
                    await authApi.updateMe({ bio })
                    await reloadMe()
                    setHint('简介已保存')
                  } catch (err) {
                    setError(err instanceof ApiError ? err.message : '保存失败')
                  }
                }}
              >
                {t('profile.saveBio')}
              </button>
            </div>

            <div className="mt-4 space-y-2 border-t border-[var(--color-border)] pt-4">
              <p className="text-sm font-medium">{t('profile.bindEmail')}</p>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('profile.newEmail')}
                className="w-full rounded-md border px-3 py-1.5 text-sm"
              />
              <div className="flex gap-2">
                <input
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder={t('profile.code')}
                  maxLength={6}
                  className="flex-1 rounded-md border px-3 py-1.5 text-sm"
                />
                <button
                  type="button"
                  className="rounded-md border px-3 py-1.5 text-sm"
                  onClick={async () => {
                    setError('')
                    setHint('')
                    try {
                      await authApi.sendCode(email)
                      setHint('验证码已发送')
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '发送失败')
                    }
                  }}
                >
                  {t('profile.send')}
                </button>
                <button
                  type="button"
                  className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white"
                  onClick={async () => {
                    setError('')
                    try {
                      await authApi.changeEmail(email, code)
                      await reloadMe()
                      setHint('邮箱已更新')
                      setCode('')
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '绑定失败')
                    }
                  }}
                >
                  {t('profile.confirm')}
                </button>
              </div>
            </div>
          </section>

          <div className="space-y-6">
            <section className="rounded-xl bg-[var(--color-surface)] p-6 shadow-card">
              <p className="mb-3 text-sm font-medium">{t('profile.changePassword')}</p>
              <p className="mb-3 text-xs text-[var(--color-text-secondary)]">{t('profile.passwordHint')}</p>
              <div className="space-y-2">
                <input
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  placeholder={t('profile.oldPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder={t('profile.newPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t('profile.confirmPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <button
                  type="button"
                  className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm text-white"
                  onClick={async () => {
                    setError('')
                    setHint('')
                    if (newPassword !== confirmPassword) {
                      setError('两次输入的密码不一致')
                      return
                    }
                    try {
                      await authApi.changePassword(oldPassword, newPassword)
                      setOldPassword('')
                      setNewPassword('')
                      setConfirmPassword('')
                      setHint('密码已修改，其他设备需要重新登录')
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '修改失败')
                    }
                  }}
                >
                  {t('profile.submitPassword')}
                </button>
              </div>
            </section>

            <section className="rounded-xl bg-[var(--color-surface)] p-6 shadow-card">
              <p className="mb-3 text-sm font-medium">{t('profile.usage')}</p>
              {!usage || usage.total_calls === 0 ? (
                <p className="text-sm text-[var(--color-text-secondary)]">{t('profile.usageEmpty')}</p>
              ) : (
                <dl className="grid grid-cols-3 gap-3 text-sm">
                  <div>
                    <dt className="text-xs text-[var(--color-text-secondary)]">{t('profile.usageCalls')}</dt>
                    <dd className="font-medium">{usage.total_calls}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-[var(--color-text-secondary)]">{t('profile.usageTokens')}</dt>
                    <dd className="font-medium">{usage.total_tokens}</dd>
                  </div>
                  <div>
                    <dt className="text-xs text-[var(--color-text-secondary)]">{t('profile.usageCost')}</dt>
                    <dd className="font-medium">¥{usage.total_cost_cny.toFixed(6)}</dd>
                  </div>
                </dl>
              )}
            </section>

            <section className="rounded-xl bg-[var(--color-surface)] p-6 shadow-card">
              <p className="mb-3 text-sm font-medium">{t('profile.devices')}</p>
              {sessions.length === 0 && (
                <p className="text-sm text-[var(--color-text-secondary)]">{t('profile.noDevices')}</p>
              )}
              <ul className="space-y-3">
                {sessions.map((session) => (
                  <li
                    key={session.device_id}
                    className="flex items-start justify-between gap-3 rounded-md border border-[var(--color-border)] px-3 py-2 text-sm"
                  >
                    <div>
                      <p className="font-medium">
                        {session.device_name || session.device_id}
                        {session.is_current || session.device_id === getDeviceId() ? (
                          <span className="ml-2 text-xs text-[var(--color-accent)]">
                            {t('profile.currentDevice')}
                          </span>
                        ) : null}
                      </p>
                      <p className="text-xs text-[var(--color-text-secondary)]">
                        {session.ip || '—'} · {session.last_used ? new Date(session.last_used).toLocaleString() : ''}
                      </p>
                    </div>
                    <button
                      type="button"
                      className="shrink-0 text-xs text-red-600"
                      onClick={async () => {
                        if (!window.confirm(t('profile.revokeConfirm'))) return
                        setError('')
                        const current = session.is_current || session.device_id === getDeviceId()
                        try {
                          await authApi.revokeSession(session.device_id)
                          if (current) {
                            clear()
                            navigate('/login', { replace: true })
                            return
                          }
                          await reloadSessions()
                          setHint('设备已撤销')
                        } catch (err) {
                          setError(err instanceof ApiError ? err.message : '撤销失败')
                        }
                      }}
                    >
                      {t('profile.revoke')}
                    </button>
                  </li>
                ))}
              </ul>
            </section>

            <button
              type="button"
              className="w-full rounded-xl border border-red-200 bg-white px-4 py-3 text-sm text-red-600 hover:bg-red-50"
              onClick={async () => {
                try {
                  await authApi.logout(useAuthStore.getState().refreshToken)
                } catch {
                  // ignore
                }
                clear()
                navigate('/login', { replace: true })
              }}
            >
              {t('profile.logout')}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
