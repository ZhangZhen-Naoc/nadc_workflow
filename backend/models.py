from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import JSON

from extensions import db


class Project(db.Model):
    """项目模型"""

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联关系
    workflow_templates = db.relationship(
        "WorkflowTemplate", backref="project", lazy=True
    )
    workflows = db.relationship("Workflow", backref="project", lazy=True)


class WorkflowTemplate(db.Model):
    """流水线配置模型"""

    __tablename__ = "workflow_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    config = db.Column(JSON, nullable=False)  # 流水线配置JSON
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联关系
    workflows = db.relationship("Workflow", backref="template", lazy=True)


class Workflow(db.Model):
    """流水线实例模型"""

    __tablename__ = "workflows"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, running, completed, failed, terminated
    template_id = db.Column(
        db.Integer, db.ForeignKey("workflow_templates.id"), nullable=False
    )
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # 关联关系
    actions = db.relationship("Action", backref="workflow", lazy=True)


class Action(db.Model):
    """流水线节点模型"""

    __tablename__ = "actions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 节点类型
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, running, completed, failed
    workflow_id = db.Column(db.Integer, db.ForeignKey("workflows.id"), nullable=False)
    config = db.Column(JSON)  # 节点配置
    logs = db.Column(db.Text)  # 节点日志
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# region ivoa_provenance


# 核心实体类
class Entity(db.Model):
    """实体类（对应文档2.2.1）"""

    __tablename__ = "entity"

    id = db.Column(db.String, primary_key=True, comment="唯一标识符")
    name = db.Column(db.String, nullable=True, comment="人类可读名称")
    location = db.Column(db.String, nullable=True, comment="路径或空间坐标")
    generated_at_time = db.Column(db.DateTime, nullable=True, comment="生成时间")
    invalidated_at_time = db.Column(db.DateTime, nullable=True, comment="失效时间")
    comment = db.Column(db.String, nullable=True, comment="备注信息")

    # 关系定义
    was_generated_by = db.relationship(
        "WasGeneratedBy", backref="entity", uselist=False
    )
    used = db.relationship("Used", backref="entity")
    was_attributed_to = db.relationship("WasAttributedTo", backref="entity")
    was_derived_from = db.relationship(
        "WasDerivedFrom", foreign_keys="WasDerivedFrom.entity_id", backref="entity"
    )
    derived_entities = db.relationship(
        "WasDerivedFrom",
        foreign_keys="WasDerivedFrom.source_entity_id",
        backref="source_entity",
    )
    entity_description_id = db.Column(
        db.String, db.ForeignKey("entity_description.id"), nullable=True
    )
    entity_description = db.relationship("EntityDescription", backref="entities")


class Collection(Entity):
    """集合类（继承自实体，对应文档2.2.1）"""

    __tablename__ = "collection"
    __mapper_args__ = {"polymorphic_identity": "collection"}

    id = db.Column(db.String, db.ForeignKey("entity.id"), primary_key=True)
    members = db.relationship(
        "Entity", secondary="collection_member", backref="collections"
    )


class CollectionMember(db.Model):
    """集合-成员关联表"""

    __tablename__ = "collection_member"
    id = db.Column(db.Integer, primary_key=True)
    collection_id = db.Column(db.String, db.ForeignKey("collection.id"))
    member_id = db.Column(db.String, db.ForeignKey("entity.id"))


class Activity(db.Model):
    """活动类（对应文档2.2.2）"""

    __tablename__ = "activity"

    id = db.Column(db.String, primary_key=True, comment="唯一标识符")
    name = db.Column(db.String, nullable=True, comment="人类可读名称")
    start_time = db.Column(db.DateTime, nullable=False, comment="开始时间")
    end_time = db.Column(db.DateTime, nullable=False, comment="结束时间")
    comment = db.Column(db.String, nullable=True, comment="备注信息")

    # 关系定义
    used = db.relationship("Used", backref="activity")
    was_generated_by = db.relationship("WasGeneratedBy", backref="activity")
    was_associated_with = db.relationship("WasAssociatedWith", backref="activity")
    was_informed_by = db.relationship(
        "WasInformedBy",
        foreign_keys="WasInformedBy.informed_id",
        backref="informed_activity",
    )
    informed_activities = db.relationship(
        "WasInformedBy",
        foreign_keys="WasInformedBy.informant_id",
        backref="informant_activity",
    )
    was_configured_by = db.relationship("WasConfiguredBy", backref="activity")
    activity_description_id = db.Column(
        db.String, db.ForeignKey("activity_description.id"), nullable=True
    )
    activity_description = db.relationship("ActivityDescription", backref="activities")


