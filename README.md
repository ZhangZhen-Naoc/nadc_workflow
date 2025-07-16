# NADC Workflow - 天文数据处理流水线管理系统

## 项目介绍

天文数据处理流水线管理系统，提供流水线配置、实例管理和节点监控功能。

## 模型架构

从大到小： 项目 - 流水线配置 - 流水线实例 - 流水线节点

## 中英文对照表（变量名）：

| 中文       | 英文             | 备注                             |
| ---------- | ---------------- | -------------------------------- |
| 项目       | Project          | 项目名称                         |
| 流水线配置 | WorkflowTemplate | 一个项目包含一组流水线配置       |
| 流水线实例 | Workflow         | 依据流水线配置创建的实例         |
| 流水线节点 | Action           | 一个流水线实例包含的多个执行步骤 |

## 技术栈

### 前端

- Vue 3 + TypeScript
- Element Plus UI 组件库
- Pinia 状态管理
- Vue Router 路由管理
- Axios HTTP 客户端

### 后端

- Flask Python Web 框架
- SQLAlchemy ORM
- SQLite 数据库
- Marshmallow 序列化
- Flask-CORS 跨域支持

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd nadc_workflow
```

### 2. 后端设置

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动后端服务
python app.py
```

后端服务将在 http://localhost:5000 启动

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:5173 启动

## 功能特性

### 流水线配置管理

- ✅ 流水线配置列表展示
- ✅ 搜索流水线配置
- ✅ 创建新流水线配置
- ✅ 编辑流水线配置
- ✅ 删除流水线配置
- ✅ 运行流水线

### 界面特性

- 🎨 现代化 UI 设计
- 📱 响应式布局
- 🔍 实时搜索
- ⚡ 快速操作按钮
- 📊 数据表格展示

## API 接口

### 项目接口

- `GET /` - 获取项目列表
- `POST /` - 创建项目
- `GET /{id}/` - 获取单个项目信息，包含流水线配置列表

### 流水线配置接口

prefix: /api/workflow-template/

- `GET /` - 获取流水线配置列表，可选路径参数：projectId
- `GET /{id}/` - 获取单个流水线配置
- `POST /` - 创建流水线配置
- `PUT /{id}/` - 更新流水线配置
- `DELETE /{id}/` - 删除流水线配置
- `POST /{id}/run` - 运行流水线

### 流水线实例接口

prefix: /api/workflow/

- `GET /` - 获取流水线实例列表
- `GET /{id}/` - 获取单个流水线实例
- `POST /{id}/terminate` - 终止流水线实例
- `POST /{id}/retry` - 重试流水线实例
- `GET /{id}/logs` - 获取流水线实例日志
- `GET /{id}/actions` - 获取流水线实例步骤列表

### 流水线节点接口

prefix: /api/action/

- `GET /{id}/` - 获取流水线节点信息，包括日志等

## 开发说明

### 数据库操作

```bash
# 使用Flask CLI命令
flask init-db    # 初始化数据库
flask seed-data  # 添加示例数据
```

### 前端开发

```bash
npm run dev      # 开发模式
npm run build    # 构建生产版本
npm run preview  # 预览构建结果
npm run lint     # 代码检查
```

## 项目结构

```
nadc_workflow/
├── backend/                 # 后端代码
│   ├── app.py              # Flask应用主文件
│   ├── models.py           # 数据库模型
│   ├── routes.py           # API路由
│   ├── schemas.py          # 数据序列化
│   ├── init_db.py          # 数据库初始化
│   ├── requirements.txt    # Python依赖
│   └── nadc_workflow.db    # SQLite数据库文件
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── components/     # 通用组件
│   │   ├── stores/         # Pinia状态管理
│   │   ├── router/         # 路由配置
│   │   └── assets/         # 静态资源
│   ├── package.json        # Node.js依赖
│   └── vite.config.ts      # Vite配置
└── README.md               # 项目说明
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
