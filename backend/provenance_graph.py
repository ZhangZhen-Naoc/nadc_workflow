from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

from app.models import Activity, Entity, Used, WasInformedBy


class NodeType(Enum):
    """节点类型枚举"""

    ENTITY = "entity"
    ACTIVITY = "activity"


@dataclass
class GraphNode:
    """图节点"""

    id: int
    name: str
    node_type: NodeType
    data: Entity | Activity
    level: int = 0

    def __str__(self) -> str:
        return f"{self.node_type.value.capitalize()}({self.id}: {self.name})"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class GraphEdge:
    """图边"""

    source_id: int
    target_id: int
    relationship_type: str
    role: Optional[str] = None

    def __str__(self) -> str:
        role_info = f" [{self.role}]" if self.role else ""
        return f"{self.source_id} --{self.relationship_type}{role_info}--> {self.target_id}"

    def __repr__(self) -> str:
        return self.__str__()


class ProvenanceGraph:
    """来源拓扑图生成器"""

    def __init__(self):
        self.nodes: Dict[int, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.node_levels: Dict[int, int] = {}
        self._visited_entities: Set[int] = set()
        self._visited_activities: Set[int] = set()

    def __str__(self) -> str:
        """返回图的字符串表示"""
        if not self.nodes:
            return "ProvenanceGraph(empty)"

        node_count = len(self.nodes)
        edge_count = len(self.edges)
        entity_count = sum(
            1 for node in self.nodes.values() if node.node_type == NodeType.ENTITY
        )
        activity_count = sum(
            1 for node in self.nodes.values() if node.node_type == NodeType.ACTIVITY
        )

        return f"ProvenanceGraph(nodes={node_count}, edges={edge_count}, entities={entity_count}, activities={activity_count})"

    def __repr__(self) -> str:
        return self.__str__()

    def print_graph(self, detailed: bool = False) -> None:
        """
        打印图的详细信息

        Args:
            detailed: 是否打印详细信息
        """
        print("=" * 60)
        print("来源拓扑图结构")
        print("=" * 60)

        if not self.nodes:
            print("图为空")
            return

        # 统计信息
        entity_nodes = [
            node for node in self.nodes.values() if node.node_type == NodeType.ENTITY
        ]
        activity_nodes = [
            node for node in self.nodes.values() if node.node_type == NodeType.ACTIVITY
        ]

        print(f"节点总数: {len(self.nodes)}")
        print(f"  - 实体节点: {len(entity_nodes)}")
        print(f"  - 活动节点: {len(activity_nodes)}")
        print(f"边总数: {len(self.edges)}")
        print()

        # 按层级打印节点
        if self.node_levels:
            print("节点层级结构:")
            print("-" * 40)
            max_level = max(self.node_levels.values()) if self.node_levels else 0

            for level in range(max_level + 1):
                level_nodes = [
                    node
                    for node in self.nodes.values()
                    if self.node_levels.get(node.id, 0) == level
                ]
                if level_nodes:
                    print(f"层级 {level}:")
                    for node in level_nodes:
                        print(f"  {node}")
                    print()

        # 打印边信息
        if self.edges:
            print("边关系:")
            print("-" * 40)
            for edge in self.edges:
                source_node = self.nodes.get(edge.source_id)
                target_node = self.nodes.get(edge.target_id)
                source_name = (
                    source_node.name if source_node else f"Node_{edge.source_id}"
                )
                target_name = (
                    target_node.name if target_node else f"Node_{edge.target_id}"
                )
                role_info = f" [{edge.role}]" if edge.role else ""
                print(
                    f"  {source_name} --{edge.relationship_type}{role_info}--> {target_name}"
                )
            print()

        # 详细模式：打印更多信息
        if detailed:
            print("详细信息:")
            print("-" * 40)
            print("节点详情:")
            for node in self.nodes.values():
                level = self.node_levels.get(node.id, 0)
                print(f"  {node} (层级: {level})")
                if hasattr(node.data, "location") and node.data.location:
                    print(f"    位置: {node.data.location}")
                if hasattr(node.data, "start_time") and node.data.start_time:
                    print(f"    开始时间: {node.data.start_time}")
                if hasattr(node.data, "end_time") and node.data.end_time:
                    print(f"    结束时间: {node.data.end_time}")
                print()

        print("=" * 60)

    def print_entity_lineage(self, entity: Entity) -> None:
        """
        打印实体的血统信息

        Args:
            entity: 目标实体
        """
        lineage_data = self.get_entity_lineage(entity)

        print("=" * 60)
        print(f"实体血统: {entity.name} (ID: {entity.id})")
        print("=" * 60)

        print(f"根实体: {lineage_data['root_entity']['name']}")
        if lineage_data["root_entity"]["location"]:
            print(f"位置: {lineage_data['root_entity']['location']}")
        print()

        print("血统层级:")
        print("-" * 40)
        for level, nodes in lineage_data["nodes_by_level"].items():
            print(f"层级 {level}:")
            for node in nodes:
                node_type_icon = "📄" if node["type"] == "entity" else "⚙️"
                print(f"  {node_type_icon} {node['name']} ({node['type']})")
            print()

        print("关系边:")
        print("-" * 40)
        for edge in lineage_data["edges"]:
            source_node = next(
                (
                    n
                    for n in lineage_data["nodes_by_level"].get(0, [])
                    if n["id"] == edge["source"]
                ),
                None,
            )
            target_node = next(
                (
                    n
                    for n in lineage_data["nodes_by_level"].get(0, [])
                    if n["id"] == edge["target"]
                ),
                None,
            )

            source_name = (
                source_node["name"] if source_node else f"Node_{edge['source']}"
            )
            target_name = (
                target_node["name"] if target_node else f"Node_{edge['target']}"
            )
            role_info = f" [{edge['role']}]" if edge["role"] else ""

            print(f"  {source_name} --{edge['type']}{role_info}--> {target_name}")

        print(
            f"\n总计: {lineage_data['total_nodes']} 个节点, {lineage_data['total_edges']} 条边"
        )
        print("=" * 60)

    def print_activity_workflow(self, activity: Activity) -> None:
        """
        打印活动的工作流信息

        Args:
            activity: 目标活动
        """
        workflow_data = self.get_activity_workflow(activity)

        print("=" * 60)
        print(f"活动工作流: {activity.name} (ID: {activity.id})")
        print("=" * 60)

        print(f"根活动: {workflow_data['root_activity']['name']}")
        if workflow_data["root_activity"]["start_time"]:
            print(f"开始时间: {workflow_data['root_activity']['start_time']}")
        if workflow_data["root_activity"]["end_time"]:
            print(f"结束时间: {workflow_data['root_activity']['end_time']}")
        print()

        print("工作流层级:")
        print("-" * 40)
        for level, nodes in workflow_data["nodes_by_level"].items():
            print(f"层级 {level}:")
            for node in nodes:
                node_type_icon = "📄" if node["type"] == "entity" else "⚙️"
                print(f"  {node_type_icon} {node['name']} ({node['type']})")
            print()

        print("关系边:")
        print("-" * 40)
        for edge in workflow_data["edges"]:
            source_node = next(
                (
                    n
                    for n in workflow_data["nodes_by_level"].get(0, [])
                    if n["id"] == edge["source"]
                ),
                None,
            )
            target_node = next(
                (
                    n
                    for n in workflow_data["nodes_by_level"].get(0, [])
                    if n["id"] == edge["target"]
                ),
                None,
            )

            source_name = (
                source_node["name"] if source_node else f"Node_{edge['source']}"
            )
            target_name = (
                target_node["name"] if target_node else f"Node_{edge['target']}"
            )
            role_info = f" [{edge['role']}]" if edge["role"] else ""

            print(f"  {source_name} --{edge['type']}{role_info}--> {target_name}")

        print(
            f"\n总计: {workflow_data['total_nodes']} 个节点, {workflow_data['total_edges']} 条边"
        )
        print("=" * 60)

    def to_dict(self) -> Dict:
        """
        将图转换为字典格式，便于JSON序列化

        Returns:
            图的字典表示
        """
        return {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "level": self.node_levels.get(node.id, 0),
                    "data_type": type(node.data).__name__,
                }
                for node in self.nodes.values()
            ],
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.relationship_type,
                    "role": edge.role,
                }
                for edge in self.edges
            ],
            "levels": self.node_levels,
            "statistics": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "entity_nodes": len(
                    [n for n in self.nodes.values() if n.node_type == NodeType.ENTITY]
                ),
                "activity_nodes": len(
                    [n for n in self.nodes.values() if n.node_type == NodeType.ACTIVITY]
                ),
            },
        }

    def build_graph(self, root_entity: Entity) -> Dict:
        """
        根据根实体构建来源拓扑图

        Args:
            root_entity: 根实体

        Returns:
            包含节点和边的图结构字典
        """
        self.nodes.clear()
        self.edges.clear()
        self.node_levels.clear()
        self._visited_entities.clear()
        self._visited_activities.clear()

        # 从根实体开始构建图
        self._add_entity_node(root_entity, level=0)
        self._traverse_entity(root_entity, level=0)

        # 计算节点层级
        self._calculate_levels()

        return {
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
            "levels": self.node_levels,
        }

    def _add_entity_node(self, entity: Entity, level: int) -> None:
        """添加实体节点"""
        if entity.id not in self._visited_entities:
            node = GraphNode(
                id=entity.id,
                name=entity.name or f"Entity_{entity.id}",
                node_type=NodeType.ENTITY,
                data=entity,
                level=level,
            )
            self.nodes[entity.id] = node
            self._visited_entities.add(entity.id)

    def _add_activity_node(self, activity: Activity, level: int) -> None:
        """添加活动节点"""
        if activity.id not in self._visited_activities:
            node = GraphNode(
                id=activity.id,
                name=activity.name or f"Activity_{activity.id}",
                node_type=NodeType.ACTIVITY,
                data=activity,
                level=level,
            )
            self.nodes[activity.id] = node
            self._visited_activities.add(activity.id)

    def _add_edge(
        self,
        source_id: int,
        target_id: int,
        relationship_type: str,
        role: Optional[str] = None,
    ) -> None:
        """添加边"""
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            relationship_type=relationship_type,
            role=role,
        )
        self.edges.append(edge)

    def _traverse_entity(self, entity: Entity, level: int) -> None:
        """遍历实体的来源关系"""
        # 1. 查找生成该实体的活动
        if entity.generated_by:
            activity = entity.generated_by
            self._add_activity_node(activity, level + 1)
            self._add_edge(
                source_id=activity.id,
                target_id=entity.id,
                relationship_type="was_generated_by",
                role=getattr(entity.was_generated_by, "role", None),
            )

            # 递归遍历活动
            self._traverse_activity(activity, level + 1)

        # 2. 查找该实体的源实体（衍生关系）
        for derived_relation in entity.was_derived_from:
            source_entity = derived_relation.source_entity
            self._add_entity_node(source_entity, level + 1)
            self._add_edge(
                source_id=source_entity.id,
                target_id=entity.id,
                relationship_type="was_derived_from",
                role=derived_relation.role,
            )

            # 递归遍历源实体
            self._traverse_entity(source_entity, level + 1)

    def _traverse_activity(self, activity: Activity, level: int) -> None:
        """遍历活动的来源关系"""
        # 1. 查找该活动使用的实体
        for used_relation in Used.query.filter(Used.activity_id == activity.id).all():
            entity = used_relation.entity
            self._add_entity_node(entity, level + 1)
            self._add_edge(
                source_id=entity.id,
                target_id=activity.id,
                relationship_type="used",
                role=used_relation.role,
            )

            # 递归遍历使用的实体
            self._traverse_entity(entity, level + 1)

        # 2. 查找通知该活动的活动（信息传递关系）
        for informed_relation in WasInformedBy.query.filter(
            WasInformedBy.informed_id == activity.id
        ).all():
            informant_activity = informed_relation.informant
            self._add_activity_node(informant_activity, level + 1)
            self._add_edge(
                source_id=informant_activity.id,
                target_id=activity.id,
                relationship_type="was_informed_by",
            )

            # 递归遍历通知活动
            self._traverse_activity(informant_activity, level + 1)

    def _calculate_levels(self) -> None:
        """计算节点的层级（拓扑排序）"""
        # 构建邻接表和入度
        adjacency = defaultdict(list)
        in_degree = defaultdict(int)

        for edge in self.edges:
            adjacency[edge.source_id].append(edge.target_id)
            in_degree[edge.target_id] += 1

        # 拓扑排序
        queue = deque()
        for node_id in self.nodes:
            if in_degree[node_id] == 0:
                queue.append(node_id)

        level = 0
        while queue:
            level_size = len(queue)
            for _ in range(level_size):
                node_id = queue.popleft()
                self.node_levels[node_id] = level

                # 更新邻接节点的入度
                for neighbor_id in adjacency[node_id]:
                    in_degree[neighbor_id] -= 1
                    if in_degree[neighbor_id] == 0:
                        queue.append(neighbor_id)

            level += 1

    def get_entity_lineage(self, entity: Entity) -> Dict:
        """
        获取实体的完整血统信息

        Args:
            entity: 目标实体

        Returns:
            包含血统信息的字典
        """
        graph_data = self.build_graph(entity)

        # 按层级组织节点
        nodes_by_level = defaultdict(list)
        for node in graph_data["nodes"]:
            level = self.node_levels.get(node.id, 0)
            nodes_by_level[level].append(
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "level": level,
                }
            )

        return {
            "root_entity": {
                "id": entity.id,
                "name": entity.name,
                "location": entity.location,
            },
            "nodes_by_level": dict(nodes_by_level),
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.relationship_type,
                    "role": edge.role,
                }
                for edge in graph_data["edges"]
            ],
            "total_nodes": len(graph_data["nodes"]),
            "total_edges": len(graph_data["edges"]),
        }

    def get_activity_workflow(self, activity: Activity) -> Dict:
        """
        获取活动的完整工作流信息

        Args:
            activity: 目标活动

        Returns:
            包含工作流信息的字典
        """
        # 构建以活动为中心的图
        self.nodes.clear()
        self.edges.clear()
        self.node_levels.clear()
        self._visited_entities.clear()
        self._visited_activities.clear()

        self._add_activity_node(activity, level=0)
        self._traverse_activity(activity, level=0)

        # 计算层级
        self._calculate_levels()

        # 按层级组织节点
        nodes_by_level = defaultdict(list)
        for node in self.nodes.values():
            level = self.node_levels.get(node.id, 0)
            nodes_by_level[level].append(
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.node_type.value,
                    "level": level,
                }
            )

        return {
            "root_activity": {
                "id": activity.id,
                "name": activity.name,
                "start_time": (
                    activity.start_time.isoformat() if activity.start_time else None
                ),
                "end_time": (
                    activity.end_time.isoformat() if activity.end_time else None
                ),
            },
            "nodes_by_level": dict(nodes_by_level),
            "edges": [
                {
                    "source": edge.source_id,
                    "target": edge.target_id,
                    "type": edge.relationship_type,
                    "role": edge.role,
                }
                for edge in self.edges
            ],
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
        }
