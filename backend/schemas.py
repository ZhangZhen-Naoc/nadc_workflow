import json

from marshmallow import Schema, fields, validate


class ProjectSchema(Schema):
    """项目模式"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    # created_at = fields.DateTime(dump_only=True)
    # updated_at = fields.DateTime(dump_only=True)


class WorkflowTemplateSchema(Schema):
    """流水线配置模式"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    config = fields.Method("_serialize_config", "_deserialize_config")
    project_id = fields.Int(required=True)
    # created_at = fields.DateTime(dump_only=True)
    # updated_at = fields.DateTime(dump_only=True)

    def _serialize_config(self, obj):
        """序列化config字段"""
        return obj.config

    def _deserialize_config(self, value):
        """反序列化config字段"""
        if value is None:
            return {}
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return {}
        return value


class WorkflowSchema(Schema):
    """流水线实例模式"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    status = fields.Str(
        validate=validate.OneOf(
            ["pending", "running", "completed", "failed", "terminated"]
        )
    )
    template_id = fields.Int(required=True)
    project_id = fields.Int(required=True)
    started_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ActionSchema(Schema):
    """流水线节点模式"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    status = fields.Str(
        validate=validate.OneOf(["pending", "running", "completed", "failed"])
    )
    workflow_id = fields.Int(required=True)
    config = fields.Dict()
    logs = fields.Str(dump_only=True)
    started_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# 响应模式
class ProjectListResponse(Schema):
    """项目列表响应"""

    projects = fields.Nested(ProjectSchema, many=True)
    total = fields.Int()


class WorkflowTemplateListResponse(Schema):
    """流水线配置列表响应"""

    templates = fields.Nested(WorkflowTemplateSchema, many=True)
    total = fields.Int()


class WorkflowListResponse(Schema):
    """流水线实例列表响应"""

    workflows = fields.Nested(WorkflowSchema, many=True)
    total = fields.Int()


class ActionListResponse(Schema):
    """流水线节点列表响应"""

    actions = fields.Nested(ActionSchema, many=True)
    total = fields.Int()


class LogResponse(Schema):
    """日志响应"""

    logs = fields.Str()
    action_id = fields.Int()
    workflow_id = fields.Int()
