from apiflask import APIBlueprint

import app.models as models
from app.models import Project
from schemas import ProjectListResponse, ProjectSchema

# 创建项目蓝图
bp = APIBlueprint("projects", __name__, tag="项目管理")


@bp.get("/")
@bp.output(ProjectListResponse)
def get_projects():
    """获取项目列表 - 获取所有项目的列表信息"""
    projects = Project.query.all()
    return {"projects": projects, "total": len(projects)}


@bp.post("/")
@bp.input(ProjectSchema)
@bp.output(ProjectSchema, 201)
def create_project(json_data):
    """创建项目 - 创建新的项目"""
    project = Project(**json_data)
    models.db.session.add(project)
    models.db.session.commit()
    return project, 201


@bp.get("/<int:id>/")
@bp.output(ProjectSchema)
def get_project(id):
    """获取单个项目 - 根据ID获取单个项目的详细信息，包含流水线配置列表"""
    project = Project.query.get_or_404(id)
    return project
