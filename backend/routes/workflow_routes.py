from datetime import datetime

from apiflask import APIBlueprint

import models
from models import Action, Workflow
from schemas import (
    ActionListResponse,
    LogResponse,
    WorkflowListResponse,
    WorkflowSchema,
)

# 创建流水线实例蓝图
bp = APIBlueprint("workflows", __name__, tag="流水线实例")


@bp.get("/")
@bp.output(WorkflowListResponse)
def get_workflows():
    """获取流水线实例列表 - 获取所有流水线实例的列表"""
    workflows = Workflow.query.all()
    return {"workflows": workflows, "total": len(workflows)}


@bp.get("/<int:id>/")
@bp.output(WorkflowSchema)
def get_workflow(id):
    """获取单个流水线实例 - 根据ID获取单个流水线实例的详细信息"""
    workflow = Workflow.query.get_or_404(id)
    return workflow


@bp.post("/<int:id>/terminate")
@bp.output(WorkflowSchema)
def terminate_workflow(id):
    """终止流水线实例 - 终止指定ID的流水线实例"""
    workflow = Workflow.query.get_or_404(id)
    workflow.status = "terminated"
    workflow.completed_at = datetime.utcnow()
    workflow.updated_at = datetime.utcnow()
    models.db.session.commit()

    # TODO: 这里应该停止实际的流水线执行逻辑

    return workflow


@bp.post("/<int:id>/retry")
@bp.output(WorkflowSchema)
def retry_workflow(id):
    """重试流水线实例 - 重试指定ID的流水线实例"""
    workflow = Workflow.query.get_or_404(id)
    workflow.status = "pending"
    workflow.started_at = None
    workflow.completed_at = None
    workflow.updated_at = datetime.utcnow()
    models.db.session.commit()

    # TODO: 这里应该重新启动流水线执行逻辑

    return workflow


@bp.get("/<int:id>/logs")
@bp.output(LogResponse)
def get_workflow_logs(id):
    """获取流水线实例日志 - 获取指定ID的流水线实例的所有日志"""
    actions = Action.query.filter_by(workflow_id=id).all()

    logs = []
    for action in actions:
        if action.logs:
            logs.append(f"[{action.name}] {action.logs}")

    return {"logs": "\n".join(logs), "workflow_id": id}


@bp.get("/<int:id>/actions")
@bp.output(ActionListResponse)
def get_workflow_actions(id):
    """获取流水线实例步骤列表 - 获取指定ID的流水线实例的所有步骤"""
    actions = Action.query.filter_by(workflow_id=id).all()
    return {"actions": actions, "total": len(actions)}
