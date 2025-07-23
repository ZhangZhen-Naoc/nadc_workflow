# ProvenanceGraph 来源拓扑图生成器

## 概述

`ProvenanceGraph` 是一个基于 IVOA Provenance 数据模型的 DAG（有向无环图）结构，用于生成数据实体的来源拓扑图。它能够追踪数据实体的完整血统信息，包括数据生成、使用、衍生和信息传递等关系。

## 核心组件

### 1. 数据模型

基于以下核心实体和关系：

- **Entity（实体）**: 数据对象，如数据集、文件等
- **Activity（活动）**: 处理过程，如数据转换、分析等
- **关系类型**:
  - `WasGeneratedBy`: 实体被活动生成
  - `Used`: 活动使用实体
  - `WasDerivedFrom`: 实体衍生自另一个实体
  - `WasInformedBy`: 活动被另一个活动通知

### 2. 图结构

- **GraphNode**: 图节点，包含实体或活动信息
- **GraphEdge**: 图边，表示实体间或活动间的关系
- **NodeType**: 节点类型枚举（ENTITY/ACTIVITY）

## 主要功能

### 1. 构建来源拓扑图

```python
from app.provenance_graph import ProvenanceGraph

# 创建图实例
graph = ProvenanceGraph()

# 根据实体构建图
entity = Entity.query.get(1)  # 从数据库获取实体
graph_data = graph.build_graph(entity)
```

### 2. 获取实体血统信息

```python
# 获取完整的血统信息
lineage_data = graph.get_entity_lineage(entity)

# 返回数据结构
{
    "root_entity": {
        "id": entity.id,
        "name": entity.name,
        "location": entity.location
    },
    "nodes_by_level": {
        0: [{"id": 1, "name": "实体1", "type": "entity", "level": 0}],
        1: [{"id": 2, "name": "活动1", "type": "activity", "level": 1}]
    },
    "edges": [
        {"source": 2, "target": 1, "type": "was_generated_by", "role": "output"}
    ],
    "total_nodes": 2,
    "total_edges": 1
}
```

### 3. 获取活动工作流

```python
# 获取活动的工作流信息
activity = Activity.query.get(1)
workflow_data = graph.get_activity_workflow(activity)
```

## 使用示例

### 基本使用

```python
from app.provenance_graph import ProvenanceGraph
from models import Entity

# 创建图实例
graph = ProvenanceGraph()

# 获取实体
entity = Entity.query.get(1)

# 生成血统图
lineage = graph.get_entity_lineage(entity)

# 打印结果
print(f"根实体: {lineage['root_entity']['name']}")
print(f"总节点数: {lineage['total_nodes']}")
print(f"总边数: {lineage['total_edges']}")

# 按层级显示节点
for level, nodes in lineage['nodes_by_level'].items():
    print(f"层级 {level}:")
    for node in nodes:
        print(f"  - {node['name']} ({node['type']})")
```

### 关系遍历

```python
# 遍历实体的来源关系
def analyze_entity_lineage(entity):
    graph = ProvenanceGraph()
    lineage = graph.get_entity_lineage(entity)

    # 分析生成关系
    generation_edges = [e for e in lineage['edges']
                       if e['type'] == 'was_generated_by']

    # 分析使用关系
    usage_edges = [e for e in lineage['edges']
                  if e['type'] == 'used']

    # 分析衍生关系
    derivation_edges = [e for e in lineage['edges']
                       if e['type'] == 'was_derived_from']

    return {
        'generation': generation_edges,
        'usage': usage_edges,
        'derivation': derivation_edges
    }
```

## 算法说明

### 1. 图构建算法

1. **深度优先遍历**: 从根实体开始，递归遍历所有相关实体和活动
2. **关系映射**: 根据四种基本关系类型构建图边
3. **去重处理**: 避免重复访问已处理的节点

### 2. 层级计算算法

使用**拓扑排序**算法计算节点的层级：

1. 构建邻接表和入度统计
2. 从入度为 0 的节点开始排序
3. 按层级分配节点

### 3. 关系类型

- **was_generated_by**: 活动 → 实体（生成关系）
- **used**: 实体 → 活动（使用关系）
- **was_derived_from**: 源实体 → 目标实体（衍生关系）
- **was_informed_by**: 通知活动 → 被通知活动（信息传递关系）

## 应用场景

1. **数据血统追踪**: 追踪数据从原始来源到最终结果的完整路径
2. **工作流依赖分析**: 分析活动间的依赖关系和执行顺序
3. **来源信息可视化**: 生成可视化的数据流图
4. **数据质量评估**: 基于来源信息评估数据质量
5. **合规性检查**: 验证数据处理过程是否符合规范

## 性能考虑

- **内存使用**: 对于大型图，考虑分批处理或流式处理
- **查询优化**: 使用数据库索引优化关系查询
- **缓存策略**: 对频繁访问的血统信息进行缓存

## 扩展性

该框架支持扩展：

1. **新的关系类型**: 可以添加新的关系类型
2. **自定义节点属性**: 可以为节点添加自定义属性
3. **过滤和筛选**: 可以添加基于条件的节点和边过滤
4. **可视化接口**: 可以集成图形可视化库

## 注意事项

1. 确保数据库中存在相应的实体和关系数据
2. 处理循环依赖的情况（虽然理论上不应该存在）
3. 考虑大数据量时的性能优化
4. 注意内存使用，避免无限递归
