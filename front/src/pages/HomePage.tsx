import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi, type DeviceSession } from '../api/auth'
import { usageApi, type UsageSummary } from '../api/usage'
import { ApiError } from '../api/client'
import { getDeviceId } from '../api/device'
import { useT } from '../i18n'
import { useAuthStore } from '../stores/useAuthStore'
import { Activity, Camera, Check, ChevronDown, Info, LoaderCircle, LogOut, Mail, Monitor, Save, ShieldCheck, UserRound } from 'lucide-react'

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
  const [editingEmail, setEditingEmail] = useState(false)
  const [pending, setPending] = useState('')

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
    <div className="profile-page">
      <div className="profile-content">
      <h1 className="mb-6 text-xl font-bold">{t('profile.title')}</h1>

      {error && <div role="alert" className="profile-feedback is-error">{error}</div>}
      {hint && <div role="status" className="profile-feedback is-success"><Check size={16} />{hint}</div>}

      {!user && !error && <div className="text-sm text-gray-500">加载中…</div>}

      {user && (
        <>
          <section className="profile-primary" aria-label={t('profile.title')}>
            <div className="profile-identity">
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                className="profile-avatar"
                title={t('profile.uploadAvatar')}
                aria-label={t('profile.uploadAvatar')}
              >
                {user.avatar ? (
                  <img src={user.avatar} alt="" className="h-full w-full object-cover" />
                ) : (
                  <UserRound size={32} strokeWidth={1.5} />
                )}
                <span className={`profile-avatar-overlay ${uploading ? 'is-uploading' : ''}`}>
                  {uploading ? <LoaderCircle size={22} className="animate-spin" /> : <Camera size={22} />}
                </span>
                <span className="profile-avatar-camera"><Camera size={12} /></span>
              </button>
              <div className="profile-identity-text">
                <h2>{user.username}</h2>
                <p>{t('profile.createdAt')} {new Date(user.created_at).toLocaleDateString()}</p>
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

            <div className="profile-email">
              <p className="profile-label">{t('profile.email')}</p>
              <div className="profile-email-value">
                <Mail size={15} />
                <span className="profile-email-address">{user.email || t('profile.unbound')}</span>
                {user.email && <span className={`profile-verification ${user.email_verified ? 'is-verified' : ''}`}>
                  {user.email_verified ? <Check size={12} /> : null}
                  {user.email_verified ? t('profile.verified') : t('profile.unverified')}
                </span>}
                <button
                  type="button"
                  className="profile-text-button"
                  aria-expanded={editingEmail}
                  aria-controls="profile-email-editor"
                  onClick={() => setEditingEmail((value) => !value)}
                >
                  {editingEmail ? t('profile.cancel') : t('profile.bindEmail')}
                </button>
              </div>
              {editingEmail && <div className="profile-email-editor" id="profile-email-editor">
              <label className="sr-only" htmlFor="profile-new-email">{t('profile.newEmail')}</label>
              <div className="profile-field-row">
              <input
                id="profile-new-email"
                type="email"
                autoComplete="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t('profile.newEmail')}
                className="profile-field"
              />
                <button
                  type="button"
                  className="primary-button"
                  disabled={pending !== '' || !email.trim()}
                  onClick={async () => {
                    setError('')
                    setHint('')
                    setPending('code')
                    try {
                      await authApi.sendCode(email)
                      setHint('验证码已发送')
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '发送失败')
                    } finally {
                      setPending('')
                    }
                  }}
                >
                  {t('profile.send')}
                </button>
              </div>
              <label className="sr-only" htmlFor="profile-email-code">{t('profile.code')}</label>
              <div className="profile-field-row">
                <input
                  id="profile-email-code"
                  inputMode="numeric"
                  autoComplete="one-time-code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder={t('profile.code')}
                  maxLength={6}
                  className="profile-field"
                />
                <button
                  type="button"
                  className="primary-button"
                  disabled={pending !== '' || !email.trim() || code.length !== 6}
                  onClick={async () => {
                    setError('')
                    setHint('')
                    setPending('email')
                    try {
                      await authApi.changeEmail(email, code)
                      await reloadMe()
                      setHint('邮箱已更新')
                      setCode('')
                      setEmail('')
                      setEditingEmail(false)
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '绑定失败')
                    } finally {
                      setPending('')
                    }
                  }}
                >
                  {t('profile.confirm')}
                </button>
              </div>
              </div>}
            </div>
            <div className="profile-bio">
              <label htmlFor="profile-bio">{t('profile.bio')}</label>
              <textarea
                id="profile-bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                maxLength={500}
                rows={3}
                placeholder={t('profile.bioPlaceholder')}
                className="profile-field profile-bio-field"
              />
              <button
                type="button"
                className="primary-button profile-save"
                disabled={pending !== ''}
                onClick={async () => {
                  setError('')
                  setHint('')
                  setPending('bio')
                  try {
                    await authApi.updateMe({ bio })
                    await reloadMe()
                    setHint('简介已保存')
                  } catch (err) {
                    setError(err instanceof ApiError ? err.message : '保存失败')
                  } finally {
                    setPending('')
                  }
                }}
              >
                {pending === 'bio' ? <LoaderCircle size={16} className="animate-spin" /> : <Save size={16} />}
                {t('profile.saveBio')}
              </button>
            </div>
          </section>

          <div className="profile-secondary">
            <details className="profile-disclosure">
              <summary><ShieldCheck size={17} /><span>{t('profile.changePassword')}</span><ChevronDown size={16} /></summary>
              <div className="profile-disclosure-body">
              <p className="mb-3 text-xs text-[var(--color-text-secondary)]">{t('profile.passwordHint')}</p>
              <div className="space-y-2">
                <input
                  type="password"
                  aria-label={t('profile.oldPassword')}
                  autoComplete="current-password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  placeholder={t('profile.oldPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <input
                  type="password"
                  aria-label={t('profile.newPassword')}
                  autoComplete="new-password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder={t('profile.newPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <input
                  type="password"
                  aria-label={t('profile.confirmPassword')}
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t('profile.confirmPassword')}
                  className="w-full rounded-md border px-3 py-1.5 text-sm"
                />
                <button
                  type="button"
                  className="primary-button"
                  disabled={pending !== ''}
                  onClick={async () => {
                    setError('')
                    setHint('')
                    if (newPassword !== confirmPassword) {
                      setError('两次输入的密码不一致')
                      return
                    }
                    setPending('password')
                    try {
                      await authApi.changePassword(oldPassword, newPassword)
                      setOldPassword('')
                      setNewPassword('')
                      setConfirmPassword('')
                      setHint('密码已修改，其他设备需要重新登录')
                    } catch (err) {
                      setError(err instanceof ApiError ? err.message : '修改失败')
                    } finally {
                      setPending('')
                    }
                  }}
                >
                  {t('profile.submitPassword')}
                </button>
              </div>
              </div>
            </details>

            <details className="profile-disclosure">
              <summary><Activity size={17} /><span>{t('profile.usage')}</span><ChevronDown size={16} /></summary>
              <div className="profile-disclosure-body">
              {!usage || usage.total_calls === 0 ? (
                <p className="text-sm text-[var(--color-text-secondary)]">{t('profile.usageEmpty')}</p>
              ) : (
                <dl className="profile-usage">
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
              </div>
            </details>

            <details className="profile-disclosure">
              <summary><Monitor size={17} /><span>{t('profile.devices')}</span><small>{sessions.length}</small><ChevronDown size={16} /></summary>
              <div className="profile-disclosure-body">
              {sessions.length === 0 && (
                <p className="text-sm text-[var(--color-text-secondary)]">{t('profile.noDevices')}</p>
              )}
              <ul className="space-y-3">
                {sessions.map((session) => (
                  <li
                    key={session.device_id}
                    className="profile-device"
                  >
                    <div className="min-w-0">
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
                      className="profile-text-button is-danger"
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
              </div>
            </details>

            <details className="profile-disclosure">
              <summary><Info size={17} /><span>{t('profile.accountInfo')}</span><ChevronDown size={16} /></summary>
              <dl className="profile-account-info profile-disclosure-body">
                <div><dt>{t('profile.status')}</dt><dd>{user.status}</dd></div>
                <div><dt>{t('profile.userId')}</dt><dd className="font-mono">{user.uuid}</dd></div>
                <div><dt>{t('profile.createdAt')}</dt><dd>{new Date(user.created_at).toLocaleString()}</dd></div>
              </dl>
            </details>

            <button
              type="button"
              className="profile-logout"
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
              <LogOut size={15} />
              {t('profile.logout')}
            </button>
          </div>
        </>
      )}
      </div>
    </div>
  )
}
