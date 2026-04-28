<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeBaseStore } from '@/stores/knowledgeBase'

const router = useRouter()
const kbStore = useKnowledgeBaseStore()
const totalDocs = ref(0)

onMounted(async () => {
  await kbStore.fetchList()
  totalDocs.value = kbStore.list.reduce((sum, kb) => sum + kb.id, 0)
})
</script>

<template>
  <div class="p-8">
    <h2 class="text-2xl font-bold text-gray-800 mb-6">仪表盘</h2>

    <div class="grid grid-cols-3 gap-5 mb-8">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-3xl font-bold text-primary">{{ kbStore.list.length }}</div>
        <div class="text-sm text-gray-500 mt-1">知识库总数</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-3xl font-bold text-emerald-500">{{ kbStore.documents.length }}</div>
        <div class="text-sm text-gray-500 mt-1">文档总数</div>
      </div>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
        <div class="text-3xl font-bold text-violet-500">—</div>
        <div class="text-sm text-gray-500 mt-1">活跃会话</div>
      </div>
    </div>

    <div class="flex gap-3">
      <button
        @click="router.push('/knowledge-bases')"
        class="px-5 py-2.5 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
      >
        管理知识库
      </button>
    </div>

    <div v-if="kbStore.list.length" class="mt-8">
      <h3 class="text-lg font-semibold text-gray-700 mb-3">最近创建的知识库</h3>
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="bg-gray-50 text-left text-gray-500">
              <th class="px-5 py-3 font-medium">名称</th>
              <th class="px-5 py-3 font-medium">集合名称</th>
              <th class="px-5 py-3 font-medium">创建时间</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="kb in kbStore.list.slice(0, 5)"
              :key="kb.id"
              class="border-t border-gray-100 hover:bg-gray-50 cursor-pointer"
              @click="router.push(`/knowledge-bases/${kb.id}`)"
            >
              <td class="px-5 py-3 font-medium text-gray-800">{{ kb.name }}</td>
              <td class="px-5 py-3 text-gray-500 font-mono text-xs">{{ kb.collection_name }}</td>
              <td class="px-5 py-3 text-gray-500">{{ new Date(kb.created_at).toLocaleString('zh-CN') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
