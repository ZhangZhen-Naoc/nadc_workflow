# ProvenanceGraph 组件使用说明

## 概述

`ProvenanceGraph` 是一个基于 Vue 3 + TypeScript 的溯源图可视化组件，使用 VueFlow 库来渲染 DAG（有向无环图）结构。该组件集成了后端 ProvenanceGraph API，能够展示数据实体的完整来源拓扑图。

## 功能特性

### 1. 多类型溯源图支持

- **实体溯源图**: 以实体为中心，展示其完整的来源关系
- **活动溯源图**: 以活动为中心，展示工作流依赖关系
- **图摘要**: 显示整体统计信息和数据质量指标

### 2. 交互式可视化

- 节点点击查看详情
- 关系类型颜色区分
- 层级信息显示
- 缩放和平移控制

### 3. 实时数据加载

- 支持输入 Entity ID 或 Activity ID
- 实时调用后端 API
- 错误处理和加载状态

## 使用方法

### 基本使用

```vue
<template>
  <div>
    <ProvenanceGraph />
  </div>
</template>

<script setup lang="ts">
import ProvenanceGraph from '@/components/ProvenanceGraph.vue'
</script>
```

### 在路由中使用

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import ProvenanceTest from '@/views/ProvenanceTest.vue'

const routes = [
  {
    path: '/provenance',
    name: 'ProvenanceTest',
    component: ProvenanceTest,
  },
]
```

## API 接口

组件内部调用以下后端 API：

### 1. 实体溯源图

```
GET /api/provenance/graph/{entity_id}
```

**请求参数**:

- `entity_id`: 实体ID

**响应格式**:

```json
{
  "success": true,
  "data": {
    "root_entity": {...},
    "nodes": [...],
    "edges": [...],
    "nodes_by_level": {...},
    "total_nodes": 10,
    "total_edges": 15,
    "graph_metadata": {...}
  }
}
```

### 2. 活动溯源图

```
GET /api/provenance/activity-graph/{activity_id}
```

**请求参数**:

- `activity_id`: 活动ID

### 3. 图摘要

```
GET /api/provenance/graph-summary
```

## 数据结构

### 节点 (Node)

```typescript
interface NodeData {
  type: 'entity' | 'activity'
  label: string
  level?: number
  location?: string
  time?: string
  comment?: string
  details?: any
}
```

### 边 (Edge)

```typescript
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
}
```

## 关系类型

组件支持以下关系类型：

1. **used** (使用): 活动使用实体

   - 颜色: #409EFF (蓝色)
   - 标签: "使用"

2. **was_generated_by** (生成): 活动生成实体

   - 颜色: #67C23A (绿色)
   - 标签: "生成"

3. **was_derived_from** (衍生): 实体衍生自另一个实体

   - 颜色: #E6A23C (橙色)
   - 标签: "衍生"

4. **was_informed_by** (通知): 活动被另一个活动通知
   - 颜色: #909399 (灰色)
   - 标签: "通知"

## 节点类型

### 实体节点 (Entity)

- 背景色: #ecf5ff (浅蓝色)
- 边框色: #409eff (蓝色)
- 显示信息: 名称、位置、生成时间、备注

### 活动节点 (Activity)

- 背景色: #f0f9ff (浅绿色)
- 边框色: #67c23a (绿色)
- 显示信息: 名称、开始时间、结束时间、备注

## 交互功能

### 1. 节点点击

点击任意节点可查看详细信息：

- 节点基本信息
- 关系信息
- 相关节点列表

### 2. 图控制

- **缩放**: 使用鼠标滚轮或控制面板
- **平移**: 拖拽画布
- **小地图**: 显示整体视图和当前位置

### 3. 图例

右侧图例显示：

- 节点类型说明
- 关系类型说明
- 当前图信息（节点数、边数、图类型、生成时间）

## 样式定制

### 自定义节点样式

```css
.custom-node.entity {
  border-color: #409eff;
  background: #ecf5ff;
}

.custom-node.activity {
  border-color: #67c23a;
  background: #f0f9ff;
}
```

### 自定义边样式

```css
.edge-line {
  stroke: #409eff;
  stroke-width: 2;
}
```

## 错误处理

组件包含完整的错误处理机制：

1. **输入验证**: 检查 Entity ID 或 Activity ID 是否为空
2. **API 错误**: 显示后端返回的错误信息
3. **网络错误**: 显示网络连接错误提示
4. **加载状态**: 显示加载动画和状态

## 性能优化

1. **按需加载**: 只在用户请求时加载数据
2. **节点位置计算**: 基于层级自动计算节点位置
3. **关系过滤**: 只显示有效的节点关系
4. **内存管理**: 及时清理不需要的数据

## 扩展性

组件设计支持未来扩展：

1. **新的关系类型**: 可以添加新的关系类型和颜色
2. **自定义布局**: 可以修改节点位置计算算法
3. **过滤功能**: 可以添加基于条件的节点和边过滤
4. **导出功能**: 可以添加图片导出功能

## 注意事项

1. **API 依赖**: 需要后端提供相应的 API 接口
2. **数据格式**: 确保后端返回的数据格式符合组件要求
3. **网络连接**: 需要稳定的网络连接来加载数据
4. **浏览器兼容性**: 建议使用现代浏览器以获得最佳体验

## 故障排除

### 常见问题

1. **图不显示**

   - 检查 API 接口是否正常
   - 检查网络连接
   - 查看浏览器控制台错误信息

2. **节点位置异常**

   - 检查节点数据是否包含 level 信息
   - 检查节点位置计算逻辑

3. **关系线不显示**
   - 检查边的 source 和 target 是否正确
   - 检查节点 ID 是否匹配

### 调试方法

1. 打开浏览器开发者工具
2. 查看 Network 标签页的 API 请求
3. 查看 Console 标签页的错误信息
4. 检查 Vue DevTools 中的组件状态
