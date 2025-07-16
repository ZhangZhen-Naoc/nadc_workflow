from apiflask import APIBlueprint

from models import Action
from schemas import ActionSchema

# 创建流水线节点蓝图
bp = APIBlueprint("actions", __name__, tag="流水线节点")


@bp.get("/<int:id>/")
@bp.output(ActionSchema)
def get_action(id):
    """获取流水线节点信息 - 根据ID获取流水线节点的详细信息，包括日志等"""
    action = Action.query.get_or_404(id)
    return action
