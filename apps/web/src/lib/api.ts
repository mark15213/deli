const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

interface ErrorResponse {
  success: false
  error: {
    code: string
    message: string
    details?: any
  }
}

class ApiClient {
  private getHeaders(): HeadersInit {
    const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
    return {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    }
  }

  async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: { ...this.getHeaders(), ...options?.headers }
    })

    const data = await response.json()

    if (!response.ok || !data.success) {
      const error = data as ErrorResponse
      throw new Error(error.error?.message || 'Request failed')
    }

    return (data as ApiResponse<T>).data
  }

  // Auth
  async register(email: string, password: string, username?: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username })
    })
  }

  async login(email: string, password: string) {
    const data = await this.request<{ access_token: string; refresh_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    })

    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
    }

    return data
  }

  async getMe() {
    return this.request('/auth/me')
  }

  // Subscriptions
  async getSubscriptions() {
    return this.request('/subscriptions')
  }

  async createSubscription(data: { title: string; url: string; frequency: string }) {
    return this.request('/subscriptions', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateSubscription(id: string, data: any) {
    return this.request(`/subscriptions/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async deleteSubscription(id: string) {
    return this.request(`/subscriptions/${id}`, {
      method: 'DELETE'
    })
  }

  // Snapshots
  async getSnapshots(params?: { page?: number; limit?: number; status?: string }) {
    const query = new URLSearchParams(params as any).toString()
    return this.request(`/snapshots${query ? `?${query}` : ''}`)
  }

  async createSnapshot(data: any) {
    return this.request('/snapshots', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async getSnapshot(id: string) {
    return this.request(`/snapshots/${id}`)
  }

  async updateSnapshot(id: string, data: any) {
    return this.request(`/snapshots/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async deleteSnapshot(id: string) {
    return this.request(`/snapshots/${id}`, {
      method: 'DELETE'
    })
  }

  // Knowledge Bases
  async getKnowledgeBases() {
    return this.request('/knowledge-bases')
  }

  async createKnowledgeBase(data: any) {
    return this.request('/knowledge-bases', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateKnowledgeBase(id: string, data: any) {
    return this.request(`/knowledge-bases/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async deleteKnowledgeBase(id: string) {
    return this.request(`/knowledge-bases/${id}`, {
      method: 'DELETE'
    })
  }

  // Cards
  async getCards(knowledgeBaseId?: string) {
    const query = knowledgeBaseId ? `?knowledge_base_id=${knowledgeBaseId}` : ''
    return this.request(`/cards${query}`)
  }

  async createCard(data: any) {
    return this.request('/cards', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateCard(id: string, data: any) {
    return this.request(`/cards/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    })
  }

  async deleteCard(id: string) {
    return this.request(`/cards/${id}`, {
      method: 'DELETE'
    })
  }

  async submitCardReview(id: string, isCorrect: boolean) {
    return this.request(`/cards/${id}/review`, {
      method: 'POST',
      body: JSON.stringify({ is_correct: isCorrect })
    })
  }

  // Gulp
  async getGulpStream() {
    return this.request('/gulp/stream')
  }

  async getQuizCards() {
    return this.request('/gulp/quiz')
  }

  async submitQuiz(id: string, isCorrect: boolean) {
    return this.request(`/gulp/quiz/${id}/submit`, {
      method: 'POST',
      body: JSON.stringify({ is_correct: isCorrect })
    })
  }
}

export const api = new ApiClient()
