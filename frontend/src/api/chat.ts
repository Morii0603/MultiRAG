import api from './index'
import type { ChatRequest, ChatResponse } from '@/types'

export const chatApi = {
  send(data: ChatRequest) {
    return api.post<ChatResponse>('/chat', data)
  },
}
