<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { formatReply } from '@/utils/format'

const props = defineProps<{ knowledgeBaseId?: number | null }>()
const store = useChatStore()
const input = ref('')
const chatBody = ref<HTMLElement>()

watch(
  () => store.messages.length,
  () => nextTick(() => chatBody.value?.scrollTo({ top: chatBody.value.scrollHeight, behavior: 'smooth' }))
)

async function send() {
  const text = input.value.trim()
  if (!text || store.sending) return
  input.value = ''
  await store.send(text, props.knowledgeBaseId)
}

async function handleKeyup(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    await send()
  }
}
</script>

<template>
  <div class="flex flex-col h-full bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
    <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between">
      <span class="text-sm font-medium text-gray-700">对话</span>
      <button
        @click="store.resetSession()"
        class="text-xs text-gray-400 hover:text-gray-600 transition-colors"
      >
        新会话
      </button>
    </div>

    <div ref="chatBody" class="flex-1 overflow-y-auto px-4 py-3 space-y-4">
      <div v-if="!store.messages.length" class="text-center text-gray-400 text-sm py-8">
        输入问题开始对话
      </div>

      <div
        v-for="(msg, i) in store.messages"
        :key="i"
        class="flex"
        :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
      >
        <div
          class="max-w-[85%] rounded-xl px-4 py-2.5 text-sm leading-relaxed"
          :class="msg.role === 'user'
            ? 'bg-primary text-white'
            : 'bg-gray-100 text-gray-800 prose prose-sm'"
        >
          <div v-if="msg.role === 'assistant'" v-html="formatReply(msg.content)" />
          <template v-else>{{ msg.content }}</template>
        </div>
      </div>

      <div v-if="store.sending" class="flex justify-start">
        <div class="bg-gray-100 rounded-xl px-4 py-2.5 text-sm text-gray-400">
          思考中<span class="animate-pulse">...</span>
        </div>
      </div>
    </div>

    <div class="px-3 py-3 border-t border-gray-100">
      <div class="flex gap-2">
        <input
          v-model="input"
          class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
          placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
          @keyup="handleKeyup"
        />
        <button
          @click="send"
          :disabled="!input.trim() || store.sending"
          class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover disabled:opacity-50 transition-colors"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>
