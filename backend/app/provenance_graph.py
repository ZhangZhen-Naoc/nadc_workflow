import os
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

ID_BIAS = 10000000  # 由于activity和entity的id可能重复，所以给activity一个偏移量
from .models import (
    Activity,
    Entity,
    Used,
    WasDerivedFrom,
    WasGeneratedBy,
    WasInformedBy,
)


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


@dataclass
class GraphEdge:
    """图边"""

    source_id: int
    target_id: int
    relationship_type: str
    role: Optional[str] = None


class ProvenanceGraph:
    """来源拓扑图生成器"""

    def __init__(self):
        self.nodes: Dict[int, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.node_levels: Dict[int, int] = {}
        self._visited_entities: Set[int] = set()
        self._visited_activities: Set[int] = set()

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
        if (activity.id + ID_BIAS) not in self._visited_activities:
            node = GraphNode(
                id=activity.id,
                name=activity.name or f"Activity_{activity.id}",
                node_type=NodeType.ACTIVITY,
                data=activity,
                level=level,
            )
            self.nodes[activity.id + ID_BIAS] = node
            self._visited_activities.add(activity.id + ID_BIAS)

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
                source_id=activity.id + ID_BIAS,  # 使用偏移后的Activity ID
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
                target_id=activity.id + ID_BIAS,  # 使用偏移后的Activity ID
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
                source_id=informant_activity.id + ID_BIAS,  # 使用偏移后的Activity ID
                target_id=activity.id + ID_BIAS,  # 使用偏移后的Activity ID
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
