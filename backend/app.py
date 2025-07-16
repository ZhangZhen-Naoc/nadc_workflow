import os

from apiflask import APIFlask
from dotenv import load_dotenv

from extensions import cors, db, migrate

# 加载环境变量
load_dotenv()

# 创建APIFlask应用
app = APIFlask(
    __name__,
    title="NADC Workflow API",
    version="1.0.0",
    docs_ui="swagger-ui",
    docs_path="/docs",
)
app.config["DESCRIPTION"] = "NADC工作流管理系统API"

# 配置数据库
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///nadc_workflow.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")

# 初始化扩展
db.init_app(app)
migrate.init_app(app, db)
cors.init_app(app)

# 导入路由
from routes import action_bp, project_bp, workflow_bp, workflow_template_bp

# 注册蓝图
app.register_blueprint(project_bp, url_prefix="/api/projects")
app.register_blueprint(workflow_template_bp, url_prefix="/api/workflow-template")
app.register_blueprint(workflow_bp, url_prefix="/api/workflow")
app.register_blueprint(action_bp, url_prefix="/api/action")


@app.route("/")
def index():
    """根路径 - 获取项目列表"""
    return {"message": "NADC Workflow API", "version": "1.0.0"}


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
