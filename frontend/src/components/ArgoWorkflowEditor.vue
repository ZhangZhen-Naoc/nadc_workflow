<template>
  <div class="workflow-editor">
    <div class="editor-toolbar">
      <el-button-group>
        <el-button size="small" @click="addStep">添加步骤</el-button>
        <el-button size="small" @click="deleteSelected" :disabled="!selectedNode"
          >删除选中</el-button
        >
      </el-button-group>
      <el-button size="small" @click="exportYaml">导出YAML</el-button>
    </div>

    <div class="editor-container">
      <VueFlow
        v-model="elements"
        :default-viewport="{ zoom: 1 }"
        :min-zoom="0.2"
        :max-zoom="4"
        class="workflow-canvas"
        @node-click="onNodeClick"
        @pane-click="onPaneClick"
        @connect="onConnect"
        @nodes-delete="onNodesDelete"
      >
        <template #node-custom="nodeProps">
          <WorkflowNode
            :data="nodeProps.data"
            :selected="nodeProps.selected"
            @click="onNodeClick(nodeProps)"
          />
        </template>

        <Background pattern-color="#aaa" gap="8" />
        <MiniMap />
        <Controls />
        <Panel position="top-right" class="controls-panel">
          <el-button size="small" @click="fitView">适应视图</el-button>
          <el-button size="small" @click="zoomIn">放大</el-button>
          <el-button size="small" @click="zoomOut">缩小</el-button>
        </Panel>
      </VueFlow>
    </div>

    <!-- 步骤属性编辑面板 -->
    <el-drawer
      v-model="showProperties"
      title="步骤属性"
      direction="rtl"
      size="400px"
      :before-close="onPropertiesClose"
    >
      <div v-if="selectedStep" class="properties-panel">
        <el-form :model="selectedStep" label-width="100px">
          <el-form-item label="步骤名称">
            <el-input v-model="selectedStep.name" placeholder="请输入步骤名称" />
          </el-form-item>

          <el-form-item label="容器镜像">
            <el-input v-model="selectedStep.image" placeholder="请输入容器镜像" />
          </el-form-item>

          <el-form-item label="执行命令">
            <el-input
              v-model="selectedStep.command"
              type="textarea"
              :rows="3"
              placeholder="请输入执行命令"
            />
          </el-form-item>

          <el-form-item label="参数">
            <div v-for="(arg, index) in selectedStep.args" :key="index" class="arg-item">
              <el-input v-model="selectedStep.args[index]" placeholder="参数值" />
              <el-button size="small" type="danger" @click="removeArg(index)">删除</el-button>
            </div>
            <el-button size="small" @click="addArg">添加参数</el-button>
          </el-form-item>

          <el-form-item label="环境变量">
            <div v-for="(env, index) in selectedStep.env" :key="index" class="env-item">
              <el-input v-model="env.name" placeholder="变量名" style="width: 40%" />
              <el-input v-model="env.value" placeholder="变量值" style="width: 40%" />
              <el-button size="small" type="danger" @click="removeEnv(index)">删除</el-button>
            </div>
            <el-button size="small" @click="addEnv">添加环境变量</el-button>
          </el-form-item>

          <el-form-item label="资源限制">
            <el-input v-model="selectedStep.resources.requests.memory" placeholder="内存请求" />
            <el-input v-model="selectedStep.resources.requests.cpu" placeholder="CPU请求" />
            <el-input v-model="selectedStep.resources.limits.memory" placeholder="内存限制" />
            <el-input v-model="selectedStep.resources.limits.cpu" placeholder="CPU限制" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveStepProperties">保存</el-button>
            <el-button @click="showProperties = false">取消</el-button>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { Panel, VueFlow, useVueFlow } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import { MiniMap } from '@vue-flow/minimap'
import * as yaml from 'js-yaml'
import { ref, watch } from 'vue'
import WorkflowNode from './WorkflowNode.vue'

