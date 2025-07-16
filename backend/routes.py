# 导入所有路由蓝图
from routes import action_bp, project_bp, workflow_bp, workflow_template_bp

# 导出所有蓝图供app.py使用
__all__ = [
    "project_bp",
    "workflow_template_bp",
    "workflow_bp",
    "action_bp",
]
