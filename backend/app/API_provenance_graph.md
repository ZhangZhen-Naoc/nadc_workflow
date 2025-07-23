# ProvenanceGraph API 文档

## 概述

本文档描述了基于 `ProvenanceGraph` 类的新增 API 端点，用于生成和返回来源拓扑图数据。

## 新增 API 端点

### 1. 获取实体来源图

**端点**: `GET /api/provenance/graph/{entity_id}`

**描述**: 获取特定实体的完整来源拓扑图，使用 `ProvenanceGraph` 生成 DAG 结构。

**参数**:

- `entity_id` (路径参数): 实体 ID

**响应示例**:

```json
{
  "success": true,
  "data": {
    "root_entity": {
      "id": 1,
      "name": "最终数据集",
      "location": "/data/final"
    },
    "nodes": [
      {
        "id": 1,
        "name": "最终数据集",
        "type": "entity",
        "level": 0,
        "details": {
          "location": "/data/final",
          "generated_at_time": "2024-01-01T12:00:00",
          "comment": "处理后的最终数据"
        }
      },
      {
        "id": 2,
        "name": "数据分析活动",
        "type": "activity",
        "level": 1,
        "details": {
          "start_time": "2024-01-01T11:00:00",
          "end_time": "2024-01-01T12:00:00",
          "comment": "数据分析和处理"
        }
      }
    ],
    "edges": [
      {
        "source": 2,
        "target": 1,
        "type": "was_generated_by",
        "role": "output"
      }
    ],
    "nodes_by_level": {
      "0": [{ "id": 1, "name": "最终数据集", "type": "entity", "level": 0 }],
      "1": [{ "id": 2, "name": "数据分析活动", "type": "activity", "level": 1 }]
    },
    "total_nodes": 2,
    "total_edges": 1,
    "graph_metadata": {
      "generated_at": "2024-01-01T12:30:00",
      "graph_type": "provenance_dag",
      "algorithm": "depth_first_traversal_with_topological_sort"
    }
  }
}
```

**错误响应**:

```json
{
  "success": false,
  "error": "实体不存在"
}
```

### 2. 获取活动来源图

**端点**: `GET /api/provenance/activity-graph/{activity_id}`

**描述**: 获取特定活动的来源拓扑图，以活动为中心生成工作流 DAG 结构。

**参数**:

- `activity_id` (路径参数): 活动 ID

**响应示例**:

```json
{
  "success": true,
  "data": {
    "root_activity": {
      "id": 1,
      "name": "数据分析活动",
      "start_time": "2024-01-01T11:00:00",
      "end_time": "2024-01-01T12:00:00"
    },
    "nodes": [
      {
        "id": 1,
        "name": "数据分析活动",
        "type": "activity",
        "level": 0,
        "details": {
          "start_time": "2024-01-01T11:00:00",
          "end_time": "2024-01-01T12:00:00",
          "comment": "数据分析和处理"
        }
      },
      {
        "id": 2,
        "name": "原始数据",
        "type": "entity",
        "level": 1,
        "details": {
          "location": "/data/raw",
          "generated_at_time": "2024-01-01T10:00:00",
          "comment": "原始输入数据"
        }
      }
    ],
    "edges": [
      {
        "source": 2,
        "target": 1,
        "type": "used",
        "role": "input"
      }
    ],
    "nodes_by_level": {
      "0": [
        { "id": 1, "name": "数据分析活动", "type": "activity", "level": 0 }
      ],
      "1": [{ "id": 2, "name": "原始数据", "type": "entity", "level": 1 }]
    },
    "total_nodes": 2,
    "total_edges": 1,
    "graph_metadata": {
      "generated_at": "2024-01-01T12:30:00",
      "graph_type": "activity_workflow_dag",
      "algorithm": "depth_first_traversal_with_topological_sort"
    }
  }
}
```

### 3. 获取图摘要信息

**端点**: `GET /api/provenance/graph-summary`

**描述**: 获取来源图的统计摘要信息，包括实体、活动、代理和关系的数量统计。

**响应示例**:

```json
{
  "success": true,
  "data": {
    "entities": {
      "total": 100,
      "with_generation_time": 85,
      "percentage_with_time": 85.0
    },
    "activities": {
      "total": 50,
      "with_start_time": 45,
      "with_end_time": 40,
      "percentage_with_start_time": 90.0,
      "percentage_with_end_time": 80.0
    },
    "agents": {
      "total": 10
    },
    "relationships": {
      "used": 150,
      "was_generated_by": 100,
      "was_derived_from": 30,
      "was_informed_by": 20,
      "was_associated_with": 80,
      "was_attributed_to": 60,
      "total": 440
    },
    "graph_metadata": {
      "generated_at": "2024-01-01T12:30:00",
      "data_quality": {
        "entities_with_time_percentage": 85.0,
        "activities_with_time_percentage": 90.0
      }
    }
  }
}
```

## 数据结构说明

### 节点 (Node)

```json
{
  "id": 1,
  "name": "节点名称",
  "type": "entity|activity",
  "level": 0,
  "details": {
    // 实体特有字段
    "location": "/path/to/entity",
    "generated_at_time": "2024-01-01T10:00:00",
    "comment": "实体注释",

    // 活动特有字段
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T11:00:00",
    "comment": "活动注释"
  }
}
```

### 边 (Edge)

```json
{
  "source": 1,
  "target": 2,
  "type": "was_generated_by|used|was_derived_from|was_informed_by",
  "role": "output|input|source|..."
}
```

### 关系类型

1. **was_generated_by**: 活动生成实体
2. **used**: 活动使用实体
3. **was_derived_from**: 实体衍生自另一个实体
4. **was_informed_by**: 活动被另一个活动通知

## 使用场景

### 1. 数据血统可视化

```javascript
// 前端调用示例
fetch("/api/provenance/graph/1")
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      // 使用 D3.js 或其他可视化库渲染图
      renderProvenanceGraph(data.data);
    }
  });
```

### 2. 工作流分析

```javascript
// 获取活动工作流
fetch("/api/provenance/activity-graph/1")
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      // 分析活动依赖关系
      analyzeWorkflowDependencies(data.data);
    }
  });
```

### 3. 数据质量评估

```javascript
// 获取数据质量统计
fetch("/api/provenance/graph-summary")
  .then((response) => response.json())
  .then((data) => {
    if (data.success) {
      // 显示数据质量指标
      displayDataQualityMetrics(data.data);
    }
  });
```

## 性能考虑

1. **缓存策略**: 对于频繁访问的图数据，建议实现缓存机制
2. **分页处理**: 对于大型图，考虑实现分页或流式加载
3. **查询优化**: 确保数据库索引优化，特别是外键关系
4. **内存管理**: 对于复杂图结构，注意内存使用情况

## 错误处理

所有端点都包含统一的错误处理：

- **404**: 实体或活动不存在
- **500**: 服务器内部错误
- **400**: 请求参数错误

## 扩展性

该 API 设计支持未来扩展：

1. **过滤参数**: 可以添加基于时间、类型等的过滤
2. **深度限制**: 可以添加遍历深度限制参数
3. **格式选项**: 可以支持不同的输出格式（JSON、GraphML 等）
4. **实时更新**: 可以添加 WebSocket 支持实时图更新
