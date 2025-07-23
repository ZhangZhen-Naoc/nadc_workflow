from datetime import datetime
from itertools import product
from typing import List, Optional

from app.models import (
    Activity,
    Entity,
    Used,
    WasDerivedFrom,
    WasGeneratedBy,
    WasInformedBy,
    db,
)


def create_activity(
    name: str,
    informers: List[Activity],
    inputs: List[Entity],
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    comment: Optional[str] = None,
) -> Activity:
    """
    创建活动并建立关系

    Args:
        name: 活动名称
        informers: 通知此活动的活动列表（前置依赖）
        inputs: 作为输入的实体列表
        start_time: 开始时间
        end_time: 结束时间
        comment: 备注信息

    Returns:
        创建的Activity对象
    """
    # 创建活动
    activity = Activity(
        name=name,
        start_time=start_time or datetime.utcnow(),
        end_time=end_time,
        comment=comment,
    )

    # 保存活动
    db.session.add(activity)
    db.session.flush()  # 获取ID

    # 建立WasInformedBy关系（活动间的依赖关系）
    for informer in informers:
        was_informed_by = WasInformedBy(
            informed_id=activity.id,
            informant_id=informer.id,
        )
        db.session.add(was_informed_by)

    # 建立Used关系（活动使用实体作为输入）
    for entity in inputs:
        used = Used(
            activity_id=activity.id,
            entity_id=entity.id,
            time=datetime.utcnow(),
        )
        db.session.add(used)

    db.session.commit()
    return activity


def run(activity: Activity) -> List[Entity]:
    """
    执行活动并生成输出实体

    Args:
        activity: 要执行的活动

    Returns:
        生成的实体列表
    """
    # 更新活动状态为运行中
    pass


def post_run(activity: Activity, outputs: List[Entity]):
    activity.end_time = datetime.utcnow()
    for output in outputs:
        generate = WasGeneratedBy(
            entity_id=output.id,
            activity_id=activity.id,
        )
        db.session.add(generate)
    for input, output in product(activity.used, outputs):
        derive = WasDerivedFrom(
            entity_id=output.id,
            source_entity_id=input.id,
        )
        db.session.add(derive)
    db.session.commit()


def get_activity_provenance(activity_id: str) -> dict:
    """
    获取活动的完整溯源信息

    Args:
        activity_id: 活动ID

    Returns:
        包含溯源信息的字典
    """
    activity = Activity.query.get(activity_id)
    if not activity:
        return {}

    # 获取输入实体
    input_entities = []
    for used_relation in activity.used:
        input_entities.append(
            {
                "entity": used_relation.entity,
                "role": used_relation.role,
                "time": used_relation.time,
            }
        )

    # 获取输出实体
    output_entities = []
    for generated_relation in activity.was_generated_by:
        output_entities.append(
            {"entity": generated_relation.entity, "role": generated_relation.role}
        )

    # 获取依赖的活动
    dependent_activities = []
    for informed_relation in activity.was_informed_by:
        dependent_activities.append(informed_relation.informant_activity)

    # 获取被依赖的活动
    dependent_on_activities = []
    for informed_relation in activity.informed_activities:
        dependent_on_activities.append(informed_relation.informed_activity)

    return {
        "activity": activity,
        "inputs": input_entities,
        "outputs": output_entities,
        "dependencies": dependent_activities,
        "dependents": dependent_on_activities,
    }


def create_entity(
    name: str, location: Optional[str] = None, comment: Optional[str] = None
) -> Entity:
    """
    创建实体

    Args:
        name: 实体名称
        location: 位置信息
        comment: 备注信息

    Returns:
        创建的Entity对象
    """
    entity = Entity(
        name=name,
        location=location,
        generated_at_time=datetime.utcnow(),
        comment=comment,
    )

    db.session.add(entity)
    db.session.commit()
    return entity
