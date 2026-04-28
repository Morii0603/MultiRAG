<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useKnowledgeBaseStore } from '@/stores/knowledgeBase'

const router = useRouter()
const kbStore = useKnowledgeBaseStore()
const showCreate = ref(false)
const newName = ref('')
const newDesc = ref('')
const creating = ref(false)

onMounted(() => kbStore.fetchList())

async function handleCreate() {
  if (!newName.value.trim()) return
  creating.value = true
  try {
    const kb = await kbStore.create({ name: newName.value.trim(), description: newDesc.value.trim() || null })
    showCreate.value = false
    newName.value = ''
    newDesc.value = ''
    router.push(`/knowledge-bases/${kb.id}`)
  } finally {
    creating.value = false
  }
}

async function handleDelete(kb: { id: number; name: string }) {
  if (!confirm(`确定要删除知识库「${kb.name}」吗？该操作不可撤销。`)) return
  await kbStore.remove(kb.id)
}
</script>

<template>
  <div class="p-8">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-bold text-gray-800">知识库管理</h2>
      <button
        @click="showCreate = true"
        class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
      >
        + 创建知识库
      </button>
    </div>

    <!-- Create dialog -->
    <div v-if="showCreate" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40" @click.self="showCreate = false">
      <div class="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
        <h3 class="text-lg font-semibold text-gray-800 mb-4">创建知识库</h3>
        <label class="block text-sm text-gray-600 mb-1">名称</label>
        <input
          v-model="newName"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 mb-3"
          placeholder="输入知识库名称"
          @keyup.enter="handleCreate"
        />
        <label class="block text-sm text-gray-600 mb-1">描述（可选）</label>
        <textarea
          v-model="newDesc"
          class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 mb-4 resize-none"
          rows="2"
          placeholder="输入描述"
        />
        <div class="flex justify-end gap-2">
          <button
            @click="showCreate = false"
            class="px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            取消
          </button>
          <button
            @click="handleCreate"
            :disabled="!newName.trim() || creating"
            class="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover disabled:opacity-50 transition-colors"
          >
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Table -->
    <div v-if="kbStore.list.length" class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 text-left text-gray-500">
            <th class="px-5 py-3 font-medium">名称</th>
            <th class="px-5 py-3 font-medium">集合名称</th>
            <th class="px-5 py-3 font-medium">描述</th>
            <th class="px-5 py-3 font-medium">创建时间</th>
            <th class="px-5 py-3 font-medium w-20">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="kb in kbStore.list"
            :key="kb.id"
            class="border-t border-gray-100 hover:bg-gray-50 cursor-pointer"
            @click="router.push(`/knowledge-bases/${kb.id}`)"
          >
            <td class="px-5 py-3 font-medium text-gray-800">{{ kb.name }}</td>
            <td class="px-5 py-3 text-gray-500 font-mono text-xs">{{ kb.collection_name }}</td>
            <td class="px-5 py-3 text-gray-400 max-w-48 truncate">{{ kb.description || '—' }}</td>
            <td class="px-5 py-3 text-gray-500">{{ new Date(kb.created_at).toLocaleString('zh-CN') }}</td>
            <td class="px-5 py-3">
              <button
                @click.stop="handleDelete(kb)"
                class="text-red-500 hover:text-red-700 text-xs font-medium transition-colors"
              >
                删除
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="text-center py-16 text-gray-400">
      <div class="text-4xl mb-3">☰</div>
      <p>暂无知识库，点击上方按钮创建</p>
    </div>
  </div>
</template>
