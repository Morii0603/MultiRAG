import api from './index'

export const ingestApi = {
  upload(file: File, knowledgeBaseId: number) {
    const form = new FormData()
    form.append('file', file)
    form.append('knowledge_base_id', String(knowledgeBaseId))
    return api.post('/ingest/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
    })
  },
}
