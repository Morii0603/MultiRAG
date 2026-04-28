<script setup lang="ts">
import { ref } from 'vue'
import { ingestApi } from '@/api/ingest'

const props = defineProps<{ kbId: number }>()
const emit = defineEmits<{ uploaded: [] }>()

const uploading = ref(false)
const dragOver = ref(false)
const fileInput = ref<HTMLInputElement>()

function triggerUpload() {
  fileInput.value?.click()
}

async function handleFile(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  await upload(file)
  input.value = ''
}

async function handleDrop(e: DragEvent) {
  dragOver.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) await upload(file)
}

async function upload(file: File) {
  uploading.value = true
  try {
    await ingestApi.upload(file, props.kbId)
    emit('uploaded')
  } catch {
    alert('上传失败，请重试。')
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div
    class="border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer"
    :class="dragOver ? 'border-primary bg-blue-50' : 'border-gray-200 hover:border-gray-300'"
    @click="triggerUpload"
    @dragover.prevent="dragOver = true"
    @dragleave="dragOver = false"
    @drop.prevent="handleDrop"
  >
    <input ref="fileInput" type="file" class="hidden" @change="handleFile"
      accept=".pdf,.docx,.pptx,.html,.png,.jpg,.jpeg,.gif,.bmp,.tiff" />
    <div v-if="uploading" class="flex flex-col items-center gap-2">
      <div class="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
      <span class="text-sm text-gray-500">上传中...</span>
    </div>
    <div v-else>
      <div class="text-2xl text-gray-300 mb-1">+</div>
      <p class="text-sm text-gray-500">点击或拖拽文件上传</p>
      <p class="text-xs text-gray-400 mt-1">支持 PDF、DOCX、PPTX、HTML、图片</p>
    </div>
  </div>
</template>
