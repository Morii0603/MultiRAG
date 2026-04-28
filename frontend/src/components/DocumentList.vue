<script setup lang="ts">
import type { Document } from '@/types'

defineProps<{ documents: Document[]; loading: boolean }>()
</script>

<template>
  <div>
    <div v-if="loading" class="text-center py-8 text-gray-400 text-sm">加载中...</div>

    <div v-else-if="!documents.length" class="text-center py-8 text-gray-400 text-sm">
      暂无文档，请上传
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="flex items-center gap-3 px-3 py-2.5 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors"
      >
        <span class="text-lg shrink-0">📄</span>
        <div class="min-w-0 flex-1">
          <div class="text-sm font-medium text-gray-700 truncate" :title="doc.filename">
            {{ doc.filename }}
          </div>
          <div class="text-xs text-gray-400 mt-0.5">
            {{ doc.chunk_count }} 个块 ·
            {{ (doc.file_size / 1024).toFixed(1) }} KB ·
            {{ new Date(doc.created_at).toLocaleDateString('zh-CN') }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
