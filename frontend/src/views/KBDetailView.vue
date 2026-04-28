<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useKnowledgeBaseStore } from '@/stores/knowledgeBase'
import type { KnowledgeBase } from '@/types'
import DocumentList from '@/components/DocumentList.vue'
import FileUpload from '@/components/FileUpload.vue'
import ChatPanel from '@/components/ChatPanel.vue'

const route = useRoute()
const router = useRouter()
const kbStore = useKnowledgeBaseStore()

const kb = ref<KnowledgeBase | null>(null)
const docsLoading = ref(false)
const kbId = computed(() => Number(route.params.id))

onMounted(async () => {
  await kbStore.fetchList()
  kb.value = kbStore.list.find((k) => k.id === kbId.value) ?? null
  await loadDocuments()
})

async function loadDocuments() {
  docsLoading.value = true
  try {
    await kbStore.fetchDocuments(kbId.value)
  } finally {
    docsLoading.value = false
  }
}
</script>

<template>
  <div class="h-full flex flex-col">
    <!-- Header -->
    <div class="px-8 py-4 bg-white border-b border-gray-100 flex items-center gap-4">
      <button
        @click="router.push('/knowledge-bases')"
        class="text-gray-400 hover:text-gray-600 transition-colors text-sm"
      >
        ← 返回
      </button>
      <div>
        <h2 class="text-lg font-bold text-gray-800">{{ kb?.name ?? '加载中...' }}</h2>
        <p class="text-xs text-gray-400 font-mono">{{ kb?.collection_name }}</p>
      </div>
    </div>

    <!-- Body: documents + chat -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Documents panel -->
      <div class="w-80 shrink-0 border-r border-gray-100 p-4 overflow-y-auto">
        <div class="mb-4">
          <FileUpload :kb-id="kbId" @uploaded="loadDocuments" />
        </div>
        <DocumentList :documents="kbStore.documents" :loading="docsLoading" />
      </div>

      <!-- Chat panel -->
      <div class="flex-1 p-4 overflow-hidden">
        <ChatPanel :knowledge-base-id="kbId" />
      </div>
    </div>
  </div>
</template>
