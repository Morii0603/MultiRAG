<script setup lang="ts">
import { RouterView, useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { path: '/', label: '仪表盘', icon: '◫' },
  { path: '/knowledge-bases', label: '知识库', icon: '☰' },
]

function isActive(path: string) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}
</script>

<template>
  <div class="flex h-screen bg-gray-50">
    <aside class="w-56 bg-sidebar flex flex-col shrink-0">
      <div class="px-5 py-5 border-b border-white/10">
        <h1 class="text-white text-base font-semibold tracking-wide">RAG Agent</h1>
      </div>
      <nav class="flex-1 py-3">
        <RouterLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-5 py-2.5 mx-2 rounded-lg text-sm transition-colors"
          :class="isActive(item.path)
            ? 'bg-sidebar-active text-white'
            : 'text-gray-300 hover:bg-sidebar-hover hover:text-white'"
        >
          <span class="text-lg">{{ item.icon }}</span>
          {{ item.label }}
        </RouterLink>
      </nav>
      <div class="px-5 py-4 border-t border-white/10 text-xs text-gray-500">
        RAG Agent v0.1
      </div>
    </aside>
    <main class="flex-1 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>
