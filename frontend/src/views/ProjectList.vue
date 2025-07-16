<template>
  <el-card>
    <template #header>
      <div class="header">
        <span>项目列表</span>
        <el-button type="primary" @click="fetchProjects" :loading="loading" size="small"
          >刷新</el-button
        >
      </div>
    </template>
    <el-table :data="projects" style="width: 100%" v-loading="loading">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button size="small" @click="goDetail(scope.row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import http from '@/utils/http'
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

interface Project {
  id: number
  name: string
  description?: string
  created_at?: string
}

const projects = ref<Project[]>([])
const loading = ref(false)
const router = useRouter()

const fetchProjects = async () => {
  loading.value = true
  try {
    const res = await http.get('/projects/')
    projects.value = (res as unknown as { projects: Project[] }).projects
  } finally {
    loading.value = false
  }
}

const goDetail = (id: number) => {
  router.push({ name: 'ProjectDetail', params: { id } })
}

onMounted(fetchProjects)
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
