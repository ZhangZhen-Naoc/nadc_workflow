"""
ProvenanceGraph 使用示例
"""

from app.provenance_graph import ProvenanceGraph


def demonstrate_provenance_graph():
    """演示 ProvenanceGraph 的使用"""

    print("=== ProvenanceGraph 使用演示 ===\n")

    # 创建 ProvenanceGraph 实例
    graph = ProvenanceGraph()

    print("1. 创建 ProvenanceGraph 实例成功")
    print(f"   初始状态: {len(graph.nodes)} 个节点, {len(graph.edges)} 条边\n")

    # 演示主要方法
    print("2. 主要方法说明:")
    print("   - build_graph(entity): 根据实体构建来源拓扑图")
    print("   - get_entity_lineage(entity): 获取实体的完整血统信息")
    print("   - get_activity_workflow(activity): 获取活动的完整工作流信息")
    print("   - _traverse_entity(entity, level): 遍历实体的来源关系")
    print("   - _traverse_activity(activity, level): 遍历活动的来源关系")
    print("   - _calculate_levels(): 计算节点的层级（拓扑排序）\n")

    # 演示支持的关系类型
    print("3. 支持的关系类型:")
    print("   - was_generated_by: 实体被活动生成")
    print("   - used: 活动使用实体")
    print("   - was_derived_from: 实体衍生自另一个实体")
    print("   - was_informed_by: 活动被另一个活动通知\n")

    # 演示数据结构
    print("4. 数据结构:")
    print("   - GraphNode: 图节点（实体或活动）")
    print("   - GraphEdge: 图边（关系）")
    print("   - NodeType: 节点类型枚举（ENTITY/ACTIVITY）\n")

    print("5. 使用场景:")
    print("   - 数据血统追踪")
    print("   - 工作流依赖分析")
    print("   - 来源信息可视化")
    print("   - 数据质量评估")
    print("   - 合规性检查\n")

    print("ProvenanceGraph 已成功部署到 app 目录下！")
    print("可以通过以下方式导入使用:")
    print("   from app.provenance_graph import ProvenanceGraph")


if __name__ == "__main__":
    demonstrate_provenance_graph()
