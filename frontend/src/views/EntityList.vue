<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>实体列表</span>
        <el-button type="primary" @click="fetchEntities" :loading="loading" size="small">
          刷新
        </el-button>
      </div>
    </template>

    <div class="search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索实体名称"
        style="width: 300px; margin-right: 10px"
        clearable
        @input="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      <el-select
        v-model="searchType"
        placeholder="搜索类型"
        style="width: 150px; margin-right: 10px"
      >
        <el-option label="全部" value="" />
        <el-option label="实体" value="entity" />
        <el-option label="活动" value="activity" />
        <el-option label="代理" value="agent" />
      </el-select>
    </div>

    <el-table :data="filteredEntities" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="200">
        <template #default="scope">
          <div class="id-cell">
            <span class="id-text">{{ scope.row.id }}</span>
            <el-button
              size="small"
              type="primary"
              link
              @click="copyId(scope.row.id)"
              title="复制ID"
            >
              <el-icon><CopyDocument /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="type" label="类型" width="100">
        <template #default="scope">
          <el-tag :type="getTypeTagType(scope.row.type)">
            {{ getTypeLabel(scope.row.type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="位置" show-overflow-tooltip />
      <el-table-column prop="generated_at_time" label="生成时间" width="180">
        <template #default="scope">
          {{ formatTime(scope.row.generated_at_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button
            size="small"
            type="primary"
            @click="viewProvenance(scope.row)"
            :disabled="scope.row.type !== 'entity'"
          >
            查看溯源
          </el-button>
          <el-button size="small" @click="copyId(scope.row.id)"> 复制ID </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="filteredEntities.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无实体数据" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { provenanceAPI, type Activity, type Agent, type Entity } from '@/utils/api'
import { CopyDocument, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

interface EntityItem extends Entity {
  type: 'entity'
}

interface ActivityItem extends Activity {
  type: 'activity'
}

interface AgentItem extends Agent {
  type: 'agent'
}

type Item = EntityItem | ActivityItem | AgentItem

const router = useRouter()
const loading = ref(false)
const searchQuery = ref('')
const searchType = ref('')
const entities = ref<Item[]>([])

// 过滤后的实体列表
const filteredEntities = computed(() => {
  let filtered = entities.value

  // 按类型过滤
  if (searchType.value) {
    filtered = filtered.filter((item) => item.type === searchType.value)
  }

  // 按名称搜索
  if (searchQuery.value) {
    filtered = filtered.filter((item) =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase()),
    )
  }

  return filtered
})

// 获取类型标签
const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    entity: '实体',
    activity: '活动',
    agent: '代理',
  }
  return labels[type] || type
}

// 获取类型标签样式
const getTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    entity: 'primary',
    activity: 'success',
    agent: 'warning',
  }
  return types[type] || ''
}

// 格式化时间
const formatTime = (time: string | undefined) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

// 复制ID到剪贴板
const copyId = async (id: string) => {
  try {
    await navigator.clipboard.writeText(id)
    ElMessage.success('ID已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 查看溯源
const viewProvenance = (item: Item) => {
  if (item.type === 'entity') {
    router.push({
      name: 'Provenance',
      query: { entityId: item.id },
    })
  }
}

// 搜索处理
const handleSearch = () => {
  // 实时搜索，不需要额外处理
}

// 获取实体列表
const fetchEntities = async () => {
  try {
    loading.value = true
    const response = await provenanceAPI.getGraph()
    if (response.success) {
      const { entities: entityList, activities, agents } = response.data

      // 合并所有类型的项目
      const allItems: Item[] = [
        ...entityList.map((entity) => ({ ...entity, type: 'entity' as const })),
        ...activities.map((activity) => ({ ...activity, type: 'activity' as const })),
        ...agents.map((agent) => ({ ...agent, type: 'agent' as const })),
      ]

      entities.value = allItems
    }
  } catch (error) {
    console.error('获取实体列表失败:', error)
    ElMessage.error('获取实体列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchEntities()
})
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.id-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.id-text {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
}

.empty-state {
  margin-top: 40px;
}
</style>
