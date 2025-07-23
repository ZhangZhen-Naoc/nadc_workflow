from datetime import datetime

from flask import Blueprint, jsonify, request

from app.models import (
    Activity,
    Agent,
    ConfigFile,
    Entity,
    Parameter,
    Used,
    WasAssociatedWith,
    WasAttributedTo,
    WasConfiguredBy,
    WasDerivedFrom,
    WasGeneratedBy,
    WasInformedBy,
)
from app.provenance_graph import ID_BIAS, ProvenanceGraph

bp = Blueprint("provenance", __name__, url_prefix="/api/provenance")


@bp.route("/graph", methods=["GET"])
def get_provenance_graph():
    """
    获取完整的溯源图
    """
    try:
        # 获取所有实体
        entities = Entity.query.all()
        entity_data = []
        for entity in entities:
            entity_info = {
                "id": entity.id,
                "name": entity.name,
                "type": "entity",
                "location": entity.location,
                "generated_at_time": (
                    entity.generated_at_time.isoformat()
                    if entity.generated_at_time
                    else None
                ),
                "comment": entity.comment,
            }
            entity_data.append(entity_info)

        # 获取所有活动
        activities = Activity.query.all()
        activity_data = []
        for activity in activities:
            activity_info = {
                "id": activity.id,
                "name": activity.name,
                "type": "activity",
                "start_time": (
                    activity.start_time.isoformat() if activity.start_time else None
                ),
                "end_time": (
                    activity.end_time.isoformat() if activity.end_time else None
                ),
                "comment": activity.comment,
            }
            activity_data.append(activity_info)

        # 获取所有代理
        agents = Agent.query.all()
        agent_data = []
        for agent in agents:
            agent_info = {
                "id": agent.id,
                "name": agent.name,
                "type": "agent",
                "agent_type": agent.type,
                "role": agent.role,
                "email": agent.email,
                "affiliation": agent.affiliation,
            }
            agent_data.append(agent_info)

        # 获取所有关系
        relationships = []

        # Used关系
        used_relations = Used.query.all()
        for used in used_relations:
            relationships.append(
                {
                    "id": used.id,
                    "type": "used",
                    "source": used.activity_id,
                    "target": used.entity_id,
                    "role": used.role,
                    "time": used.time.isoformat() if used.time else None,
                }
            )

        # WasGeneratedBy关系
        generated_relations = WasGeneratedBy.query.all()
        for generated in generated_relations:
            relationships.append(
                {
                    "id": generated.id,
                    "type": "was_generated_by",
                    "source": generated.activity_id,
                    "target": generated.entity_id,
                    "role": generated.role,
                }
            )

        # WasDerivedFrom关系
        derived_relations = WasDerivedFrom.query.all()
        for derived in derived_relations:
            relationships.append(
                {
                    "id": derived.id,
                    "type": "was_derived_from",
                    "source": derived.source_entity_id,
                    "target": derived.entity_id,
                    "role": derived.role,
                }
            )

        # WasInformedBy关系
        informed_relations = WasInformedBy.query.all()
        for informed in informed_relations:
            relationships.append(
                {
                    "id": informed.id,
                    "type": "was_informed_by",
                    "source": informed.informant_id,
                    "target": informed.informed_id,
                }
            )

        # WasAssociatedWith关系
        associated_relations = WasAssociatedWith.query.all()
        for associated in associated_relations:
            relationships.append(
                {
                    "id": associated.id,
                    "type": "was_associated_with",
                    "source": associated.activity_id,
                    "target": associated.agent_id,
                    "role": associated.role,
                }
            )

        # WasAttributedTo关系
        attributed_relations = WasAttributedTo.query.all()
        for attributed in attributed_relations:
            relationships.append(
                {
                    "id": attributed.id,
                    "type": "was_attributed_to",
                    "source": attributed.entity_id,
                    "target": attributed.agent_id,
                    "role": attributed.role,
                }
            )

        return jsonify(
            {
                "success": True,
                "data": {
                    "entities": entity_data,
                    "activities": activity_data,
                    "agents": agent_data,
                    "relationships": relationships,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/entity/<entity_id>", methods=["GET"])
def get_entity_provenance(entity_id):
    """
    获取特定实体的溯源信息
    """
    try:
        entity: Entity = Entity.query.get(entity_id)
        if not entity:
            return jsonify({"success": False, "error": "实体不存在"}), 404

        # 使用属性获取生成此实体的活动
        generated_activity = entity.generated_by

        # 使用属性获取使用此实体的活动
        used_activities = []
        for activity in entity.used_by:
            used_relation = Used.query.filter_by(
                activity_id=activity.id, entity_id=entity_id
            ).first()
            used_activities.append(
                {
                    "activity": {
                        "id": activity.id,
                        "name": activity.name,
                        "start_time": (
                            activity.start_time.isoformat()
                            if activity.start_time
                            else None
                        ),
                        "end_time": (
                            activity.end_time.isoformat() if activity.end_time else None
                        ),
                    },
                    "role": used_relation.role if used_relation else None,
                    "time": (
                        used_relation.time.isoformat()
                        if used_relation and used_relation.time
                        else None
                    ),
                }
            )

        # 使用属性获取衍生自的实体
        source_entities = []
        for source_entity in entity.derived_from:
            derived_relation = WasDerivedFrom.query.filter_by(
                entity_id=entity_id, source_entity_id=source_entity.id
            ).first()
            source_entities.append(
                {
                    "entity": {
                        "id": source_entity.id,
                        "name": source_entity.name,
                        "location": source_entity.location,
                    },
                    "role": derived_relation.role if derived_relation else None,
                }
            )

        # 使用属性获取衍生出的实体
        target_entities = []
        for target_entity in entity.derived:
            derived_relation = WasDerivedFrom.query.filter_by(
                entity_id=target_entity.id, source_entity_id=entity_id
            ).first()
            target_entities.append(
                {
                    "entity": {
                        "id": target_entity.id,
                        "name": target_entity.name,
                        "location": target_entity.location,
                    },
                    "role": derived_relation.role if derived_relation else None,
                }
            )

        # 获取归因的代理
        attributed_to = WasAttributedTo.query.filter_by(entity_id=entity_id).all()
        agents = []
        for attributed in attributed_to:
            agent = Agent.query.get(attributed.agent_id)
            if agent:
                agents.append(
                    {
                        "agent": {
                            "id": agent.id,
                            "name": agent.name,
                            "type": agent.type,
                            "role": agent.role,
                        },
                        "role": attributed.role,
                    }
                )

        return jsonify(
            {
                "success": True,
                "data": {
                    "entity": {
                        "id": entity.id,
                        "name": entity.name,
                        "location": entity.location,
                        "generated_at_time": (
                            entity.generated_at_time.isoformat()
                            if entity.generated_at_time
                            else None
                        ),
                        "comment": entity.comment,
                    },
                    "generated_by": {
                        "activity": (
                            {
                                "id": generated_activity.id,
                                "name": generated_activity.name,
                                "start_time": (
                                    generated_activity.start_time.isoformat()
                                    if generated_activity.start_time
                                    else None
                                ),
                                "end_time": (
                                    generated_activity.end_time.isoformat()
                                    if generated_activity.end_time
                                    else None
                                ),
                            }
                            if generated_activity
                            else None
                        ),
                        "role": (
                            WasGeneratedBy.query.filter_by(entity_id=entity_id)
                            .first()
                            .role
                            if entity.was_generated_by
                            else None
                        ),
                    },
                    "used_by": used_activities,
                    "derived_from": source_entities,
                    "derived_entities": target_entities,
                    "attributed_to": agents,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/activity/<activity_id>", methods=["GET"])
def get_activity_provenance(activity_id):
    """
    获取特定活动的溯源信息
    """
    try:
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({"success": False, "error": "活动不存在"}), 404

        # 使用属性获取活动使用的实体
        inputs = []
        for entity in activity.used:
            used_relation = Used.query.filter_by(
                activity_id=activity_id, entity_id=entity.id
            ).first()
            inputs.append(
                {
                    "entity": {
                        "id": entity.id,
                        "name": entity.name,
                        "location": entity.location,
                    },
                    "role": used_relation.role if used_relation else None,
                    "time": (
                        used_relation.time.isoformat()
                        if used_relation and used_relation.time
                        else None
                    ),
                }
            )

        # 使用属性获取活动生成的实体
        outputs = []
        for entity in activity.generated:
            generated_relation = WasGeneratedBy.query.filter_by(
                activity_id=activity_id, entity_id=entity.id
            ).first()
            outputs.append(
                {
                    "entity": {
                        "id": entity.id,
                        "name": entity.name,
                        "location": entity.location,
                    },
                    "role": generated_relation.role if generated_relation else None,
                }
            )

        # 使用属性获取依赖的活动
        dependencies = []
        for dep_activity in activity.informants:
            dependencies.append(
                {
                    "id": dep_activity.id,
                    "name": dep_activity.name,
                    "start_time": (
                        dep_activity.start_time.isoformat()
                        if dep_activity.start_time
                        else None
                    ),
                    "end_time": (
                        dep_activity.end_time.isoformat()
                        if dep_activity.end_time
                        else None
                    ),
                }
            )

        # 使用属性获取被依赖的活动
        dependents = []
        for dep_activity in activity.informed:
            dependents.append(
                {
                    "id": dep_activity.id,
                    "name": dep_activity.name,
                    "start_time": (
                        dep_activity.start_time.isoformat()
                        if dep_activity.start_time
                        else None
                    ),
                    "end_time": (
                        dep_activity.end_time.isoformat()
                        if dep_activity.end_time
                        else None
                    ),
                }
            )

        # 获取关联的代理
        associated_agents = WasAssociatedWith.query.filter_by(
            activity_id=activity_id
        ).all()
        agents = []
        for associated in associated_agents:
            agent = Agent.query.get(associated.agent_id)
            if agent:
                agents.append(
                    {
                        "agent": {
                            "id": agent.id,
                            "name": agent.name,
                            "type": agent.type,
                            "role": agent.role,
                        },
                        "role": associated.role,
                    }
                )

        # 获取配置信息
        configurations = WasConfiguredBy.query.filter_by(activity_id=activity_id).all()
        configs = []
        for config in configurations:
            if config.artefact_type == "Parameter" and config.parameter_id:
                param = Parameter.query.get(config.parameter_id)
                if param:
                    configs.append(
                        {"type": "parameter", "name": param.name, "value": param.value}
                    )
            elif config.artefact_type == "ConfigFile" and config.config_file_id:
                config_file = ConfigFile.query.get(config.config_file_id)
                if config_file:
                    configs.append(
                        {
                            "type": "config_file",
                            "name": config_file.name,
                            "location": config_file.location,
                        }
                    )

        return jsonify(
            {
                "success": True,
                "data": {
                    "activity": {
                        "id": activity.id,
                        "name": activity.name,
                        "start_time": (
                            activity.start_time.isoformat()
                            if activity.start_time
                            else None
                        ),
                        "end_time": (
                            activity.end_time.isoformat() if activity.end_time else None
                        ),
                        "comment": activity.comment,
                    },
                    "inputs": inputs,
                    "outputs": outputs,
                    "dependencies": dependencies,
                    "dependents": dependents,
                    "associated_agents": agents,
                    "configurations": configs,
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/search", methods=["GET"])
def search_provenance():
    """
    搜索溯源信息
    """
    try:
        query = request.args.get("q", "")
        entity_type = request.args.get("type", "")

        if not query:
            return jsonify({"success": False, "error": "搜索查询不能为空"}), 400

        results = {"entities": [], "activities": [], "agents": []}

        # 搜索实体
        entities = Entity.query.filter(Entity.name.contains(query)).all()
        for entity in entities:
            if not entity_type or entity_type == "entity":
                results["entities"].append(
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": "entity",
                        "location": entity.location,
                    }
                )

        # 搜索活动
        activities = Activity.query.filter(Activity.name.contains(query)).all()
        for activity in activities:
            if not entity_type or entity_type == "activity":
                results["activities"].append(
                    {
                        "id": activity.id,
                        "name": activity.name,
                        "type": "activity",
                        "start_time": (
                            activity.start_time.isoformat()
                            if activity.start_time
                            else None
                        ),
                    }
                )

        # 搜索代理
        agents = Agent.query.filter(Agent.name.contains(query)).all()
        for agent in agents:
            if not entity_type or entity_type == "agent":
                results["agents"].append(
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "type": "agent",
                        "agent_type": agent.type,
                        "role": agent.role,
                    }
                )

        return jsonify({"success": True, "data": results})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/timeline", methods=["GET"])
def get_provenance_timeline():
    """
    获取溯源时间线
    """
    try:
        # 获取所有有时间信息的实体和活动
        timeline_events = []

        # 添加实体生成事件
        entities = Entity.query.filter(Entity.generated_at_time.isnot(None)).all()
        for entity in entities:
            timeline_events.append(
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": "entity_generated",
                    "time": entity.generated_at_time.isoformat(),
                    "description": f"实体 '{entity.name}' 被生成",
                }
            )

        # 添加活动开始事件
        activities = Activity.query.filter(Activity.start_time.isnot(None)).all()
        for activity in activities:
            timeline_events.append(
                {
                    "id": activity.id,
                    "name": activity.name,
                    "type": "activity_started",
                    "time": activity.start_time.isoformat(),
                    "description": f"活动 '{activity.name}' 开始",
                }
            )

        # 添加活动结束事件
        activities_ended = Activity.query.filter(Activity.end_time.isnot(None)).all()
        for activity in activities_ended:
            timeline_events.append(
                {
                    "id": activity.id,
                    "name": activity.name,
                    "type": "activity_ended",
                    "time": activity.end_time.isoformat(),
                    "description": f"活动 '{activity.name}' 结束",
                }
            )

        # 按时间排序
        timeline_events.sort(key=lambda x: x["time"])

        return jsonify({"success": True, "data": {"timeline": timeline_events}})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/graph/<entity_id>", methods=["GET"])
def get_entity_provenance_graph(entity_id):
    """
    获取特定实体的来源拓扑图
    使用 ProvenanceGraph 生成完整的 DAG 结构
    """
    try:
        # 获取实体
        entity = Entity.query.get(entity_id)
        if not entity:
            return jsonify({"success": False, "error": "实体不存在"}), 404

        # 创建 ProvenanceGraph 实例
        graph = ProvenanceGraph()

        # 生成来源拓扑图
        lineage_data = graph.get_entity_lineage(entity)

        # 格式化返回数据
        formatted_data = {
            "root_entity": lineage_data["root_entity"],
            "nodes": [],
            "edges": [],
            "nodes_by_level": lineage_data["nodes_by_level"],
            "total_nodes": lineage_data["total_nodes"],
            "total_edges": lineage_data["total_edges"],
            "graph_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "graph_type": "provenance_dag",
                "algorithm": "depth_first_traversal_with_topological_sort",
            },
        }

        # 添加节点详细信息
        for level, nodes in lineage_data["nodes_by_level"].items():
            for node in nodes:
                node_id = node["id"]
                node_type = node["type"]

                # 根据节点类型获取详细信息
                if node_type == "entity":
                    entity_obj = Entity.query.get(node_id)
                    if entity_obj:
                        node_detail = {
                            "graph_id": node_id,  # 用于图的连接
                            "id": node_id,  # 用于API检索详细信息
                            "name": node["name"],
                            "type": node_type,
                            "level": level,
                            "details": {
                                "location": entity_obj.location,
                                "generated_at_time": (
                                    entity_obj.generated_at_time.isoformat()
                                    if entity_obj.generated_at_time
                                    else None
                                ),
                                "comment": entity_obj.comment,
                            },
                        }
                elif node_type == "activity":
                    # Activity ID需要减去偏移量来获取原始ID
                    original_activity_id = node_id
                    activity_obj = Activity.query.get(original_activity_id)
                    if activity_obj:
                        node_detail = {
                            "graph_id": node_id + ID_BIAS,  # 用于图的连接（带偏移量）
                            "id": original_activity_id,  # 用于API检索详细信息（原始ID）
                            "name": node["name"],
                            "type": node_type,
                            "level": level,
                            "details": {
                                "start_time": (
                                    activity_obj.start_time.isoformat()
                                    if activity_obj.start_time
                                    else None
                                ),
                                "end_time": (
                                    activity_obj.end_time.isoformat()
                                    if activity_obj.end_time
                                    else None
                                ),
                                "comment": activity_obj.comment,
                            },
                        }
                else:
                    node_detail = {
                        "graph_id": node_id,
                        "id": node_id,
                        "name": node["name"],
                        "type": node_type,
                        "level": level,
                        "details": {},
                    }

                formatted_data["nodes"].append(node_detail)

        # 处理边数据，确保使用正确的graph_id
        for edge in lineage_data["edges"]:
            formatted_edge = {
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "type": edge["type"],
                "role": edge["role"],
            }
            formatted_data["edges"].append(formatted_edge)

        return jsonify({"success": True, "data": formatted_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/activity-graph/<activity_id>", methods=["GET"])
def get_activity_provenance_graph(activity_id):
    """
    获取特定活动的来源拓扑图
    使用 ProvenanceGraph 生成以活动为中心的 DAG 结构
    """
    try:
        # 获取活动
        activity = Activity.query.get(activity_id)
        if not activity:
            return jsonify({"success": False, "error": "活动不存在"}), 404

        # 创建 ProvenanceGraph 实例
        graph = ProvenanceGraph()

        # 生成活动工作流图
        workflow_data = graph.get_activity_workflow(activity)

        # 格式化返回数据
        formatted_data = {
            "root_activity": workflow_data["root_activity"],
            "nodes": [],
            "edges": [],
            "nodes_by_level": workflow_data["nodes_by_level"],
            "total_nodes": workflow_data["total_nodes"],
            "total_edges": workflow_data["total_edges"],
            "graph_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "graph_type": "activity_workflow_dag",
                "algorithm": "depth_first_traversal_with_topological_sort",
            },
        }

        # 添加节点详细信息
        for level, nodes in workflow_data["nodes_by_level"].items():
            for node in nodes:
                node_id = node["id"]
                node_type = node["type"]

                # 根据节点类型获取详细信息
                if node_type == "entity":
                    entity_obj = Entity.query.get(node_id)
                    if entity_obj:
                        node_detail = {
                            "graph_id": node_id,  # 用于图的连接
                            "id": node_id,  # 用于API检索详细信息
                            "name": node["name"],
                            "type": node_type,
                            "level": level,
                            "details": {
                                "location": entity_obj.location,
                                "generated_at_time": (
                                    entity_obj.generated_at_time.isoformat()
                                    if entity_obj.generated_at_time
                                    else None
                                ),
                                "comment": entity_obj.comment,
                            },
                        }
                elif node_type == "activity":
                    # Activity ID需要减去偏移量来获取原始ID
                    original_activity_id = node_id - ID_BIAS
                    activity_obj = Activity.query.get(original_activity_id)
                    if activity_obj:
                        node_detail = {
                            "graph_id": node_id,  # 用于图的连接（带偏移量）
                            "id": original_activity_id,  # 用于API检索详细信息（原始ID）
                            "name": node["name"],
                            "type": node_type,
                            "level": level,
                            "details": {
                                "start_time": (
                                    activity_obj.start_time.isoformat()
                                    if activity_obj.start_time
                                    else None
                                ),
                                "end_time": (
                                    activity_obj.end_time.isoformat()
                                    if activity_obj.end_time
                                    else None
                                ),
                                "comment": activity_obj.comment,
                            },
                        }
                else:
                    node_detail = {
                        "graph_id": node_id,
                        "id": node_id,
                        "name": node["name"],
                        "type": node_type,
                        "level": level,
                        "details": {},
                    }

                formatted_data["nodes"].append(node_detail)

        # 处理边数据，确保使用正确的graph_id
        for edge in workflow_data["edges"]:
            formatted_edge = {
                "source": str(edge["source"]),
                "target": str(edge["target"]),
                "type": edge["type"],
                "role": edge["role"],
            }
            formatted_data["edges"].append(formatted_edge)

        return jsonify({"success": True, "data": formatted_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/graph-summary", methods=["GET"])
def get_provenance_graph_summary():
    """
    获取来源图的统计摘要信息
    """
    try:
        # 获取基本统计信息
        total_entities = Entity.query.count()
        total_activities = Activity.query.count()
        total_agents = Agent.query.count()

        # 获取关系统计
        total_used_relations = Used.query.count()
        total_generated_relations = WasGeneratedBy.query.count()
        total_derived_relations = WasDerivedFrom.query.count()
        total_informed_relations = WasInformedBy.query.count()
        total_associated_relations = WasAssociatedWith.query.count()
        total_attributed_relations = WasAttributedTo.query.count()

        # 获取有生成时间的实体数量
        entities_with_time = Entity.query.filter(
            Entity.generated_at_time.isnot(None)
        ).count()

        # 获取有开始时间的活动数量
        activities_with_start_time = Activity.query.filter(
            Activity.start_time.isnot(None)
        ).count()

        # 获取有结束时间的活动数量
        activities_with_end_time = Activity.query.filter(
            Activity.end_time.isnot(None)
        ).count()

        summary = {
            "entities": {
                "total": total_entities,
                "with_generation_time": entities_with_time,
                "percentage_with_time": (
                    round(entities_with_time / total_entities * 100, 2)
                    if total_entities > 0
                    else 0
                ),
            },
            "activities": {
                "total": total_activities,
                "with_start_time": activities_with_start_time,
                "with_end_time": activities_with_end_time,
                "percentage_with_start_time": (
                    round(activities_with_start_time / total_activities * 100, 2)
                    if total_activities > 0
                    else 0
                ),
                "percentage_with_end_time": (
                    round(activities_with_end_time / total_activities * 100, 2)
                    if total_activities > 0
                    else 0
                ),
            },
            "agents": {"total": total_agents},
            "relationships": {
                "used": total_used_relations,
                "was_generated_by": total_generated_relations,
                "was_derived_from": total_derived_relations,
                "was_informed_by": total_informed_relations,
                "was_associated_with": total_associated_relations,
                "was_attributed_to": total_attributed_relations,
                "total": (
                    total_used_relations
                    + total_generated_relations
                    + total_derived_relations
                    + total_informed_relations
                    + total_associated_relations
                    + total_attributed_relations
                ),
            },
            "graph_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "data_quality": {
                    "entities_with_time_percentage": (
                        round(entities_with_time / total_entities * 100, 2)
                        if total_entities > 0
                        else 0
                    ),
                    "activities_with_time_percentage": (
                        round(activities_with_start_time / total_activities * 100, 2)
                        if total_activities > 0
                        else 0
                    ),
                },
            },
        }

        return jsonify({"success": True, "data": summary})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
