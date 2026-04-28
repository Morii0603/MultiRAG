import api from './index'
import type { KnowledgeBase, CreateKBRequest } from '@/types'

export const knowledgeBaseApi = {
  list() {
    return api.get<KnowledgeBase[]>('/knowledge-bases/')
  },
  create(data: CreateKBRequest) {
    return api.post<KnowledgeBase>('/knowledge-bases/', data)
  },
  delete(id: number) {
    return api.delete(`/knowledge-bases/${id}`)
  },
  getDocuments(kbId: number) {
    return api.get<import('@/types').Document[]>(`/knowledge-bases/${kbId}/documents`)
  },
}
