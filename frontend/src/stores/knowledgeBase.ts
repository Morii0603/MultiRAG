import { defineStore } from 'pinia'
import { ref } from 'vue'
import { knowledgeBaseApi } from '@/api/knowledgeBases'
import type { KnowledgeBase, Document } from '@/types'

export const useKnowledgeBaseStore = defineStore('knowledgeBase', () => {
  const list = ref<KnowledgeBase[]>([])
  const documents = ref<Document[]>([])
  const loading = ref(false)

  async function fetchList() {
    loading.value = true
    try {
      const res = await knowledgeBaseApi.list()
      list.value = res.data
    } finally {
      loading.value = false
    }
  }

  async function create(data: { name: string; description?: string | null }) {
    const res = await knowledgeBaseApi.create(data)
    list.value.unshift(res.data)
    return res.data
  }

  async function remove(id: number) {
    await knowledgeBaseApi.delete(id)
    list.value = list.value.filter((kb) => kb.id !== id)
  }

  async function fetchDocuments(kbId: number) {
    const res = await knowledgeBaseApi.getDocuments(kbId)
    documents.value = res.data
    return res.data
  }

  return { list, documents, loading, fetchList, create, remove, fetchDocuments }
})
