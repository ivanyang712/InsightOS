# InsightOS

InsightOS 是一个 AI 投资研究系统骨架。当前版本只包含本地可运行的全栈基础设施，不接入真实市场数据，也不调用外部付费 API。

## 技术栈

- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL
- Cache/Queue: Redis
- Container: Docker Compose

## 本地启动

### 前置条件

本地一键启动依赖 Docker Desktop。请先确认 Docker Desktop 已安装并正在运行。

可以先执行诊断：

```bash
bash scripts/doctor.sh
```

如果看到 `MISS docker`，说明当前机器还没有可用的 Docker 命令，需要先安装并启动 Docker Desktop。

### 启动步骤

1. 准备环境变量：

```bash
cp .env.example .env
```

2. 启动服务：

```bash
docker compose up --build
```

3. 访问：

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs

首页会调用后端 `/health`，展示 API、数据库和 Redis 的健康状态。

### 无 Docker 的本地预览

如果当前机器还没有 Docker Desktop，也可以先启动一个轻量主页预览：

```bash
cd frontend
npm install
npm run preview:local
```

这个预览会打开 `http://localhost:3000` 并调用本地后端 `/health`。完整的 PostgreSQL 和 Redis 仍然需要 Docker Compose。

如果已经安装过本地依赖，也可以用脚本启动后台预览：

```bash
bash scripts/start-local.sh
```

## 常见启动问题

### `docker: command not found`

当前机器没有安装 Docker Desktop，或者安装后终端还没有识别到 Docker 命令。

处理方式：

1. 安装 Docker Desktop for Mac
2. 启动 Docker Desktop
3. 等待状态变成 running
4. 重新打开终端
5. 再执行：

```bash
docker compose up --build
```

### `Cannot connect to the Docker daemon`

Docker Desktop 已安装，但还没有启动，或仍在启动中。打开 Docker Desktop，等它启动完成后重试。

### `docker-compose: command not found`

本项目使用新版命令：

```bash
docker compose up --build
```

注意是 `docker compose`，中间是空格，不是 `docker-compose`。

## 本地检查

Backend:

```bash
cd backend
python -m pip install -e ".[dev]"
ruff check .
mypy app
pytest
```

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm test
```

## 项目结构

```text
.
├── backend
│   ├── app
│   ├── tests
│   ├── Dockerfile
│   └── pyproject.toml
├── docs
│   └── architecture.md
├── frontend
│   ├── app
│   ├── src
│   ├── Dockerfile
│   └── package.json
├── infra
│   └── postgres
├── tests
│   └── README.md
├── .env.example
├── docker-compose.yml
└── README.md
```

## 当前不做

- 不接入真实市场数据
- 不调用外部付费 API
- 不连接券商账户
- 不提供买卖建议、目标价或个性化投资建议
- 不实现自动交易
