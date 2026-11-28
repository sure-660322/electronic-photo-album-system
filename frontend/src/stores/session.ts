// 会话状态：页面刷新时通过 GET /auth/me 恢复身份。
import { reactive } from 'vue'

import { api, type Account } from '@/api/client'

interface SessionState {
  user: Account | null
  loaded: boolean
}

const state = reactive<SessionState>({ user: null, loaded: false })
let loading: Promise<void> | null = null

export function useSession() {
  async function load(): Promise<void> {
    if (state.loaded) return
    if (!loading) {
      loading = (async () => {
        try {
          state.user = await api.get<Account>('/api/auth/me')
        } catch {
          state.user = null
        } finally {
          state.loaded = true
        }
      })()
    }
    await loading
  }

  async function login(username: string, password: string): Promise<Account> {
    const user = await api.post<Account>('/api/auth/login', { username, password })
    state.user = user
    state.loaded = true
    return user
  }

  async function register(payload: {
    username: string
    password: string
    password_confirmation: string
    email: string
  }): Promise<Account> {
    return api.post<Account>('/api/auth/register', payload)
  }

  async function logout(): Promise<void> {
    try {
      await api.post('/api/auth/logout')
    } finally {
      state.user = null
      state.loaded = true
    }
  }

  return { state, load, login, register, logout }
}
