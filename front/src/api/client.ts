import axios, { type AxiosRequestConfig } from 'axios'
import { getDeviceId } from './device'
import { useAuthStore } from '../stores/useAuthStore'

/** 后端统一失败响应的业务码，转成异常抛给调用方。 */
export class ApiError extends Error {
  code: number
  constructor(code: number, message: string) {
    super(message)
    this.code = code
  }
}

export const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

// 请求发出前自动带上 Access Token
http.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  config.headers['X-Device-Id'] = getDeviceId()
  return config
})

// 全局只允许一个刷新请求在途，避免并发 401 触发多次刷新
let refreshing: Promise<boolean> | null = null

async function tryRefresh(): Promise<boolean> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState()
  if (!refreshToken) return false

  refreshing ??= axios
    .post('/api/v1/auth/refresh', { refresh_token: refreshToken, device_id: getDeviceId() })
    .then((res) => {
      const data = res.data.data as { access_token: string; refresh_token: string }
      setTokens(data.access_token, data.refresh_token)
      return true
    })
    .catch(() => {
      // Refresh Token 也失效了：清空登录态，回登录页
      clear()
      window.location.href = '/login'
      return false
    })
    .finally(() => {
      refreshing = null
    })
  return refreshing
}

http.interceptors.response.use(
  (res) => res,
  async (error) => {
    const { response, config } = error
    if (!response) throw new ApiError(-1, '网络异常，请稍后重试')
    const body = response.data as { code?: number; message?: string }

    if (response.status === 401 && config && !config._retried) {
      if (body?.code === 40101) {
        // Access Token 过期：静默续期后重放原请求，用户无感知
        config._retried = true
        if (await tryRefresh()) return http(config)
      } else if (body?.code === 40102) {
        // Token 无效或已被撤销（登出/篡改）：直接回登录页
        useAuthStore.getState().clear()
        window.location.href = '/login'
      }
    }

    throw new ApiError(body?.code ?? -1, body?.message ?? '请求失败')
  },
)

/** 统一请求入口：解包 {code, message, data}，非 0 一律抛 ApiError。 */
export async function request<T>(path: string, options?: AxiosRequestConfig): Promise<T> {
  const res = await http.request<{ code: number; message: string; data: T }>({
    url: path,
    ...options,
  })
  if (res.data.code !== 0) {
    throw new ApiError(res.data.code, res.data.message)
  }
  return res.data.data
}