interface WorkflowStep {
  id: string
  name: string
  image: string
  command: string
  args: string[]
  env: Array<{ name: string; value: string }>
  resources: {
    requests: { memory: string; cpu: string }
    limits: { memory: string; cpu: string }
  }
}

interface WorkflowNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: WorkflowStep
}

interface WorkflowEdge {
  id: string
  source: string
  target: string
  type: string
}

const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const { fitView, zoomIn, zoomOut } = useVueFlow()

const elements = ref<(WorkflowNode | WorkflowEdge)[]>([])
const selectedNode = ref<WorkflowNode | null>(null)
const selectedStep = ref<WorkflowStep | null>(null)
const showProperties = ref(false)

// 从YAML解析workflow配置
const parseYamlToElements = (yamlStr: string) => {
  try {
    const workflow = yaml.load(yamlStr) as Record<string, any>
    const nodes: WorkflowNode[] = []
    const edges: WorkflowEdge[] = []

    if (workflow?.spec?.templates) {
      workflow.spec.templates.forEach((template: Record<string, any>) => {
        if (template.steps) {
          template.steps.forEach((stepGroup: any[], stepGroupIndex: number) => {
            stepGroup.forEach((step: Record<string, any>, stepIndex: number) => {
              const stepId = `${template.name}-${stepGroupIndex}-${stepIndex}`
              const stepName = step.name || step.template || 'unnamed'

              const node: WorkflowNode = {
                id: stepId,
                type: 'custom',
                position: {
                  x: stepGroupIndex * 200 + 100,
                  y: stepIndex * 120 + 100,
                },
                data: {
                  id: stepId,
                  name: stepName,
                  image: step.container?.image || '',
                  command: step.container?.command?.join(' ') || '',
                  args: step.container?.args || [],
                  env:
                    step.container?.env?.map((e: Record<string, any>) => ({
                      name: e.name,
                      value: e.value || '',
                    })) || [],
                  resources: {
                    requests: {
                      memory: step.container?.resources?.requests?.memory || '',
                      cpu: step.container?.resources?.requests?.cpu || '',
                    },
                    limits: {
                      memory: step.container?.resources?.limits?.memory || '',
                      cpu: step.container?.resources?.limits?.cpu || '',
                    },
                  },
                },
              }
              nodes.push(node)
            })
          })
        }
      })
    }

    elements.value = [...nodes, ...edges]
  } catch {
    console.error('解析YAML失败')
    elements.value = []
  }
}

// 将elements转换为YAML
const elementsToYaml = () => {
  const nodes = elements.value.filter((el) => 'data' in el) as WorkflowNode[]

  const templates = [
    {
      name: 'main',
      steps: [],
    },
  ]

  // 按位置分组steps
  const stepGroups: Record<number, any[]> = {}
  nodes.forEach((node) => {
    const groupIndex = Math.floor(node.position.x / 200)
    if (!stepGroups[groupIndex]) {
      stepGroups[groupIndex] = []
    }

    const step = {
      name: node.data.name,
      container: {
        image: node.data.image,
        command: node.data.command ? node.data.command.split(' ') : undefined,
        args: node.data.args.length > 0 ? node.data.args : undefined,
        env: node.data.env.length > 0 ? node.data.env : undefined,
        resources: {
          requests: {
            memory: node.data.resources.requests.memory || undefined,
            cpu: node.data.resources.requests.cpu || undefined,
          },
          limits: {
            memory: node.data.resources.limits.memory || undefined,
            cpu: node.data.resources.limits.cpu || undefined,
          },
        },
      },
    }

    // 清理undefined值
    Object.keys(step.container).forEach((key) => {
      const container = step.container as Record<string, any>
      if (container[key] === undefined) {
        delete container[key]
      }
    })

    stepGroups[groupIndex].push(step)
  })

  // 转换为steps数组
  Object.keys(stepGroups).forEach((groupIndex) => {
    templates[0].steps.push(stepGroups[parseInt(groupIndex)])
  })

  const workflow = {
    apiVersion: 'argoproj.io/v1alpha1',
    kind: 'Workflow',
    metadata: {
      name: 'workflow',
    },
    spec: {
      templates: templates,
    },
  }

  return yaml.dump(workflow, { indent: 2 })
}