# 实体-活动关系类
class Used(db.Model):
    """使用关系类（对应文档2.3.1）"""

    __tablename__ = "used"

    id = db.Column(db.String, primary_key=True)
    activity_id = db.Column(db.String, db.ForeignKey("activity.id"), nullable=False)
    entity_id = db.Column(db.String, db.ForeignKey("entity.id"), nullable=False)
    role = db.Column(db.String, nullable=True, comment="实体在活动中的角色")
    time = db.Column(db.DateTime, nullable=True, comment="使用开始时间")

    # 关系定义
    usage_description_id = db.Column(
        db.String, db.ForeignKey("usage_description.id"), nullable=True
    )
    usage_description = db.relationship("UsageDescription", backref="used_relations")


class WasGeneratedBy(db.Model):
    """生成关系类（对应文档2.3.2）"""

    __tablename__ = "was_generated_by"

    id = db.Column(db.String, primary_key=True)
    entity_id = db.Column(db.String, db.ForeignKey("entity.id"), nullable=False)
    activity_id = db.Column(db.String, db.ForeignKey("activity.id"), nullable=False)
    role = db.Column(db.String, nullable=True, comment="实体在活动中的角色")

    # 关系定义
    generation_description_id = db.Column(
        db.String, db.ForeignKey("generation_description.id"), nullable=True
    )
    generation_description = db.relationship(
        "GenerationDescription", backref="generated_relations"
    )


class WasDerivedFrom(db.Model):
    """衍生关系类（对应文档2.3.4）"""

    __tablename__ = "was_derived_from"

    id = db.Column(db.String, primary_key=True)
    entity_id = db.Column(
        db.String, db.ForeignKey("entity.id"), nullable=False, comment="衍生实体"
    )
    source_entity_id = db.Column(
        db.String, db.ForeignKey("entity.id"), nullable=False, comment="源实体"
    )
    role = db.Column(db.String, nullable=True, comment="角色描述")


class WasInformedBy(db.Model):
    """信息传递关系类（对应文档2.3.5）"""

    __tablename__ = "was_informed_by"

    id = db.Column(db.String, primary_key=True)
    informed_id = db.Column(
        db.String, db.ForeignKey("activity.id"), nullable=False, comment="被通知活动"
    )
    informant_id = db.Column(
        db.String, db.ForeignKey("activity.id"), nullable=False, comment="通知活动"
    )


# 代理及关系类
class Agent(db.Model):
    """代理类（对应文档2.4.1）"""

    __tablename__ = "agent"

    id = db.Column(db.String, primary_key=True, comment="唯一标识符")
    name = db.Column(db.String, nullable=False, comment="名称")
    type = db.Column(
        db.Enum("Person", "Organization", "SoftwareAgent", name="agent_type"),
        nullable=False,
        comment="代理类型",
    )
    role = db.Column(db.String, nullable=True, comment="角色")
    comment = db.Column(db.String, nullable=True, comment="备注")
    email = db.Column(db.String, nullable=True, comment="电子邮件")
    affiliation = db.Column(db.String, nullable=True, comment="所属机构")
    url = db.Column(db.String, nullable=True, comment="URL地址")

    # 关系定义
    was_associated_with = db.relationship("WasAssociatedWith", backref="agent")
    was_attributed_to = db.relationship("WasAttributedTo", backref="agent")


