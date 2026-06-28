# InsightOS

InsightOS 是一个面向个人使用的 AI 美股投资研究系统骨架。第一阶段聚焦 AI 相关美股公司，目标是把公司数据、财务计算、产业链位置、估值假设、风险、催化剂和证据链放进同一个研究工作台。

当前首页的单只股票研究入口直接连接 SEC EDGAR / XBRL 在线数据。测试 fixture 只保留在自动化测试和内部开发场景中，不作为页面研究结果展示。

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

如需调用 SEC，请把 `.env` 里的 `SEC_USER_AGENT` 改成可识别的联系信息。FRED 需要把 `FRED_API_KEY` 设置为自己的 key。

2. 启动服务：

```bash
docker compose up --build
```

3. 访问：

- Frontend: http://localhost:3000
- Backend health check: http://localhost:8000/health
- Backend API docs: http://localhost:8000/docs

首页顶部有单只股票研究入口，默认跑 `NVDA`。第一阶段在线股票池对齐 BRD，支持 `NVDA`、`MSFT`、`GOOGL`、`AMZN`、`META`、`AMD`、`AVGO`、`TSM`、`ASML`、`PLTR`。页面会展示 SEC 来源、来源 URL、拉取时间、数据哈希、期间、币种和置信度。

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

这个脚本会清理旧的 `3000` / `8000` 端口进程，然后启动后端和 Next.js 前端。单只股票研究依赖后端在线接口；如果后端没有启动，页面会明确显示在线接口不可用，不会用本地样例替代。

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

### `http://localhost:8000/health` 访问不了

通常是后端服务没有启动，或旧进程占住端口。可以执行：

```bash
bash scripts/start-local.sh
```

然后访问：

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/health

如果后端没有连上，单只股票研究区会明确显示在线接口不可用。请先确认后端服务已经启动，再刷新前端页面。

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

数据库迁移：

```bash
cd backend
alembic upgrade head
```

数据模型和证据链字段说明见 [docs/data-dictionary.md](docs/data-dictionary.md)。

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run typecheck
npm test
```

## API 演示

本地服务启动后可以访问：

- Backend metadata: http://localhost:8000/
- Backend health: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Archetype examples: http://localhost:8000/api/archetypes/examples
- Financial quality API: `POST /api/analysis/financial-quality`
- Single stock research API: `GET /api/research/company/NVDA`
- DCF API: `POST /api/analysis/valuation/dcf`
- Multiple valuation API: `POST /api/analysis/valuation/multiple`
- Reverse DCF API: `POST /api/analysis/valuation/reverse-dcf`
- Quality audit API: `POST /api/analysis/quality/ai-output`
- Agent report API: `POST /api/analysis/agents/research-report`

### 拉取 Apple 基础数据演示

Apple 的 SEC CIK 是 `0000320193`。配置好 `SEC_USER_AGENT` 后，可以用：

```bash
curl http://localhost:8000/api/connectors/sec/company/0000320193/profile
curl http://localhost:8000/api/connectors/sec/company/0000320193/filings
curl http://localhost:8000/api/connectors/sec/company/0000320193/facts
```

这些接口会返回 raw record 结构、来源 URL、拉取时间、source hash，以及 normalized facts。SEC 请求有可识别 User-Agent、缓存、重试和每秒不超过 10 次的限流。

FRED 示例：

```bash
curl http://localhost:8000/api/connectors/fred/series/FEDFUNDS
```

如果没有配置 `FRED_API_KEY`，FRED endpoint 会返回明确错误，而不是伪造数据。

## 研究系统文档

- PRD: [docs/prd.md](docs/prd.md)
- BRD: [docs/BRD.md](docs/BRD.md)
- 数据字典: [docs/data-dictionary.md](docs/data-dictionary.md)
- 公式文档: [docs/formulas.md](docs/formulas.md)
- 行业 archetype JSON schema: [docs/archetype-schema.json](docs/archetype-schema.json)
- Agent JSON schema: [docs/agent-schemas.json](docs/agent-schemas.json)
- 研究质量体系: [docs/research-quality.md](docs/research-quality.md)

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
