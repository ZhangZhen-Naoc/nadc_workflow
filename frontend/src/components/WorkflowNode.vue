<template>
  <div class="workflow-node" :class="{ selected: selected }" @click="$emit('click')">
    <div class="node-header">
      <el-icon class="node-icon">
        <component :is="getNodeIcon()" />
      </el-icon>
      <span class="node-name">{{ data.name }}</span>
    </div>

    <div class="node-content">
      <div v-if="data.image" class="node-info">
        <span class="info-label">镜像:</span>
        <span class="info-value">{{ data.image }}</span>
      </div>

      <div v-if="data.command" class="node-info">
        <span class="info-label">命令:</span>
        <span class="info-value">{{ truncateText(data.command, 30) }}</span>
      </div>

      <div v-if="data.args.length > 0" class="node-info">
        <span class="info-label">参数:</span>
        <span class="info-value">{{ data.args.length }}个</span>
      </div>

      <div v-if="data.env.length > 0" class="info-label">
        <span class="info-label">环境变量:</span>
        <span class="info-value">{{ data.env.length }}个</span>
      </div>
    </div>

    <div class="node-ports">
      <div class="port port-input" title="输入"></div>
      <div class="port port-output" title="输出"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CircleCheck, Connection, Cpu, Monitor, Setting } from '@element-plus/icons-vue'

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
  dependencies?: string[]
}

const props = defineProps<{
  data: WorkflowStep
  selected: boolean
}>()

defineEmits<{
  click: []
}>()

const getNodeIcon = () => {
  const name = props.data.name.toLowerCase()

  if (name.includes('build') || name.includes('构建')) {
    return Cpu
  } else if (name.includes('test') || name.includes('测试')) {
    return CircleCheck
  } else if (name.includes('deploy') || name.includes('部署')) {
    return Setting
  } else if (name.includes('condition') || name.includes('条件')) {
    return Connection
  } else if (name.includes('parallel') || name.includes('并行')) {
    return Monitor
  } else {
    return Cpu
  }
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) {
    return text
  }
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.workflow-node {
  background: white;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  padding: 12px;
  min-width: 150px;
  max-width: 200px;
  cursor: pointer;
  position: relative;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.workflow-node:hover {
  border-color: #409eff;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.workflow-node.selected {
  border-color: #409eff;
  background: #f0f9ff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-weight: 600;
  color: #303133;
}

.node-icon {
  font-size: 16px;
  color: #409eff;
}

.node-name {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-content {
  font-size: 12px;
  color: #606266;
}

.node-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
  gap: 8px;
}

.info-label {
  font-weight: 500;
  color: #909399;
}

.info-value {
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100px;
}

.node-ports {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.port {
  position: absolute;
  width: 12px;
  height: 12px;
  background: #409eff;
  border: 2px solid white;
  border-radius: 50%;
  pointer-events: all;
  cursor: crosshair;
}

.port-input {
  top: 50%;
  left: -6px;
  transform: translateY(-50%);
}

.port-output {
  top: 50%;
  right: -6px;
  transform: translateY(-50%);
}

.port:hover {
  background: #66b1ff;
  transform: translateY(-50%) scale(1.2);
}
</style>
