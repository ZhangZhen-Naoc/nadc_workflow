"""
ProvenanceGraph 使用示例
"""

from app.provenance_graph import ProvenanceGraph

from .app.models import (
    Activity,
    Entity,
    Used,
    WasDerivedFrom,
    WasGeneratedBy,
    WasInformedBy,
)


def example_usage():
    """使用示例"""

    # 创建 ProvenanceGraph 实例
    graph = ProvenanceGraph()

    # 假设我们有一个实体
    # entity = Entity.query.get(1)  # 从数据库获取实体

    # 生成来源拓扑图
    # lineage_data = graph.get_entity_lineage(entity)

    # 打印结果
    # print("实体血统信息:")
    # print(f"根实体: {lineage_data['root_entity']}")
    # print(f"总节点数: {lineage_data['total_nodes']}")
    # print(f"总边数: {lineage_data['total_edges']}")

    # 按层级打印节点
    # for level, nodes in lineage_data['nodes_by_level'].items():
    #     print(f"层级 {level}:")
    #     for node in nodes:
    #         print(f"  - {node['name']} ({node['type']})")

    # 打印边关系
    # print("\n边关系:")
    # for edge in lineage_data['edges']:
    #     print(f"  {edge['source']} -> {edge['target']} ({edge['type']})")

    pass


def create_sample_data():
    """创建示例数据用于测试"""

    # 创建实体
    entity1 = Entity(name="原始数据", location="/data/raw")
    entity2 = Entity(name="处理后的数据", location="/data/processed")
    entity3 = Entity(name="最终结果", location="/data/final")

    # 创建活动
    activity1 = Activity(name="数据预处理", start_time="2024-01-01T10:00:00")
    activity2 = Activity(name="数据分析", start_time="2024-01-01T11:00:00")
    activity3 = Activity(name="结果生成", start_time="2024-01-01T12:00:00")

    # 建立关系
    # entity1 被 activity1 使用
    used1 = Used(activity_id=activity1.id, entity_id=entity1.id, role="输入数据")

    # entity2 被 activity1 生成
    generated1 = WasGeneratedBy(
        entity_id=entity2.id, activity_id=activity1.id, role="输出数据"
    )

    # entity2 被 activity2 使用
    used2 = Used(activity_id=activity2.id, entity_id=entity2.id, role="输入数据")

    # entity3 被 activity2 生成
    generated2 = WasGeneratedBy(
        entity_id=entity3.id, activity_id=activity2.id, role="输出数据"
    )

    # entity3 衍生自 entity1
    derived1 = WasDerivedFrom(
        entity_id=entity3.id, source_entity_id=entity1.id, role="源数据"
    )

    # activity2 被 activity1 通知
    informed1 = WasInformedBy(informed_id=activity2.id, informant_id=activity1.id)

    # activity3 被 activity2 通知
    informed2 = WasInformedBy(informed_id=activity3.id, informant_id=activity2.id)

    return {
        "entities": [entity1, entity2, entity3],
        "activities": [activity1, activity2, activity3],
        "relations": [
            used1,
            generated1,
            used2,
            generated2,
            derived1,
            informed1,
            informed2,
        ],
    }


def test_provenance_graph():
    """测试 ProvenanceGraph 功能"""

    # 创建示例数据
    sample_data = create_sample_data()

    # 创建图实例
    graph = ProvenanceGraph()

    # 测试实体血统
    root_entity = sample_data["entities"][2]  # entity3 (最终结果)
    lineage = graph.get_entity_lineage(root_entity)

    print("=== 实体血统测试 ===")
    print(f"根实体: {lineage['root_entity']['name']}")
    print(f"总节点数: {lineage['total_nodes']}")
    print(f"总边数: {lineage['total_edges']}")

    # 按层级显示节点
    for level in sorted(lineage["nodes_by_level"].keys()):
        nodes = lineage["nodes_by_level"][level]
        print(f"\n层级 {level}:")
        for node in nodes:
            print(f"  - {node['name']} ({node['type']})")

    # 显示边关系
    print("\n边关系:")
    for edge in lineage["edges"]:
        source_name = next(
            n["name"]
            for n in lineage["nodes_by_level"].values()
            for n in n
            if n["id"] == edge["source"]
        )
        target_name = next(
            n["name"]
            for n in lineage["nodes_by_level"].values()
            for n in n
            if n["id"] == edge["target"]
        )
        print(f"  {source_name} -> {target_name} ({edge['type']})")

    return lineage


if __name__ == "__main__":
    test_provenance_graph()
