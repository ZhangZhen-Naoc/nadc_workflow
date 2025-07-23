from datetime import datetime

from app.workflow_management import (
    create_activity,
    create_entity,
    get_activity_provenance,
    post_run,
    run,
)


def test_inform(app_context):
    start_activity = create_activity(
        name="test_activity",
        informers=[],
        inputs=[],
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    act1 = create_activity(
        name="act1",
        informers=[start_activity],
        inputs=[],
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    assert act1.informants == [start_activity]
    assert act1.informed == []
    assert start_activity.informed == [act1]
    assert start_activity.informants == []


def test_create_entity(app_context):
    """测试创建实体"""
    entity = create_entity(
        name="test_entity", location="/path/to/entity", comment="测试实体"
    )

    assert entity.name == "test_entity"
    assert entity.location == "/path/to/entity"
    assert entity.comment == "测试实体"
    assert entity.generated_at_time is not None
    assert entity.generated_by is None  # 新创建的实体没有生成活动
    assert entity.used_by == []  # 新创建的实体没有被使用
    assert entity.derived_from == []  # 新创建的实体没有源实体
    assert entity.derived == []  # 新创建的实体没有衍生实体


def test_used(app_context):
    """测试活动与实体的关系"""
    # 创建输入实体
    input_entity1 = create_entity("input1", "/input/1")
    input_entity2 = create_entity("input2", "/input/2")

    # 创建活动，使用这些实体作为输入
    activity = create_activity(
        name="process_activity",
        informers=[],
        inputs=[input_entity1, input_entity2],
        start_time=datetime.now(),
        end_time=datetime.now(),
    )

    # 测试活动的used_entities属性
    assert len(activity.used) == 2
    assert input_entity1 in activity.used
    assert input_entity2 in activity.used

    # 测试实体的using_activities属性
    assert len(input_entity1.used_by) == 1
    assert activity in input_entity1.used_by
    assert len(input_entity2.used_by) == 1
    assert activity in input_entity2.used_by

    # 测试活动还没有生成实体
    assert activity.generated == []


def test_generate(app_context):
    input1 = create_entity("input1", "/input/1")
    input2 = create_entity("input2", "/input/2")
    activity = create_activity(
        name="activity",
        informers=[],
        inputs=[input1, input2],
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    output1 = create_entity("output1", "/output/1")
    output2 = create_entity("output2", "/output/2")

    post_run(activity, [output1, output2])

    assert activity.generated == [output1, output2]
    assert output1.generated_by == activity
    assert output2.generated_by == activity


def test_derive(app_context):
    input1 = create_entity("input1", "/input/1")
    input2 = create_entity("input2", "/input/2")
    activity = create_activity(
        name="activity",
        informers=[],
        inputs=[input1, input2],
        start_time=datetime.now(),
        end_time=datetime.now(),
    )
    output1 = create_entity("output1", "/output/1")
    output2 = create_entity("output2", "/output/2")

    post_run(activity, [output1, output2])

    assert input1.derived == [output1, output2]
    assert input2.derived == [output1, output2]
    assert output1.derived_from == [input1, input2]
    assert output2.derived_from == [input1, input2]
