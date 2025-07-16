<template>
  <el-card>
    <template #header>
      <div class="header-content">
        <span>编辑流水线配置</span>
        <div class="header-actions">
          <el-button @click="goBack">返回</el-button>
          <el-button type="primary" @click="saveTemplate" :loading="saving"> 保存 </el-button>
        </div>
      </div>
    </template>

    <div v-if="template">
      <el-form :model="form" label-width="120px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="请输入配置名称" />
        </el-form-item>

        <el-form-item label="配置描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入配置描述"
          />
        </el-form-item>

        <el-form-item label="YAML配置">
          <div class="yaml-editor-container">
            <el-input
              v-model="form.yamlConfig"
              type="textarea"
              :rows="20"
              placeholder="请输入YAML格式的流水线配置"
              class="yaml-editor"
            />
            <div class="yaml-actions">
              <el-button size="small" @click="formatYaml">格式化</el-button>
              <el-button size="small" @click="validateYaml">验证</el-button>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div v-else>
      <el-empty description="未找到模板" />
    </div>
  </el-card>
</template>

<script setup lang="ts">
import http from '@/utils/http'
import { ElMessage } from 'element-plus'
import * as yaml from 'js-yaml'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

interface WorkflowTemplate {
  id: number
  name: string
  description?: string
  config: Record<string, unknown>
  project_id: number
  created_at?: string
  updated_at?: string
}

const route = useRoute()
const router = useRouter()
const template = ref<WorkflowTemplate | null>(null)
const saving = ref(false)

const form = ref({
  name: '',
  description: '',
  yamlConfig: '',
})

const fetchTemplate = async () => {
  const templateId = route.params.templateId
  try {
    const res = await http.get(`/workflow-template/${templateId}/`)
    template.value = res as unknown as WorkflowTemplate

    // 填充表单
    form.value.name = template.value.name
    form.value.description = template.value.description || ''

    // 将config转换为YAML
    try {
      form.value.yamlConfig = yaml.dump(template.value.config, {
        indent: 2,
        lineWidth: 80,
        noRefs: true,
      })
    } catch {
      console.error('转换配置为YAML失败')
      form.value.yamlConfig = JSON.stringify(template.value.config, null, 2)
    }
  } catch (error) {
    console.error('获取模板失败:', error)
    ElMessage.error('获取模板失败')
  }
}

const formatYaml = () => {
  try {
    const parsed = yaml.load(form.value.yamlConfig)
    form.value.yamlConfig = yaml.dump(parsed, {
      indent: 2,
      lineWidth: 80,
      noRefs: true,
    })
    ElMessage.success('格式化成功')
  } catch (error) {
    ElMessage.error('YAML格式错误，无法格式化')
  }
}

const validateYaml = () => {
  try {
    yaml.load(form.value.yamlConfig)
    ElMessage.success('YAML格式正确')
  } catch {
    ElMessage.error('YAML格式错误')
  }
}

const saveTemplate = async () => {
  if (!template.value) return

  // 验证YAML格式
  let config: Record<string, unknown>
  try {
    config = yaml.load(form.value.yamlConfig) as Record<string, unknown>
  } catch (error) {
    ElMessage.error('YAML格式错误，请检查配置')
    return
  }

  saving.value = true
  try {
    await http.put(`/workflow-template/${template.value.id}/`, {
      name: form.value.name,
      description: form.value.description,
      config: config,
    })

    ElMessage.success('保存成功')
    goBack()
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchTemplate()
})
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.yaml-editor-container {
  position: relative;
}

.yaml-editor {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
}

.yaml-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}
</style>
