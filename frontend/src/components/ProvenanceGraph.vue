<template>
  <div class="provenance-graph">
    <div class="graph-header">
      <h2>{{ $t('graph.title') }}</h2>
      <div class="search-section">
        <el-input
          v-model="entityId"
          :placeholder="$t('graph.entity') + 'ID'"
          style="width: 300px; margin-right: 10px"
        />
        <el-button type="primary" @click="loadEntityProvenance" :loading="loading">
          {{ $t('button.loadEntity') }}
        </el-button>
        <el-input
          v-model="activityId"
          :placeholder="$t('graph.activity') + 'ID'"
          style="width: 300px; margin-right: 10px"
        />
        <el-button type="success" @click="loadActivityProvenance" :loading="loading">
          {{ $t('button.loadActivity') }}
        </el-button>
        <el-button @click="loadGraphSummary" :loading="loading">
          {{ $t('button.summary') }}
        </el-button>
      </div>
    </div>

    <div class="graph-container">
      <VueFlow
        v-model="elements"
        :default-viewport="{ zoom: 1.2 }"
        :min-zoom="0.2"
        :max-zoom="4"
        class="provenance-flow"
        @node-click="onNodeClick"
      >
        <template #node-custom="props">
          <div class="custom-node" :class="props.data.type">
            <div class="node-header">
              <span class="node-type">{{ getNodeTypeLabel(props.data.type) }}</span>
              <span v-if="props.data.level !== undefined" class="node-level">
                {{ $t('graph.level') }}: {{ props.data.level }}
              </span>
            </div>
            <div class="node-content">
              <div class="node-name">{{ props.data.label }}</div>
              <div v-if="props.data.location" class="node-location">
                {{ props.data.location }}
              </div>
              <div v-if="props.data.time" class="node-time">
                {{ formatTime(props.data.time) }}
              </div>
              <div v-if="props.data.comment" class="node-comment">
                {{ props.data.comment }}
              </div>
            </div>
          </div>
        </template>

        <Controls />
        <MiniMap />
        <Background pattern-color="#aaa" :gap="8" />
      </VueFlow>

      <!-- 图例 -->
      <div class="legend">
        <h4>{{ $t('graph.legend') }}</h4>

        <!-- 节点类型图例 -->
        <div class="legend-section">
          <h5>{{ $t('graph.entity') }}</h5>
          <div class="legend-item">
            <div class="legend-node entity"></div>
            <span>{{ $t('graph.entity') }}</span>
          </div>
          <div class="legend-item">
            <div class="legend-node activity"></div>
            <span>{{ $t('graph.activity') }}</span>
          </div>
        </div>

        <!-- 关系类型图例 -->
        <div class="legend-section">
          <h5>{{ $t('graph.activity') }}</h5>
          <div class="legend-item">
            <div class="legend-line" style="background-color: #409eff"></div>
            <span>{{ $t('graph.used') }} (used)</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="background-color: #67c23a"></div>
            <span>{{ $t('graph.was_generated_by') }} (was_generated_by)</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="background-color: #e6a23c"></div>
            <span>{{ $t('graph.was_derived_from') }} (was_derived_from)</span>
          </div>
          <div class="legend-item">
            <div class="legend-line" style="background-color: #909399"></div>
            <span>{{ $t('graph.was_informed_by') }} (was_informed_by)</span>
          </div>
        </div>

        <!-- 图信息 -->
        <div v-if="graphInfo" class="legend-section">
          <h5>{{ $t('graph.info') }}</h5>
          <div class="graph-info">
            <div class="info-item">
              <span>{{ $t('graph.total_nodes') }}:</span>
              <span>{{ graphInfo.total_nodes }}</span>
            </div>
            <div class="info-item">
              <span>{{ $t('graph.total_edges') }}:</span>
              <span>{{ graphInfo.total_edges }}</span>
            </div>
            <div class="info-item">
              <span>{{ $t('graph.graph_type') }}:</span>
              <span>{{ graphInfo.graph_type }}</span>
            </div>
            <div class="info-item">
              <span>{{ $t('graph.generated_at') }}:</span>
              <span>{{ formatTime(graphInfo.generated_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 节点详情弹窗 -->
    <el-dialog
      v-model="showNodeDetail"
      :title="$t('dialog.nodeDetail')"
      width="600px"
      :before-close="closeNodeDetail"
    >
      <div v-if="selectedNode" class="node-detail">
        <h3>{{ selectedNode.data.label }}</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="$t('graph.entity')">
            {{ getNodeTypeLabel(selectedNode.data.type) }}
          </el-descriptions-item>
          <el-descriptions-item
            v-if="selectedNode.data.level !== undefined"
            label="$t('graph.activity')"
          >
            {{ selectedNode.data.level }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedNode.data.location" label="$t('graph.info')">
            {{ selectedNode.data.location }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedNode.data.time" label="$t('graph.info')">
            {{ formatTime(selectedNode.data.time) }}
          </el-descriptions-item>
          <el-descriptions-item v-if="selectedNode.data.comment" label="$t('graph.info')">
            {{ selectedNode.data.comment }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 关系信息 -->
        <div v-if="nodeRelations.length > 0" class="relations-section">
          <h4>关系信息</h4>
          <el-table :data="nodeRelations" style="width: 100%">
            <el-table-column prop="type" label="关系类型" width="120">
              <template #default="scope">
                <el-tag :type="getRelationTagType(scope.row.type)">
                  {{ getRelationLabel(scope.row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="target" label="目标节点" />
            <el-table-column prop="role" label="角色" width="100" />
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 图摘要弹窗 -->
    <el-dialog
      v-model="showSummaryDialog"
      :title="$t('graph.summary')"
      width="800px"
      :before-close="closeSummaryDialog"
    >
      <div v-if="summaryData" class="summary-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>{{ $t('graph.entity_stat') }}</span>
                </div>
              </template>
              <div class="stat-item">
                <span>总数:</span>
                <span>{{ summaryData.entities.total }}</span>
              </div>
              <div class="stat-item">
                <span>有时间信息:</span>
                <span>{{ summaryData.entities.with_generation_time }}</span>
              </div>
              <div class="stat-item">
                <span>完整度:</span>
                <span>{{ summaryData.entities.percentage_with_time }}%</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>{{ $t('graph.activity_stat') }}</span>
                </div>
              </template>
              <div class="stat-item">
                <span>总数:</span>
                <span>{{ summaryData.activities.total }}</span>
              </div>
              <div class="stat-item">
                <span>有开始时间:</span>
                <span>{{ summaryData.activities.with_start_time }}</span>
              </div>
              <div class="stat-item">
                <span>有结束时间:</span>
                <span>{{ summaryData.activities.with_end_time }}</span>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>{{ $t('graph.relationships_stat') }}</span>
                </div>
              </template>
              <div class="stat-item">
                <span>{{ $t('graph.used_relation') }}:</span>
                <span>{{ summaryData.relationships.used }}</span>
              </div>
              <div class="stat-item">
                <span>{{ $t('graph.was_generated_by_relation') }}:</span>
                <span>{{ summaryData.relationships.was_generated_by }}</span>
              </div>
              <div class="stat-item">
                <span>{{ $t('graph.was_derived_from_relation') }}:</span>
                <span>{{ summaryData.relationships.was_derived_from }}</span>
              </div>
              <div class="stat-item">
                <span>{{ $t('graph.was_informed_by_relation') }}:</span>
                <span>{{ summaryData.relationships.was_informed_by }}</span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import '@vue-flow/controls/dist/style.css'
import { VueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import { MiniMap } from '@vue-flow/minimap'
import '@vue-flow/minimap/dist/style.css'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t: $t } = useI18n()

// 定义类型
interface NodeDetails {
  location?: string
  generated_at_time?: string
  start_time?: string
  end_time?: string
  comment?: string
}

interface NodeData {
  type: 'entity' | 'activity'
  label: string
  level?: number
  location?: string
  time?: string
  comment?: string
  details?: NodeDetails
  graphId?: string // 用于图的连接
  apiId?: number // 用于API检索详细信息
}

interface NodeElement {
  id: string
  type: string
  position: { x: number; y: number }
  data: NodeData
}

interface EdgeElement {
  id: string
  source: string
  target: string
  type: string
  label: string
  data: {
    type: string
    role?: string
  }
  style: {
    stroke: string
    strokeWidth: number
  }
  markerEnd?: {
    type: string
    color: string
  }
}

interface NodeRelation {
  type: string
  target: string
  role?: string
}

interface GraphInfo {
  total_nodes: number
  total_edges: number
  graph_type: string
  generated_at: string
}

interface GraphNode {
  graph_id: string // 用于图的连接
  id: number // 用于API检索详细信息
  type: 'entity' | 'activity'
  name: string
  level: number
  details?: NodeDetails
}

interface GraphEdge {
  source: string // 使用graph_id作为边的源和目标
  target: string
  type: string
  role?: string
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  total_nodes: number
  total_edges: number
  graph_metadata: {
    graph_type: string
    generated_at: string
  }
}

interface SummaryData {
  entities: {
    total: number
    with_generation_time: number
    percentage_with_time: number
  }
  activities: {
    total: number
    with_start_time: number
    with_end_time: number
    percentage_with_start_time: number
    percentage_with_end_time: number
  }
  relationships: {
    used: number
    was_generated_by: number
    was_derived_from: number
    was_informed_by: number
    total: number
  }
}

// 响应式数据
const entityId = ref('')
const activityId = ref('')
const loading = ref(false)
const showNodeDetail = ref(false)
const showSummaryDialog = ref(false)
const selectedNode = ref<NodeElement | null>(null)
const nodeRelations = ref<NodeRelation[]>([])
const graphInfo = ref<GraphInfo | null>(null)
const summaryData = ref<SummaryData | null>(null)

// VueFlow元素
const elements = ref<(NodeElement | EdgeElement)[]>([])

// 节点类型标签
const getNodeTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    entity: $t('graph.entity'),
    activity: $t('graph.activity'),
  }
  return labels[type] || type
}

// 关系标签
const getRelationLabel = (type: string) => {
  const labels: Record<string, string> = {
    used: $t('graph.used'),
    was_generated_by: $t('graph.was_generated_by'),
    was_derived_from: $t('graph.was_derived_from'),
    was_informed_by: $t('graph.was_informed_by'),
  }
  return labels[type] || type
}

// 关系标签类型
const getRelationTagType = (type: string) => {
  const types: Record<string, string> = {
    used: 'primary',
    was_generated_by: 'success',
    was_derived_from: 'warning',
    was_informed_by: 'info',
  }
  return types[type] || ''
}

// 格式化时间
const formatTime = (time: string) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

// 加载实体溯源图
const loadEntityProvenance = async () => {
  if (!entityId.value.trim()) {
    ElMessage.warning('请输入Entity ID')
    return
  }

  try {
    loading.value = true
    const response = await fetch(`/api/provenance/graph/${entityId.value.trim()}`)
    const data = await response.json()

    if (data.success) {
      generateGraphElements(data.data)
      graphInfo.value = {
        total_nodes: data.data.total_nodes,
        total_edges: data.data.total_edges,
        graph_type: data.data.graph_metadata.graph_type,
        generated_at: data.data.graph_metadata.generated_at,
      }
      ElMessage.success('实体溯源图加载成功')
    } else {
      ElMessage.error(data.error || '加载失败')
    }
  } catch (error) {
    console.error('加载实体溯源失败:', error)
    ElMessage.error('加载实体溯源失败')
  } finally {
    loading.value = false
  }
}

// 加载活动溯源图
const loadActivityProvenance = async () => {
  if (!activityId.value.trim()) {
    ElMessage.warning('请输入Activity ID')
    return
  }

  try {
    loading.value = true
    const response = await fetch(`/api/provenance/activity-graph/${activityId.value.trim()}`)
    const data = await response.json()

    if (data.success) {
      generateGraphElements(data.data)
      graphInfo.value = {
        total_nodes: data.data.total_nodes,
        total_edges: data.data.total_edges,
        graph_type: data.data.graph_metadata.graph_type,
        generated_at: data.data.graph_metadata.generated_at,
      }
      ElMessage.success('活动溯源图加载成功')
    } else {
      ElMessage.error(data.error || '加载失败')
    }
  } catch (error) {
    console.error('加载活动溯源失败:', error)
    ElMessage.error('加载活动溯源失败')
  } finally {
    loading.value = false
  }
}

// 加载图摘要
const loadGraphSummary = async () => {
  try {
    loading.value = true
    const response = await fetch('/api/provenance/graph-summary')
    const data = await response.json()

    if (data.success) {
      summaryData.value = data.data
      showSummaryDialog.value = true
      ElMessage.success('图摘要加载成功')
    } else {
      ElMessage.error(data.error || '加载失败')
    }
  } catch (error) {
    console.error('加载图摘要失败:', error)
    ElMessage.error('加载图摘要失败')
  } finally {
    loading.value = false
  }
}

// 生成图元素
const generateGraphElements = (graphData: GraphData) => {
  const nodes: NodeElement[] = []
  const edges: EdgeElement[] = []

  // 添加节点
  graphData.nodes.forEach((node: GraphNode) => {
    const position = calculateNodePosition(node.level, nodes.length)

    nodes.push({
      id: node.graph_id, // 使用graph_id作为节点ID
      type: 'custom',
      position,
      data: {
        type: node.type,
        label: node.name,
        level: node.level,
        location: node.details?.location,
        time: node.details?.generated_at_time || node.details?.start_time,
        comment: node.details?.comment,
        details: node.details,
        graphId: node.graph_id, // 保存graph_id用于图的连接
        apiId: node.id, // 保存api_id用于API检索
      },
    })
  })

  // 添加边
  graphData.edges.forEach((edge: GraphEdge) => {
    const edgeColor = getEdgeColor(edge.type)
    edges.push({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      label: getRelationLabel(edge.type),
      data: {
        type: edge.type,
        role: edge.role,
      },
      style: {
        stroke: edgeColor,
        strokeWidth: 2,
      },
      markerEnd: {
        type: 'arrowclosed',
        color: edgeColor,
      },
    })
  })

  elements.value = [...nodes, ...edges]
}

// 计算节点位置
const calculateNodePosition = (level: number, index: number) => {
  const baseX = 100
  const baseY = 100
  const xSpacing = 300
  const ySpacing = 200

  return {
    x: baseX + index * xSpacing,
    y: baseY + level * ySpacing,
  }
}

// 获取边的颜色
const getEdgeColor = (type: string) => {
  const colors: Record<string, string> = {
    used: '#409EFF',
    was_generated_by: '#67C23A',
    was_derived_from: '#E6A23C',
    was_informed_by: '#909399',
  }
  return colors[type] || '#909399'
}

// 节点点击事件
const onNodeClick = (event: { node: NodeElement }) => {
  const node = event.node
  selectedNode.value = node
  showNodeDetail.value = true

  // 获取节点关系
  const nodeId = node.id
  const relations = elements.value
    .filter(
      (el) =>
        (el.id.includes('-') && (el as EdgeElement).source === nodeId) ||
        (el as EdgeElement).target === nodeId,
    )
    .map((el) => {
      const edge = el as EdgeElement
      const isSource = edge.source === nodeId
      const targetId = isSource ? edge.target : edge.source
      const targetNode = elements.value.find((n) => n.id === targetId)
      return {
        type: edge.data.type,
        target: (targetNode as NodeElement)?.data?.label || targetId,
        role: edge.data.role,
      }
    })

  nodeRelations.value = relations
}

// 关闭节点详情
const closeNodeDetail = () => {
  showNodeDetail.value = false
  selectedNode.value = null
  nodeRelations.value = []
}

// 关闭摘要弹窗
const closeSummaryDialog = () => {
  showSummaryDialog.value = false
  summaryData.value = null
}

// 组件挂载时清空图
onMounted(() => {
  elements.value = []
})
</script>

<style scoped>
.provenance-graph {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.graph-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;
}

.graph-header h2 {
  margin: 0 0 15px 0;
  color: #303133;
}

.search-section {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.graph-container {
  flex: 1;
  position: relative;
  display: flex;
}

.provenance-flow {
  height: 100%;
  background: #fafafa;
  flex: 1;
}

.custom-node {
  padding: 10px;
  border: 2px solid #ddd;
  background: white;
  min-width: 150px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.custom-node.entity {
  border-color: #409eff;
  background: #ecf5ff;
  border-radius: 50%;
  width: 150px;
  height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.custom-node.activity {
  border-color: #67c23a;
  background: #f0f9ff;
  border-radius: 8px;
}

.node-header {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.custom-node.entity .node-header {
  margin-bottom: 5px;
  flex-direction: column;
  gap: 2px;
}

.node-type {
  font-size: 12px;
  color: #909399;
  background: #f4f4f5;
  padding: 2px 6px;
  border-radius: 4px;
}

.custom-node.entity .node-type {
  font-size: 10px;
  padding: 1px 4px;
}

.node-level {
  font-size: 10px;
  color: #c0c4cc;
}

.custom-node.entity .node-level {
  font-size: 9px;
}

.node-content {
  text-align: center;
  width: 100%;
}

.custom-node.entity .node-content {
  text-align: center;
  width: 100%;
  padding: 5px;
}

.node-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
  word-break: break-word;
}

.custom-node.entity .node-name {
  font-size: 12px;
  line-height: 1.2;
}

.node-location {
  font-size: 12px;
  color: #606266;
  margin-bottom: 2px;
  word-break: break-all;
}

.custom-node.entity .node-location {
  font-size: 10px;
}

.node-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.custom-node.entity .node-time {
  font-size: 10px;
}

.node-comment {
  font-size: 11px;
  color: #c0c4cc;
  font-style: italic;
}

.custom-node.entity .node-comment {
  font-size: 9px;
}

.node-detail h3 {
  margin: 0 0 15px 0;
  color: #303133;
}

.relations-section {
  margin-top: 20px;
}

.relations-section h4 {
  margin: 0 0 10px 0;
  color: #606266;
}

.legend {
  padding: 20px;
  border-left: 1px solid #e4e7ed;
  background: #fff;
  width: 280px;
  box-shadow: -2px 0 4px rgba(0, 0, 0, 0.05);
  overflow-y: auto;
}

.legend h4 {
  margin: 0 0 15px 0;
  color: #303133;
}

.legend-section {
  margin-bottom: 20px;
}

.legend-section h5 {
  margin: 0 0 10px 0;
  color: #606266;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.legend-node {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  border: 1px solid #ddd;
}

.legend-node.entity {
  background-color: #ecf5ff;
  border-color: #409eff;
  border-radius: 50%;
}

.legend-node.activity {
  background-color: #f0f9ff;
  border-color: #67c23a;
  border-radius: 2px;
}

.legend-line {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 8px;
  border: 1px solid #ddd;
}

.graph-info {
  font-size: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.summary-content {
  padding: 10px 0;
}

.card-header {
  font-weight: bold;
  color: #303133;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.stat-item:last-child {
  margin-bottom: 0;
}
</style>
