<template>
  <div class="provenance-test">
    <div class="test-header">
      <h1>ProvenanceGraph 组件测试</h1>
      <p>测试基于 ProvenanceGraph API 的溯源图可视化功能</p>
    </div>

    <div class="test-content">
      <ProvenanceGraph />
    </div>
  </div>
</template>

<script setup lang="ts">
import ProvenanceGraph from '@/components/ProvenanceGraph.vue'
</script>

<style scoped>
.provenance-test {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.test-header {
  padding: 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.test-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
  font-size: 24px;
}

.test-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.test-content {
  flex: 1;
  overflow: hidden;
}
</style>
