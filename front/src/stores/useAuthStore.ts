import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserInfo {
  uuid: string
  username: string
  email: string | null
  email_verified?: boolean
  avatar: string | null
  bio: string | null
  status: string
  created_at: string
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: UserInfo | null
  setTokens: (accessToken: string, refreshToken: string) => void
  setUser: (user: UserInfo) => void
  clear: () => void
}

/**
 * 认证状态：token 与当前用户信息持久化到 localStorage。
 * api/client.ts 会读写这里的 token，实现请求自动携带与静默续期。
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      setUser: (user) => set({ user }),
      clear: () => set({ accessToken: null, refreshToken: null, user: null }),
    }),
    { name: 'learnlittle-auth' },
  ),
)
