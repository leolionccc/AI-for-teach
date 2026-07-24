# ITAI Agent - 人工智能导论课程智能体系统

基于 **FastAPI + Vue 3** 的全栈智能体系统，支持 RAG 知识库问答、在线考试、资料管理等功能，服务于人工智能导论课程教学场景。

---

## 功能特性

- **用户认证**：注册 / 登录 / JWT Token 鉴权
- **智能体管理**：创建与管理课程智能体，支持多模型配置
- **RAG 知识库**：上传文档（PDF / DOCX / PPTX），向量化检索，智能问答
- **资料管理**：课程资料的上传、分类与检索
- **在线考试**：章节管理、考试配置、在线答题、自动评分与报告生成
- **系统日志**：操作日志记录与查看
- **模型配置**：灵活对接大语言模型（默认支持阿里通义千问 DashScope）

---

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 + Vite + Element Plus + Vue Router + Axios |
| **后端** | FastAPI + SQLAlchemy + Pydantic + Uvicorn |
| **数据库** | SQLite（开发/演示） |
| **向量数据库** | ChromaDB |
| **文档解析** | pdfplumber / python-docx / python-pptx |
| **LLM 对接** | DashScope（通义千问）兼容 OpenAI API |
| **部署** | Docker + Docker Compose + Nginx 反向代理 |

---

## 项目结构

```
ITAI agent/
├── backend/                  # 后端服务
│   ├── app/
│   │   ├── api/v1/endpoints/ # API 路由端点
│   │   ├── core/             # 核心配置（数据库、安全、设置）
│   │   ├── models/           # SQLAlchemy 数据模型
│   │   ├── schemas/          # Pydantic 请求/响应模型
│   │   ├── services/         # 业务逻辑层
│   │   ├── rag/              # RAG 向量化模块
│   │   └── utils/            # 工具函数（文件解析等）
│   ├── data/                 # 数据库文件
│   ├── uploads/              # 上传文件存储
│   ├── main.py               # 应用入口
│   ├── requirements.txt      # Python 依赖
│   └── .env                  # 环境变量配置
├── frontend/                 # 前端服务
│   ├── src/
│   │   ├── api/              # API 请求封装
│   │   ├── views/            # 页面组件
│   │   ├── router/           # 路由配置
│   │   └── styles/           # 全局样式
│   ├── nginx.conf            # Nginx 配置（生产）
│   ├── vite.config.js        # Vite 构建配置
│   └── package.json          # Node 依赖
└── docker-compose.yml        # Docker 编排文件
```

---

## 快速开始

### 方式一：Docker 一键部署（推荐）

**前置要求**：安装 [Docker](https://docs.docker.com/get-docker/) 和 [Docker Compose](https://docs.docker.com/compose/install/)

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd "ITAI agent"

# 2. 修改后端环境变量（可选但建议）
# 编辑 backend/.env，修改 JWT_SECRET_KEY 为随机密钥

# 3. 一键启动
docker-compose up -d --build

# 4. 访问
# 前端页面：http://localhost
# 后端 API：http://localhost:8000
```

**停止服务**：
```bash
docker-compose down
```

**清除数据卷**：
```bash
docker-compose down -v
```

---

### 方式二：本地开发部署

#### 后端

**前置要求**：Python 3.11+

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 编辑 .env 文件，设置 DASHSCOPE_API_KEY 等

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端 API 文档启动后访问：`http://localhost:8000/docs`

#### 前端

**前置要求**：Node.js 18+

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器访问：`http://localhost:5173`

> 开发模式下 Vite 已配置 `/api` 代理到后端 `http://127.0.0.1:8000`，无需额外处理跨域。

---

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_ENV` | 运行环境 | `production` |
| `DATABASE_URL` | 数据库连接 | `sqlite:///./data/app.db` |
| `JWT_SECRET_KEY` | JWT 签名密钥（**生产环境务必修改**） | — |
| `JWT_ALGORITHM` | JWT 算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期（分钟） | `1440` |
| `DASHSCOPE_API_KEY` | 阿里通义千问 API Key | — |
| `EMBEDDING_MODEL` | 向量化模型 | `text-embedding-v4` |
| `EMBEDDING_BASE_URL` | Embedding 接口地址 | DashScope 兼容端点 |
| `EMBEDDING_DIMENSION` | 向量维度 | `1024` |
| `BACKEND_CORS_ORIGINS` | CORS 允许的源（逗号分隔） | `http://localhost,...` |

---

## API 概览

所有接口统一前缀 `/api/v1`，主要模块如下：

| 模块 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/v1/auth` | 登录、注册 |
| 用户 | `/api/v1/users` | 用户信息管理 |
| 智能体 | `/api/v1/agents` | 智能体 CRUD 与对话 |
| RAG | `/api/v1/rag` | 知识库文档上传与检索问答 |
| 资料 | `/api/v1/materials` | 课程资料管理 |
| 考试 | `/api/v1/exams` | 考试配置、答题、评分 |
| 模型配置 | `/api/v1/model-configs` | LLM 模型参数管理 |
| 聊天记录 | `/api/v1/chat-history` | 历史对话查询 |
| 系统日志 | `/api/v1/system-logs` | 操作日志 |
| 健康检查 | `/api/v1/health` | 服务健康状态 |

---

## 默认端口

| 服务 | 端口 |
|------|------|
| 前端（Docker） | `80` |
| 前端（开发） | `5173` |
| 后端 | `8000` |

---

## 注意事项

1. **首次启动**会自动初始化数据库和创建表结构
2. **生产部署前**请务必修改 `backend/.env` 中的 `JWT_SECRET_KEY` 为安全的随机字符串
3. **DashScope API Key** 需要在 [阿里云](https://dashscope.console.aliyun.com/) 申请，用于 LLM 对话和文档向量化
4. 上传的文件存储在 `backend/uploads/` 目录，Docker 部署时通过 Volume 持久化
5. 向量数据库（ChromaDB）数据存储在 `backend/data/chroma_db/`，同样通过 Volume 持久化

---

## License

MIT

