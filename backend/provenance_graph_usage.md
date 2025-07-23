# ProvenanceGraph 打印功能使用指南

## 概述

`ProvenanceGraph` 类提供了多种打印功能，帮助您直观地查看和分析来源拓扑图的结构。这些功能包括基本打印、详细打印、实体血统打印、活动工作流打印等。

## 基本打印功能

### 1. 字符串表示

```python
from provenance_graph import ProvenanceGraph

# 创建图实例
graph = ProvenanceGraph()

# 基本字符串表示
print(graph)  # 输出: ProvenanceGraph(nodes=5, edges=4, entities=3, activities=2)
```

### 2. 节点和边的打印

```python
# 打印单个节点
for node in graph.nodes.values():
    print(node)  # 输出: Entity(1: 原始数据文件)

# 打印单个边
for edge in graph.edges:
    print(edge)  # 输出: 1 --used [input]--> 4
```

## 详细图结构打印

### 基本打印

```python
# 打印图的基本结构
graph.print_graph()
```

输出示例：

```
============================================================
来源拓扑图结构
============================================================
节点总数: 5
  - 实体节点: 3
  - 活动节点: 2
边总数: 4

节点层级结构:
----------------------------------------
层级 0:
  Entity(1: 原始数据文件)

层级 1:
  Entity(2: 清洗后数据)
  Activity(4: 数据清洗)

层级 2:
  Entity(3: 分析报告)
  Activity(5: 数据分析)

边关系:
----------------------------------------
  原始数据文件 --used [input]--> 数据清洗
  数据清洗 --was_generated_by [output]--> 清洗后数据
  清洗后数据 --used [input]--> 数据分析
  数据分析 --was_generated_by [output]--> 分析报告
============================================================
```

### 详细打印

```python
# 打印图的详细信息（包括位置、时间等）
graph.print_graph(detailed=True)
```

输出示例：

```
============================================================
来源拓扑图结构
============================================================
节点总数: 5
  - 实体节点: 3
  - 活动节点: 2
边总数: 4

节点层级结构:
----------------------------------------
层级 0:
  Entity(1: 原始数据文件)

层级 1:
  Entity(2: 清洗后数据)
  Activity(4: 数据清洗)

层级 2:
  Entity(3: 分析报告)
  Activity(5: 数据分析)

边关系:
----------------------------------------
  原始数据文件 --used [input]--> 数据清洗
  数据清洗 --was_generated_by [output]--> 清洗后数据
  清洗后数据 --used [input]--> 数据分析
  数据分析 --was_generated_by [output]--> 分析报告

详细信息:
----------------------------------------
节点详情:
  Entity(1: 原始数据文件) (层级: 0)
    位置: /data/raw/file1.csv

  Entity(2: 清洗后数据) (层级: 1)
    位置: /data/cleaned/file2.csv

  Entity(3: 分析报告) (层级: 2)
    位置: /reports/analysis.pdf

  Activity(4: 数据清洗) (层级: 1)
    开始时间: 2024-01-01 10:00:00
    结束时间: 2024-01-01 11:00:00

  Activity(5: 数据分析) (层级: 2)
    开始时间: 2024-01-01 14:00:00
    结束时间: 2024-01-01 16:00:00
============================================================
```

## 实体血统打印

```python
# 获取并打印实体的血统信息
entity = some_entity  # 您的实体对象
graph.print_entity_lineage(entity)
```

输出示例：

```
============================================================
实体血统: 分析报告 (ID: 3)
============================================================
根实体: 分析报告
位置: /reports/analysis.pdf

血统层级:
----------------------------------------
层级 0:
  📄 分析报告 (entity)

层级 1:
  📄 清洗后数据 (entity)

层级 2:
  📄 原始数据文件 (entity)

关系边:
----------------------------------------
  清洗后数据 --was_derived_from [source]--> 分析报告
  原始数据文件 --was_derived_from [source]--> 清洗后数据

总计: 3 个节点, 2 条边
============================================================
```

## 活动工作流打印

```python
# 获取并打印活动的工作流信息
activity = some_activity  # 您的活动对象
graph.print_activity_workflow(activity)
```

输出示例：

```
============================================================
活动工作流: 数据分析 (ID: 2)
============================================================
根活动: 数据分析
开始时间: 2024-01-01T14:00:00
结束时间: 2024-01-01T16:00:00

工作流层级:
----------------------------------------
层级 0:
  ⚙️ 数据分析 (activity)

层级 1:
  📄 清洗后数据 (entity)

层级 2:
  📄 原始数据文件 (entity)

关系边:
----------------------------------------
  清洗后数据 --used [input]--> 数据分析
  原始数据文件 --was_derived_from [source]--> 清洗后数据

总计: 3 个节点, 2 条边
============================================================
```

## 字典格式转换

```python
# 将图转换为字典格式，便于JSON序列化
graph_dict = graph.to_dict()
print(json.dumps(graph_dict, indent=2, ensure_ascii=False))
```

输出示例：

```json
{
  "nodes": [
    {
      "id": 1,
      "name": "原始数据文件",
      "type": "entity",
      "level": 0,
      "data_type": "Entity"
    },
    {
      "id": 2,
      "name": "清洗后数据",
      "type": "entity",
      "level": 1,
      "data_type": "Entity"
    }
  ],
  "edges": [
    {
      "source": 1,
      "target": 4,
      "type": "used",
      "role": "input"
    }
  ],
  "levels": {
    "1": 0,
    "4": 1,
    "2": 1,
    "5": 2,
    "3": 2
  },
  "statistics": {
    "total_nodes": 5,
    "total_edges": 4,
    "entity_nodes": 3,
    "activity_nodes": 2
  }
}
```

## 使用建议

1. **调试时**: 使用 `graph.print_graph()` 查看基本结构
2. **详细分析**: 使用 `graph.print_graph(detailed=True)` 查看完整信息
3. **实体追踪**: 使用 `graph.print_entity_lineage(entity)` 追踪实体血统
4. **工作流分析**: 使用 `graph.print_activity_workflow(activity)` 分析活动流程
5. **数据导出**: 使用 `graph.to_dict()` 转换为 JSON 格式

## 图标说明

- 📄 : 实体节点
- ⚙️ : 活动节点

## 关系类型

- `used`: 活动使用实体
- `was_generated_by`: 实体由活动生成
- `was_derived_from`: 实体从其他实体衍生
- `was_informed_by`: 活动被其他活动通知
