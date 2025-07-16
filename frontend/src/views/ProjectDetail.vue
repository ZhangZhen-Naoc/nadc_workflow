<template>
  <el-card>
    <template #header>
      <span>项目详情</span>
    </template>
    <div v-if="project">
      <p><b>ID：</b>{{ project.id }}</p>
      <p><b>名称：</b>{{ project.name }}</p>
      <p><b>描述：</b>{{ project.description }}</p>
      <p><b>创建时间：</b>{{ project.created_at }}</p>

      <!-- 流水线配置列表 -->
      <el-divider content-position="left">流水线配置列表</el-divider>
      <div v-if="templates.length > 0">
        <el-table :data="templates" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="名称" />
          <el-table-column prop="description" label="描述" show-overflow-tooltip />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
              {{ formatDate(scope.row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button
                size="small"
                type="primary"
                @click="runWorkflow(scope.row.id)"
                :loading="scope.row.running"
              >
                运行
              </el-button>
              <el-button size="small" type="warning" @click="editTemplate(scope.row)">
                编辑
              </el-button>
              <el-button size="small" type="danger" @click="deleteTemplate(scope.row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div v-else>
        <el-empty description="暂无流水线配置" />
      </div>
    </div>
    <div v-else>
      <el-empty description="未找到项目" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import http from '@/utils/http'
import { ElMessage, ElMessageBox } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface Project {
  id: number
  name: string
  description?: string
  created_at?: string
}

interface WorkflowTemplate {
  id: number
  name: string
  description?: string
  config: Record<string, unknown>
  project_id: number
  created_at?: string
  updated_at?: string
  running?: boolean
}

const route = useRoute()
const router = useRouter()
const project = ref<Project | null>(null)
const templates = ref<WorkflowTemplate[]>([])

const fetchProject = async () => {
  const id = route.params.id
  try {
    const res = await http.get(`/projects/${id}/`)
    project.value = res as unknown as Project
  } catch {
    project.value = null
  }
}

const fetchTemplates = async () => {
  const projectId = route.params.id
  try {
    const res = await http.get(`/workflow-template/?projectId=${projectId}`)
    templates.value = (res as unknown as { templates: WorkflowTemplate[] }).templates || []
  } catch (error) {
    console.error('获取流水线配置失败:', error)
    templates.value = []
  }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const runWorkflow = async (templateId: number) => {
  const template = templates.value.find((t) => t.id === templateId)
  if (!template) return

  template.running = true
  try {
    await http.post(`/workflow-template/${templateId}/run`)
    ElMessage.success('流水线启动成功')
  } catch (error) {
    console.error('启动流水线失败:', error)
    ElMessage.error('启动流水线失败')
  } finally {
    template.running = false
  }
}

const editTemplate = (template: WorkflowTemplate) => {
  // 跳转到编辑页面
  router.push(`/template/${template.id}/edit`)
}

const deleteTemplate = async (templateId: number) => {
  try {
    await ElMessageBox.confirm('确定要删除这个流水线配置吗？此操作不可恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    await http.delete(`/workflow-template/${templateId}/`)
    ElMessage.success('删除成功')
    await fetchTemplates() // 重新获取列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchProject()
  fetchTemplates()
})
</script>
