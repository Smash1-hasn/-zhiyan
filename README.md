# 智言 - AI 智能客服系统

智言是一个面向电商场景的 AI 智能客服系统，具备意图识别、多 Agent 路由、工具调用、人机协同等企业级能力。

## 核心功能

- **多 Agent 架构**：通过意图分类器将用户请求路由到专门的 Agent（订单/售后/通用）
- **工具调用**：查询订单、库存、退换货规则、提交退款
- **人机协同**：高风险操作（退款）需用户二次确认
- **流式输出**：SSE 实现打字机效果
- **上下文记忆**：滑动窗口保留最近 10 轮对话
- **全链路可观测**：管理面板展示调用统计、成功率、Token 成本
- **会话管理**：多会话创建、切换、删除，按日期分组

## 快速启动

### 前置条件

- Docker 与 Docker Compose
- Node.js 18+（仅开发时需要）

### 启动

```bash
# 1. 构建前端
cd frontend && npm install && npm run build && cd ..

# 2. 配置环境变量
# 将 backend/.env.example 复制为 backend/.env，并填写密钥

# 3. 启动所有服务
docker-compose up
```

访问 `http://localhost` 即可使用。

### 开发模式

```bash
# 终端 1：启动后端
cd backend && pip install -r requirements.txt && python app.py

# 终端 2：启动前端
cd frontend && npm install && npm run dev

# 终端 3：启动 MySQL（使用本地或 Docker）
```

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 + Vite + Pinia |
| 后端 | Flask + SQLAlchemy + Flask-Migrate |
| AI | LangChain + DeepSeek API |
| 数据库 | MySQL 8.0 |
| 部署 | Docker Compose (Flask + Nginx + MySQL) |

## 架构

```
用户输入
  → IntentClassifier（意图识别）
    → OrderAgent（查询订单）
    → AfterSalesAgent（售后/退款）→ 需用户确认
    → GeneralAgent（通用对话）
  → SSE 流式输出到前端
  → ToolCallLog（全链路记录）
```

## 截图



## 项目结构

```
zhiyan/
├── backend/
│   ├── api/           # HTTP 接口层
│   ├── ai/            # AI 逻辑层（Agent、工具、意图）
│   ├── models/        # 数据模型
│   └── app.py         # 入口
├── frontend/
│   └── src/
│       ├── views/     # 页面
│       ├── stores/    # 状态管理
│       └── api/       # HTTP 请求
├── docker-compose.yml
└── README.md
```