class WasAssociatedWith(db.Model):
    """关联关系类（对应文档2.4.2）"""

    __tablename__ = "was_associated_with"

    id = db.Column(db.String, primary_key=True)
    activity_id = db.Column(db.String, db.ForeignKey("activity.id"), nullable=False)
    agent_id = db.Column(db.String, db.ForeignKey("agent.id"), nullable=False)
    role = db.Column(db.String, nullable=True, comment="代理在活动中的角色")


class WasAttributedTo(db.Model):
    """归因关系类（对应文档2.4.3）"""

    __tablename__ = "was_attributed_to"

    id = db.Column(db.String, primary_key=True)
    entity_id = db.Column(db.String, db.ForeignKey("entity.id"), nullable=False)
    agent_id = db.Column(db.String, db.ForeignKey("agent.id"), nullable=False)
    role = db.Column(db.String, nullable=True, comment="代理在实体中的角色")


# 描述类
class ActivityDescription(db.Model):
    """活动描述类（对应文档2.5.1）"""

    __tablename__ = "activity_description"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    version = db.Column(db.String, nullable=True, comment="版本号")
    description = db.Column(db.String, nullable=True, comment="描述")
    docurl = db.Column(db.String, nullable=True, comment="文档URL")
    type = db.Column(db.String, nullable=False, comment="活动类型")
    subtype = db.Column(db.String, nullable=True, comment="活动子类型")

    # 关系定义
    usage_descriptions = db.relationship(
        "UsageDescription", backref="activity_description"
    )
    generation_descriptions = db.relationship(
        "GenerationDescription", backref="activity_description"
    )
    parameter_descriptions = db.relationship(
        "ParameterDescription", backref="activity_description"
    )
    config_file_descriptions = db.relationship(
        "ConfigFileDescription", backref="activity_description"
    )


class EntityDescription(db.Model):
    """实体描述类（对应文档2.5.2）"""

    __tablename__ = "entity_description"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    description = db.Column(db.String, nullable=True, comment="描述")
    docurl = db.Column(db.String, nullable=True, comment="文档URL")
    type = db.Column(db.String, nullable=False, comment="实体类型")


class UsageDescription(db.Model):
    """使用描述类（对应文档2.5.3）"""

    __tablename__ = "usage_description"

    id = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, nullable=False, comment="角色")
    description = db.Column(db.String, nullable=True, comment="描述")
    type = db.Column(db.String, nullable=False, comment="类型")
    multiplicity = db.Column(db.String, nullable=False, comment=" multiplicity")
    activity_description_id = db.Column(
        db.String, db.ForeignKey("activity_description.id"), nullable=False
    )
    entity_description_id = db.Column(
        db.String, db.ForeignKey("entity_description.id"), nullable=True
    )
    entity_description = db.relationship(
        "EntityDescription", backref="usage_descriptions"
    )


class GenerationDescription(db.Model):
    """生成描述类（对应文档2.5.3）"""

    __tablename__ = "generation_description"

    id = db.Column(db.String, primary_key=True)
    role = db.Column(db.String, nullable=False, comment="角色")
    description = db.Column(db.String, nullable=True, comment="描述")
    type = db.Column(db.String, nullable=False, comment="类型")
    multiplicity = db.Column(db.String, nullable=False, comment=" multiplicity")
    activity_description_id = db.Column(
        db.String, db.ForeignKey("activity_description.id"), nullable=False
    )
    entity_description_id = db.Column(
        db.String, db.ForeignKey("entity_description.id"), nullable=True
    )
    entity_description = db.relationship(
        "EntityDescription", backref="generation_descriptions"
    )


# 特定实体类型
class DatasetEntity(Entity):
    """数据集实体（对应文档2.6.1）"""

    __tablename__ = "dataset_entity"
    __mapper_args__ = {"polymorphic_identity": "dataset"}

    id = db.Column(db.String, db.ForeignKey("entity.id"), primary_key=True)
    dataset_description_id = db.Column(
        db.String, db.ForeignKey("dataset_description.id"), nullable=True
    )
    dataset_description = db.relationship(
        "DatasetDescription", backref="dataset_entities"
    )


