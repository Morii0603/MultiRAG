import { defineStore } from 'pinia'
import { ref } from 'vue'
import { chatApi } from '@/api/chat'
import type { ChatMessage } from '@/types'

function genSessionId() {
  return Array.from({ length: 32 }, () => Math.floor(Math.random() * 16).toString(16)).join('')
}

export const useChatStore = defineStore('chat', () => {
  const sessionId = ref(genSessionId())
  const messages = ref<ChatMessage[]>([])
  const sending = ref(false)

  function resetSession() {
    sessionId.value = genSessionId()
    messages.value = []
  }

  async function send(text: string, knowledgeBaseId?: number | null) {
    messages.value.push({ role: 'user', content: text })
    sending.value = true

    try {
      const res = await chatApi.send({
        message: text,
        session_id: sessionId.value,
        knowledge_base_id: knowledgeBaseId ?? null,
      })
      messages.value.push({ role: 'assistant', content: res.data.reply })
    } catch {
      messages.value.push({ role: 'assistant', content: '请求失败，请重试。' })
    } finally {
      sending.value = false
    }
  }

  return { sessionId, messages, sending, resetSession, send }
})
