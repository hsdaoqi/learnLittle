import { request } from './client'
import { getDeviceId, getDeviceName } from './device'
import type { UserInfo } from '../stores/useAuthStore'

export interface TokenPair {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  device_id?: string | null
}

export interface DeviceSession {
  device_id: string
  device_name?: string | null
  ip?: string | null
  created_at?: string | null
  last_used?: string | null
  is_current: boolean
}

export const authApi = {
  register(data: { username: string; password: string; email?: string; verification_code?: string }) {
    return request<{ user_id: string; username: string }>('/auth/register', {
      method: 'POST',
      data,
    })
  },

  sendCode(email: string) {
    return request<null>('/auth/send-code', { method: 'POST', data: { email } })
  },

  changeEmail(email: string, verification_code: string) {
    return request<null>('/user/change-email', {
      method: 'POST',
      data: { email, verification_code },
    })
  },

  login(data: { username: string; password: string }) {
    return request<TokenPair>('/auth/login', {
      method: 'POST',
      data: {
        ...data,
        device_id: getDeviceId(),
        device_name: getDeviceName(),
      },
    })
  },

  logout(refreshToken: string | null) {
    return request<{ refresh_tokens_revoked: number }>('/auth/logout', {
      method: 'POST',
      data: { refresh_token: refreshToken, device_id: getDeviceId() },
    })
  },

  me() {
    return request<UserInfo>('/user/me')
  },

  updateMe(data: { bio: string }) {
    return request<null>('/user/me', { method: 'PUT', data })
  },

  changePassword(oldPassword: string, newPassword: string) {
    return request<null>('/user/me/password', {
      method: 'POST',
      data: { old_password: oldPassword, new_password: newPassword },
    })
  },

  uploadAvatar(file: File) {
    const form = new FormData()
    form.append('file', file)
    return request<{ avatar_url: string; filename: string }>('/file/avatar', {
      method: 'POST',
      data: form,
    })
  },

  listSessions() {
    return request<{ sessions: DeviceSession[] }>('/auth/sessions')
  },

  revokeSession(deviceId: string) {
    return request<null>(`/auth/sessions/${encodeURIComponent(deviceId)}`, {
      method: 'DELETE',
    })
  },
}