class DatasetDescription(EntityDescription):
    """数据集描述类（对应文档2.6.1）"""

    __tablename__ = "dataset_description"

    id = db.Column(db.String, db.ForeignKey("entity_description.id"), primary_key=True)
    content_type = db.Column(db.String, nullable=False, comment="内容类型")


class ValueEntity(Entity):
    """值实体（对应文档2.6.2）"""

    __tablename__ = "value_entity"
    __mapper_args__ = {"polymorphic_identity": "value"}

    id = db.Column(db.String, db.ForeignKey("entity.id"), primary_key=True)
    value = db.Column(db.String, nullable=False, comment="值")
    value_description_id = db.Column(
        db.String, db.ForeignKey("value_description.id"), nullable=True
    )
    value_description = db.relationship("ValueDescription", backref="value_entities")


class ValueDescription(EntityDescription):
    """值描述类（对应文档2.6.2）"""

    __tablename__ = "value_description"

    id = db.Column(db.String, db.ForeignKey("entity_description.id"), primary_key=True)
    value_type = db.Column(db.String, nullable=False, comment="值类型")
    unit = db.Column(db.String, nullable=True, comment="单位")
    ucd = db.Column(db.String, nullable=True, comment="UCD")
    utype = db.Column(db.String, nullable=True, comment="UType")


# 活动配置类
class Parameter(db.Model):
    """参数类（对应文档2.7.2）"""

    __tablename__ = "parameter"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    value = db.Column(db.String, nullable=False, comment="值")
    value_entity_id = db.Column(
        db.String, db.ForeignKey("value_entity.id"), nullable=True
    )
    value_entity = db.relationship("ValueEntity", backref="parameters")


class ParameterDescription(db.Model):
    """参数描述类（对应文档2.7.2）"""

    __tablename__ = "parameter_description"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    value_type = db.Column(db.String, nullable=False, comment="值类型")
    description = db.Column(db.String, nullable=True, comment="描述")
    unit = db.Column(db.String, nullable=True, comment="单位")
    ucd = db.Column(db.String, nullable=True, comment="UCD")
    utype = db.Column(db.String, nullable=True, comment="UType")
    min = db.Column(db.String, nullable=True, comment="最小值")
    max = db.Column(db.String, nullable=True, comment="最大值")
    options = db.Column(db.JSON, nullable=True, comment="选项")
    default = db.Column(db.String, nullable=True, comment="默认值")
    activity_description_id = db.Column(
        db.String, db.ForeignKey("activity_description.id"), nullable=False
    )


class ConfigFile(db.Model):
    """配置文件类（对应文档2.7.3）"""

    __tablename__ = "config_file"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    location = db.Column(db.String, nullable=False, comment="位置")
    comment = db.Column(db.String, nullable=True, comment="备注")


class ConfigFileDescription(db.Model):
    """配置文件描述类（对应文档2.7.3）"""

    __tablename__ = "config_file_description"

    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False, comment="名称")
    content_type = db.Column(db.String, nullable=False, comment="内容类型")
    description = db.Column(db.String, nullable=True, comment="描述")
    activity_description_id = db.Column(
        db.String, db.ForeignKey("activity_description.id"), nullable=False
    )


class WasConfiguredBy(db.Model):
    """配置关系类（对应文档2.7.4）"""

    __tablename__ = "was_configured_by"

    id = db.Column(db.String, primary_key=True)
    activity_id = db.Column(db.String, db.ForeignKey("activity.id"), nullable=False)
    artefact_type = db.Column(
        db.Enum("Parameter", "ConfigFile", name="config_artefact_type"), nullable=False
    )
    parameter_id = db.Column(db.String, db.ForeignKey("parameter.id"), nullable=True)
    config_file_id = db.Column(
        db.String, db.ForeignKey("config_file.id"), nullable=True
    )
    parameter = db.relationship("Parameter", backref="configurations")
    config_file = db.relationship("ConfigFile", backref="configurations")


# endregion
