// 统一 API 客户端：同源代理 /api，错误按公共设计约定的 {error:{code,message,field}} 解析。
export class ApiError extends Error {
  code: string
  field?: string
  status: number

  constructor(status: number, code: string, message: string, field?: string) {
    super(message)
    this.status = status
    this.code = code
    this.field = field
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  let body = init.body
  if (body !== undefined && !(body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const response = await fetch(path, { ...init, headers, credentials: 'same-origin' })
  if (response.status === 204) {
    return undefined as T
  }
  const text = await response.text()
  const data = text ? JSON.parse(text) : null
  if (!response.ok) {
    const error = data?.error ?? {}
    throw new ApiError(response.status, error.code ?? 'INTERNAL_ERROR', error.message ?? '请求失败', error.field)
  }
  return data as T
}

export interface Account {
  id: number
  username: string
  email: string
  role: 'member' | 'admin'
}

export interface Category {
  id: number
  name: string
}

export interface Album {
  id: number
  name: string
  visibility: 'public' | 'private'
  version: number
  owner_id: number
  category: Category
  created_at: string
  updated_at: string
}

export interface UserSummary {
  id: number
  username: string
}

export interface Photo {
  id: number
  album_id: number
  uploader: UserSummary
  created_at: string
  thumbnail_url: string
}

export interface Comment {
  id: number
  photo_id: number
  author: UserSummary
  body: string
  created_at: string
}

export interface PhotoDetail {
  photo: Photo
  original_url: string
  comments: Comment[]
  like: { liked: boolean; like_count: number }
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'POST', body: data === undefined ? undefined : JSON.stringify(data) }),
  put: <T>(path: string, data: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(data) }),
  upload: <T>(path: string, formData: FormData) =>
    request<T>(path, { method: 'POST', body: formData }),
}
