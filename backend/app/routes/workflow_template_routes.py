from datetime import datetime

from apiflask import APIBlueprint
from flask import request

import app.models as models
from app.models import Workflow, WorkflowTemplate
from schemas import WorkflowSchema, WorkflowTemplateListResponse, WorkflowTemplateSchema

# 创建流水线配置蓝图
bp = APIBlueprint("workflow_templates", __name__, tag="流水线配置")


@bp.get("/")
@bp.output(WorkflowTemplateListResponse)
def get_workflow_templates():
    """获取流水线配置列表 - 获取流水线配置列表，可选projectId参数"""
    project_id = request.args.get("projectId", type=int)
    query = WorkflowTemplate.query
    if project_id:
        query = query.filter_by(project_id=project_id)

    templates = query.all()
    return {"templates": templates, "total": len(templates)}


@bp.get("/<int:id>/")
@bp.output(WorkflowTemplateSchema)
def get_workflow_template(id):
    """获取单个流水线配置 - 根据ID获取单个流水线配置的详细信息"""
    template = WorkflowTemplate.query.get_or_404(id)
    return template


@bp.post("/")
@bp.input(WorkflowTemplateSchema)
@bp.output(WorkflowTemplateSchema, 201)
def create_workflow_template(data):
    """创建流水线配置 - 创建新的流水线配置"""
    template = WorkflowTemplate(**data)
    models.db.session.add(template)
    models.db.session.commit()
    return template, 201


@bp.put("/<int:id>/")
@bp.input(WorkflowTemplateSchema)
@bp.output(WorkflowTemplateSchema)
def update_workflow_template(id, data):
    """更新流水线配置 - 更新指定ID的流水线配置"""
    template = WorkflowTemplate.query.get_or_404(id)
    for key, value in data.items():
        setattr(template, key, value)
    template.updated_at = datetime.utcnow()
    models.db.session.commit()
    return template


@bp.delete("/<int:id>/")
def delete_workflow_template(id):
    """删除流水线配置 - 删除指定ID的流水线配置"""
    template = WorkflowTemplate.query.get_or_404(id)
    models.db.session.delete(template)
    models.db.session.commit()
    return {"message": "流水线配置删除成功"}, 200


@bp.post("/<int:id>/run")
@bp.output(WorkflowSchema, 201)
def run_workflow(id):
    """运行流水线 - 根据流水线配置创建并运行新的流水线实例"""
    template = WorkflowTemplate.query.get_or_404(id)

    # 创建新的流水线实例
    workflow = Workflow(
        name=(
            f"{template.name}_instance_"
            f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        ),
        template_id=template.id,
        project_id=template.project_id,
        status="pending",
    )
    models.db.session.add(workflow)
    models.db.session.commit()

    # TODO: 这里应该启动实际的流水线执行逻辑

    return workflow, 201
