<template>
  <div class="provenance-view">
    <ProvenanceGraph />
  </div>
</template>

<script setup lang="ts">
import ProvenanceGraph from '@/components/ProvenanceGraph.vue'
</script>

<style scoped>
.provenance-view {
  height: 100vh;
  width: 100%;
}
</style>