// 监听YAML变化
watch(
  () => props.modelValue,
  (newValue) => {
    if (newValue) {
      parseYamlToElements(newValue)
    }
  },
  { immediate: true },
)

// 监听elements变化，更新YAML
watch(
  elements,
  () => {
    const yamlStr = elementsToYaml()
    emit('update:modelValue', yamlStr)
  },
  { deep: true },
)

// 事件处理
const onNodeClick = (node: any) => {
  selectedNode.value = node
  selectedStep.value = { ...node.data }
  showProperties.value = true
}

const onPaneClick = () => {
  selectedNode.value = null
  showProperties.value = false
}

const onConnect = (params: any) => {
  const newEdge: WorkflowEdge = {
    id: `${params.source}-${params.target}`,
    source: params.source,
    target: params.target,
    type: 'smoothstep',
  }
  elements.value.push(newEdge)
}

const onNodesDelete = (nodes: WorkflowNode[]) => {
  // 删除相关的边
  const nodeIds = nodes.map((n) => n.id)
  elements.value = elements.value.filter((el) => {
    if ('source' in el) {
      return !nodeIds.includes(el.source) && !nodeIds.includes(el.target)
    }
    return true
  })
}

// 工具栏操作
const addStep = () => {
  const newNode: WorkflowNode = {
    id: `step-${Date.now()}`,
    type: 'custom',
    position: { x: 100, y: 100 },
    data: {
      id: `step-${Date.now()}`,
      name: '新步骤',
      image: '',
      command: '',
      args: [],
      env: [],
      resources: {
        requests: { memory: '', cpu: '' },
        limits: { memory: '', cpu: '' },
      },
    },
  }
  elements.value.push(newNode)
}

const deleteSelected = () => {
  if (selectedNode.value) {
    elements.value = elements.value.filter((el) => el.id !== selectedNode.value!.id)
    selectedNode.value = null
    showProperties.value = false
  }
}

const exportYaml = () => {
  const yamlStr = elementsToYaml()
  console.log('Export YAML:', yamlStr)
}

// 属性面板操作
const addArg = () => {
  if (selectedStep.value) {
    selectedStep.value.args.push('')
  }
}

const removeArg = (index: number) => {
  if (selectedStep.value) {
    selectedStep.value.args.splice(index, 1)
  }
}

const addEnv = () => {
  if (selectedStep.value) {
    selectedStep.value.env.push({ name: '', value: '' })
  }
}

const removeEnv = (index: number) => {
  if (selectedStep.value) {
    selectedStep.value.env.splice(index, 1)
  }
}

const saveStepProperties = () => {
  if (selectedStep.value && selectedNode.value) {
    // 更新节点数据
    const nodeIndex = elements.value.findIndex((el) => el.id === selectedNode.value!.id)
    if (nodeIndex !== -1) {
      ;(elements.value[nodeIndex] as WorkflowNode).data = { ...selectedStep.value }
    }
    showProperties.value = false
  }
}

const onPropertiesClose = () => {
  selectedStep.value = null
  selectedNode.value = null
}
</script>

<style scoped>
.workflow-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.editor-toolbar {
  padding: 10px;
  border-bottom: 1px solid #e4e7ed;
  background: #f5f7fa;
}

.editor-container {
  flex: 1;
  position: relative;
}

.workflow-canvas {
  height: 100%;
  background: #fafafa;
}

.controls-panel {
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 8px;
}

.properties-panel {
  padding: 20px;
}

.arg-item,
.env-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.arg-item .el-input,
.env-item .el-input {
  flex: 1;
}
</style>
