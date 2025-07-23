// API基础配置
const API_BASE_URL = 'http://localhost:5000/api'

// 通用请求函数
async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  return response.json()
}

// 溯源相关API
export interface ProvenanceGraph {
  entities: Entity[]
  activities: Activity[]
  agents: Agent[]
  relationships: Relationship[]
}

export interface Entity {
  id: string
  name: string
  type: string
  location?: string
  generated_at_time?: string
  comment?: string
}

export interface Activity {
  id: string
  name: string
  type: string
  start_time?: string
  end_time?: string
  comment?: string
}

export interface Agent {
  id: string
  name: string
  type: string
  agent_type: string
  role?: string
  email?: string
  affiliation?: string
}

export interface Relationship {
  id: string
  type: string
  source: string
  target: string
  role?: string
  time?: string
}

export interface EntityProvenance {
  entity: Entity
  generated_by: {
    activity?: Activity
    role?: string
  }
  used_by: Array<{
    activity: Activity
    role?: string
    time?: string
  }>
  derived_from: Array<{
    entity: Entity
    role?: string
  }>
  derived_entities: Array<{
    entity: Entity
    role?: string
  }>
  attributed_to: Array<{
    agent: Agent
    role?: string
  }>
}

export interface ActivityProvenance {
  activity: Activity
  inputs: Array<{
    entity: Entity
    role?: string
    time?: string
  }>
  outputs: Array<{
    entity: Entity
    role?: string
  }>
  dependencies: Activity[]
  dependents: Activity[]
  associated_agents: Array<{
    agent: Agent
    role?: string
  }>
  configurations: Array<{
    type: string
    name: string
    value?: string
    location?: string
  }>
}

export interface TimelineEvent {
  id: string
  name: string
  type: string
  time: string
  description: string
}

export interface SearchResult {
  entities: Entity[]
  activities: Activity[]
  agents: Agent[]
}

// API函数
export const provenanceAPI = {
  // 获取完整溯源图
  getGraph: (): Promise<{ success: boolean; data: ProvenanceGraph }> => {
    return request('/provenance/graph')
  },

  // 获取实体溯源
  getEntityProvenance: (
    entityId: string,
  ): Promise<{ success: boolean; data: EntityProvenance }> => {
    return request(`/provenance/entity/${entityId}`)
  },

  // 获取活动溯源
  getActivityProvenance: (
    activityId: string,
  ): Promise<{ success: boolean; data: ActivityProvenance }> => {
    return request(`/provenance/activity/${activityId}`)
  },

  // 搜索溯源
  search: (query: string, type?: string): Promise<{ success: boolean; data: SearchResult }> => {
    const params = new URLSearchParams({ q: query })
    if (type) {
      params.append('type', type)
    }
    return request(`/provenance/search?${params.toString()}`)
  },

  // 获取时间线
  getTimeline: (): Promise<{ success: boolean; data: { timeline: TimelineEvent[] } }> => {
    return request('/provenance/timeline')
  },
}
