import json
from datetime import datetime, timedelta

from app import app, db
from models import Action, Project, Workflow, WorkflowTemplate


def insert_test_data():
    """插入测试数据"""

    # 清空现有数据
    Action.query.delete()
    Workflow.query.delete()
    WorkflowTemplate.query.delete()
    Project.query.delete()

    # 创建项目
    project1 = Project(
        name="机器学习项目",
        description=("用于训练和部署机器学习模型的自动化流水线"),
    )

    project2 = Project(
        name="数据ETL项目", description="数据提取、转换和加载的自动化流程"
    )

    project3 = Project(
        name="Web应用部署项目", description=("前端和后端应用的自动化部署流水线")
    )

    db.session.add_all([project1, project2, project3])
    db.session.commit()

    # 创建工作流模板
    ml_template_config = {
        "stages": [
            {
                "name": "数据预处理",
                "type": "data_processing",
                "config": {
                    "input_path": "/data/raw",
                    "output_path": "/data/processed",
                    "preprocessing_steps": ["清洗", "标准化", "特征工程"],
                },
            },
            {
                "name": "模型训练",
                "type": "model_training",
                "config": {
                    "algorithm": "random_forest",
                    "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                    "validation_split": 0.2,
                },
            },
            {
                "name": "模型评估",
                "type": "model_evaluation",
                "config": {
                    "metrics": ["accuracy", "precision", "recall", "f1"],
                    "test_data_path": "/data/test",
                },
            },
            {
                "name": "模型部署",
                "type": "model_deployment",
                "config": {
                    "deployment_target": "production",
                    "api_endpoint": "/api/predict",
                },
            },
        ]
    }

    etl_template_config = {
        "stages": [
            {
                "name": "数据提取",
                "type": "data_extraction",
                "config": {
                    "source": "postgresql",
                    "query": "SELECT * FROM source_table",
                    "batch_size": 1000,
                },
            },
            {
                "name": "数据转换",
                "type": "data_transformation",
                "config": {
                    "transformations": [
                        {"type": "filter", "condition": "status = 'active'"},
                        {
                            "type": "aggregate",
                            "group_by": ["category"],
                            "metrics": ["sum", "avg"],
                        },
                    ]
                },
            },
            {
                "name": "数据加载",
                "type": "data_loading",
                "config": {
                    "target": "data_warehouse",
                    "table_name": "processed_data",
                    "load_strategy": "upsert",
                },
            },
        ]
    }

    deploy_template_config = {
        "stages": [
            {
                "name": "代码构建",
                "type": "build",
                "config": {
                    "build_tool": "docker",
                    "dockerfile_path": "./Dockerfile",
                    "image_name": "myapp:latest",
                },
            },
            {
                "name": "单元测试",
                "type": "testing",
                "config": {
                    "test_framework": "pytest",
                    "test_path": "./tests",
                    "coverage_threshold": 80,
                },
            },
            {
                "name": "部署到测试环境",
                "type": "deployment",
                "config": {
                    "environment": "staging",
                    "deployment_method": "kubernetes",
                    "namespace": "staging",
                },
            },
            {
                "name": "部署到生产环境",
                "type": "deployment",
                "config": {
                    "environment": "production",
                    "deployment_method": "kubernetes",
                    "namespace": "production",
                    "rollback_enabled": True,
                },
            },
        ]
    }

    template1 = WorkflowTemplate(
        name="机器学习流水线",
        description="完整的机器学习模型训练和部署流水线",
        config=ml_template_config,
        project_id=project1.id,
    )

    template2 = WorkflowTemplate(
        name="ETL数据处理流水线",
        description="数据提取、转换和加载的自动化流程",
        config=etl_template_config,
        project_id=project2.id,
    )

    template3 = WorkflowTemplate(
        name="应用部署流水线",
        description="Web应用的自动化构建和部署流程",
        config=deploy_template_config,
        project_id=project3.id,
    )

    db.session.add_all([template1, template2, template3])
    db.session.commit()

    # 创建工作流实例
    now = datetime.utcnow()

    workflow1 = Workflow(
        name="ML模型训练v1.0",
        status="completed",
        template_id=template1.id,
        project_id=project1.id,
        started_at=now - timedelta(hours=2),
        completed_at=now - timedelta(minutes=30),
    )

    workflow2 = Workflow(
        name="ETL每日数据同步",
        status="running",
        template_id=template2.id,
        project_id=project2.id,
        started_at=now - timedelta(minutes=15),
    )

    workflow3 = Workflow(
        name="Web应用部署v2.1",
        status="pending",
        template_id=template3.id,
        project_id=project3.id,
    )

    workflow4 = Workflow(
        name="ML模型训练v1.1",
        status="failed",
        template_id=template1.id,
        project_id=project1.id,
        started_at=now - timedelta(hours=1),
        completed_at=now - timedelta(minutes=45),
    )

    db.session.add_all([workflow1, workflow2, workflow3, workflow4])
    db.session.commit()

    # 为工作流1创建动作节点（已完成）
    action1_1 = Action(
        name="数据预处理",
        type="data_processing",
        status="completed",
        workflow_id=workflow1.id,
        config=json.dumps(
            {
                "input_path": "/data/raw",
                "output_path": "/data/processed",
                "preprocessing_steps": ["清洗", "标准化", "特征工程"],
            }
        ),
        logs="数据预处理完成，处理了10000条记录，生成了15个特征",
        started_at=workflow1.started_at,
        completed_at=workflow1.started_at + timedelta(minutes=20),
    )

    action1_2 = Action(
        name="模型训练",
        type="model_training",
        status="completed",
        workflow_id=workflow1.id,
        config=json.dumps(
            {
                "algorithm": "random_forest",
                "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                "validation_split": 0.2,
            }
        ),
        logs="模型训练完成，准确率达到85.6%，训练时间45分钟",
        started_at=action1_1.completed_at,
        completed_at=action1_1.completed_at + timedelta(minutes=45),
    )

    action1_3 = Action(
        name="模型评估",
        type="model_evaluation",
        status="completed",
        workflow_id=workflow1.id,
        config=json.dumps(
            {
                "metrics": ["accuracy", "precision", "recall", "f1"],
                "test_data_path": "/data/test",
            }
        ),
        logs="模型评估完成：准确率85.6%，精确率87.2%，召回率83.1%，F1分数85.1%",
        started_at=action1_2.completed_at,
        completed_at=action1_2.completed_at + timedelta(minutes=10),
    )

    action1_4 = Action(
        name="模型部署",
        type="model_deployment",
        status="completed",
        workflow_id=workflow1.id,
        config=json.dumps(
            {"deployment_target": "production", "api_endpoint": "/api/predict"}
        ),
        logs="模型已成功部署到生产环境，API端点已激活",
        started_at=action1_3.completed_at,
        completed_at=workflow1.completed_at,
    )

    # 为工作流2创建动作节点（运行中）
    action2_1 = Action(
        name="数据提取",
        type="data_extraction",
        status="completed",
        workflow_id=workflow2.id,
        config=json.dumps(
            {
                "source": "postgresql",
                "query": "SELECT * FROM source_table",
                "batch_size": 1000,
            }
        ),
        logs=("数据提取完成，共提取5000条记录"),
        started_at=workflow2.started_at,
        completed_at=workflow2.started_at + timedelta(minutes=5),
    )

    action2_2 = Action(
        name="数据转换",
        type="data_transformation",
        status="running",
        workflow_id=workflow2.id,
        config=json.dumps(
            {
                "transformations": [
                    {"type": "filter", "condition": "status = 'active'"},
                    {
                        "type": "aggregate",
                        "group_by": ["category"],
                        "metrics": ["sum", "avg"],
                    },
                ]
            }
        ),
        logs="正在进行数据转换，已处理3000条记录...",
        started_at=action2_1.completed_at,
    )

    # 为工作流4创建动作节点（失败）
    action4_1 = Action(
        name="数据预处理",
        type="data_processing",
        status="completed",
        workflow_id=workflow4.id,
        config=json.dumps(
            {
                "input_path": "/data/raw",
                "output_path": "/data/processed",
                "preprocessing_steps": ["清洗", "标准化", "特征工程"],
            }
        ),
        logs="数据预处理完成，处理了8000条记录",
        started_at=workflow4.started_at,
        completed_at=workflow4.started_at + timedelta(minutes=18),
    )

    action4_2 = Action(
        name="模型训练",
        type="model_training",
        status="failed",
        workflow_id=workflow4.id,
        config=json.dumps(
            {
                "algorithm": "random_forest",
                "hyperparameters": {"n_estimators": 100, "max_depth": 10},
                "validation_split": 0.2,
            }
        ),
        logs="模型训练失败：内存不足，无法处理大规模数据集",
        started_at=action4_1.completed_at,
        completed_at=workflow4.completed_at,
    )

    db.session.add_all(
        [
            action1_1,
            action1_2,
            action1_3,
            action1_4,
            action2_1,
            action2_2,
            action4_1,
            action4_2,
        ]
    )
    db.session.commit()

    print("测试数据插入完成！")
    print(f"创建了 {Project.query.count()} 个项目")
    print(f"创建了 {WorkflowTemplate.query.count()} 个工作流模板")
    print(f"创建了 {Workflow.query.count()} 个工作流实例")
    print(f"创建了 {Action.query.count()} 个动作节点")


if __name__ == "__main__":
    with app.app_context():
        insert_test_data()
