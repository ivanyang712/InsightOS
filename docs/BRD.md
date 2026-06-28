# BRD｜AI 美股投资研究系统

## 1. 文档信息

**产品名称**：AI Equity Research OS
**暂定产品名**：InsightOS
**版本**：BRD v0.1
**用户**：个人用户，仅供本人投资研究使用
**第一阶段市场范围**：美国上市公司
**第一阶段研究范围**：AI 相关美股公司
**产品性质**：投资研究辅助工具，不是自动交易系统，不提供个性化买卖建议，不执行交易。

---

## 2. 背景与问题

我希望基于 AI 建立一套个人投资分析系统，用来系统化研究美股 AI 相关公司，包括 AI 芯片、云计算、AI 软件、数据中心、半导体设备、AI 应用平台等方向。

目前个人投资研究中存在几个问题：

1. 信息来源分散，包括财报、SEC 文件、公司 IR、新闻、行业报告、宏观数据等。
2. 手工阅读财报和资料效率低。
3. 财务指标计算容易重复劳动。
4. AI 工具可以总结信息，但容易出现幻觉、数据来源不清、数字不可验证的问题。
5. 缺少一个统一的研究工作台，能够把数据、计算、假设、结论和风险放在一起。
6. 对 AI 产业链缺少持续跟踪机制，例如芯片、云厂商、数据中心、软件应用和能源基础设施之间的联动。

因此，我需要开发一个个人使用的 AI 投资研究产品，帮助我快速、结构化、可追溯地分析美股 AI 相关股票。

---

## 3. 产品目标

第一阶段目标：

构建一个可以研究美股 AI 相关公司的个人投研系统。用户输入一个股票代码，例如 NVDA、MSFT、GOOGL、AMZN、META、AMD、AVGO、TSM、ASML、PLTR、SNOW、CRM 等，系统可以自动生成一份结构化研究报告。

报告需要包括：

1. 公司基本信息
2. AI 业务相关性
3. 商业模式分析
4. 财务表现分析
5. 核心指标趋势
6. 估值分析
7. 同业对比
8. 风险与催化剂
9. Bull / Base / Bear 三情景
10. 关键假设
11. 数据来源与证据链
12. AI 投资研究备忘录

产品不追求第一版覆盖所有公司和所有市场，而是先把“美股 AI 相关股票研究”做深做稳。

---

## 4. 目标用户

第一阶段只有一个用户：我本人。

用户特征：

1. 有一定投资兴趣，希望研究美股 AI 产业机会。
2. 不是专业基金经理，但希望用机构化方式做研究。
3. 希望 AI 提高研究效率，但不希望 AI 编造数据。
4. 更关注中长期产业趋势、公司质量、估值和风险，而不是短线交易。
5. 希望产品未来可以扩展到更多公司、行业和市场。

---

## 5. 产品定位

InsightOS 是一个个人 AI 投资研究工作台。

它不是普通聊天机器人，而是一个结合数据、财务模型、估值引擎、AI 分析和证据链的研究系统。

核心定位：

> 输入一个美股 AI 相关股票代码，系统自动生成一份有数据、有逻辑、有估值、有风险、有来源的公司研究报告。

---

## 6. 第一阶段研究范围

### 6.1 支持市场

第一阶段仅支持：

* 美股上市公司
* ADR 公司，如果数据可通过 SEC 或公开渠道获取，也可以支持
* AI 产业链相关公司

暂不支持：

* A 股
* 港股
* 私募公司
* 非上市公司
* 加密货币
* ETF 深度分析
* 期权策略
* 自动交易

---

### 6.2 AI 相关股票范围

第一阶段重点覆盖以下类别：

#### 1. AI 芯片与半导体

示例公司：

* NVIDIA
* AMD
* Broadcom
* Intel
* Qualcomm
* Marvell
* Arm
* Micron
* TSMC
* ASML
* Applied Materials
* Lam Research
* KLA

#### 2. 云计算与 AI 基础设施

示例公司：

* Microsoft
* Amazon
* Alphabet
* Oracle
* Meta

#### 3. AI 软件与应用

示例公司：

* Palantir
* Salesforce
* ServiceNow
* Adobe
* Snowflake
* Datadog
* MongoDB
* CrowdStrike

#### 4. 数据中心与基础设施

示例公司：

* Super Micro Computer
* Dell
* Vertiv
* Eaton
* Digital Realty
* Equinix

#### 5. AI 产业相关能源与电力基础设施

第一阶段可以先做简单观察，不做深度电力模型。

示例公司：

* GE Vernova
* Constellation Energy
* Vistra
* NRG Energy

---

## 7. 第一阶段 MVP 范围

### 7.1 MVP 必须实现的功能

MVP 只需要实现以下核心功能：

1. 用户输入股票代码。
2. 系统识别公司基本信息。
3. 系统拉取或导入公司财务数据。
4. 系统计算核心财务指标。
5. 系统判断公司与 AI 产业链的相关性。
6. 系统生成公司研究报告。
7. 系统生成风险与催化剂列表。
8. 系统输出 Bull / Base / Bear 三种情景。
9. 系统展示引用来源。
10. 系统保存研究历史。

---

### 7.2 MVP 不做的功能

第一版明确不做：

1. 不做自动交易。
2. 不做买入、卖出、持有建议。
3. 不做个性化资产配置建议。
4. 不接券商账户。
5. 不做实时行情交易。
6. 不做复杂组合管理。
7. 不做手机 App。
8. 不做多人协作。
9. 不做付费订阅。
10. 不做社交分享。
11. 不做预测股价短期涨跌。
12. 不承诺投资收益。

---

## 8. 核心业务流程

### 8.1 公司研究流程

用户输入：

```text
NVDA
```

系统流程：

1. 识别股票代码和公司名称。
2. 判断公司是否属于 AI 相关股票。
3. 获取公司基本信息。
4. 获取最近 5 年财务数据。
5. 获取最近财报和 10-K / 10-Q 信息。
6. 计算核心财务指标。
7. 识别 AI 业务相关内容。
8. 识别增长驱动因素。
9. 识别主要风险。
10. 进行估值分析。
11. 生成 Bull / Base / Bear 情景。
12. 生成公司研究报告。
13. 保存报告和关键假设。
14. 前端展示结果。

---

### 8.2 研究报告输出结构

每份公司研究报告必须包含：

1. 一页摘要
2. 公司基本信息
3. AI 相关性判断
4. 商业模式
5. 收入结构
6. 行业位置
7. 竞争格局
8. 财务趋势
9. 核心指标
10. 估值分析
11. Bull / Base / Bear 情景
12. 风险因素
13. 催化剂
14. 关键假设
15. 未解决问题
16. 数据来源与引用
17. 研究结论更新记录

---

## 9. 功能需求

## 9.1 股票查询功能

用户可以输入美股代码或公司名称。

示例：

```text
NVDA
NVIDIA
MSFT
Microsoft
PLTR
Palantir
```

系统需要返回：

1. 公司名称
2. 股票代码
3. 交易所
4. 行业
5. 公司简介
6. 是否属于 AI 相关公司
7. AI 产业链分类

---

## 9.2 AI 产业链分类功能

系统需要将公司归类到一个或多个 AI 产业链位置。

分类包括：

1. AI 芯片
2. 半导体制造
3. 半导体设备
4. 云计算
5. 数据中心
6. AI 软件
7. 企业 AI 应用
8. 数据基础设施
9. 网络安全
10. 电力与能源基础设施
11. 终端设备
12. 其他

输出示例：

```json
{
  "ticker": "NVDA",
  "company": "NVIDIA",
  "ai_categories": ["AI 芯片", "数据中心", "AI 软件生态"],
  "ai_relevance_score": 95,
  "reason": "公司数据中心 GPU 和 AI 加速器业务是 AI 基础设施核心组成部分。"
}
```

---

## 9.3 财务数据功能

系统需要支持最近 5 年核心财务数据，包括：

1. Revenue
2. Gross Profit
3. Operating Income
4. Net Income
5. Operating Cash Flow
6. Capital Expenditure
7. Free Cash Flow
8. Cash and Equivalents
9. Total Debt
10. Total Assets
11. Total Liabilities
12. Shareholders' Equity
13. Diluted Shares
14. EPS

每个财务数字必须包含：

1. 公司
2. 股票代码
3. 财年
4. 财季，如果有
5. 币种
6. 单位
7. 来源
8. 获取时间
9. 原始字段名称
10. 数据可信度

---

## 9.4 财务指标计算功能

系统需要计算以下指标：

### 增长指标

1. Revenue Growth
2. Gross Profit Growth
3. Operating Income Growth
4. Net Income Growth
5. Free Cash Flow Growth

### 盈利能力

1. Gross Margin
2. Operating Margin
3. Net Margin
4. Free Cash Flow Margin
5. ROE
6. ROIC

### 现金流质量

1. Operating Cash Flow / Net Income
2. Free Cash Flow / Net Income
3. Capital Expenditure / Revenue

### 资产负债

1. Debt / Equity
2. Net Debt
3. Net Debt / EBITDA
4. Current Ratio

### 股东回报

1. EPS Growth
2. Share Dilution
3. Buyback Trend

所有指标必须由 Python 计算，不允许由 LLM 直接生成。

---

## 9.5 估值分析功能

第一阶段支持以下估值方法：

1. PE
2. PS
3. EV / EBITDA
4. EV / FCF
5. 简化 DCF
6. Reverse DCF
7. Bull / Base / Bear 情景估值

估值结果必须展示：

1. 当前估值倍数
2. 历史区间
3. 同业对比
4. 核心假设
5. 敏感性分析
6. 估值风险

系统不能输出“应该买入”或“应该卖出”。

可以输出：

```text
当前估值对未来收入增长和利润率假设较敏感。
如果未来三年收入增长低于基准情景，当前估值的安全边际可能不足。
```

---

## 9.6 AI 研究报告生成功能

系统需要基于已有数据生成研究报告。

AI 可以做：

1. 总结财报内容
2. 解释财务趋势
3. 识别风险
4. 识别催化剂
5. 生成对比分析
6. 生成开放问题
7. 生成研究备忘录

AI 不可以做：

1. 编造财务数字
2. 编造新闻
3. 编造来源
4. 编造估值
5. 直接给出买入或卖出建议
6. 承诺收益
7. 把假设说成事实

---

## 9.7 风险识别功能

系统需要识别以下类型风险：

1. 估值过高风险
2. 收入增长放缓风险
3. 毛利率下降风险
4. 客户集中度风险
5. 供应链风险
6. 地缘政治风险
7. 监管风险
8. 技术替代风险
9. 资本开支过高风险
10. 现金流质量下降风险
11. 股权稀释风险
12. AI 泡沫风险
13. 竞争加剧风险

每个风险需要包含：

1. 风险名称
2. 风险描述
3. 影响程度
4. 发生可能性
5. 监控指标
6. 数据来源
7. 是否需要人工确认

---

## 9.8 催化剂识别功能

系统需要识别潜在催化剂，包括：

1. 新产品发布
2. 财报超预期
3. AI 需求增长
4. 云资本开支增加
5. 数据中心建设加速
6. 毛利率改善
7. 大客户订单
8. 监管改善
9. 行业周期复苏
10. 估值修复

每个催化剂需要包含：

1. 催化剂名称
2. 相关公司
3. 影响逻辑
4. 时间范围
5. 证据来源
6. 不确定性

---

## 9.9 同业比较功能

第一阶段需要支持简单同业比较。

示例：

```text
NVDA vs AMD vs AVGO
MSFT vs GOOGL vs AMZN
PLTR vs SNOW vs CRM
```

比较维度：

1. Revenue Growth
2. Gross Margin
3. Operating Margin
4. Free Cash Flow Margin
5. ROIC
6. PE
7. PS
8. EV / EBITDA
9. AI Relevance Score
10. Risk Score

输出形式：

1. 表格
2. 雷达图，后续版本实现
3. AI 总结
4. 优势与劣势

---

## 9.10 研究历史功能

系统需要保存每次研究结果。

每条研究记录包含：

1. 股票代码
2. 公司名称
3. 研究时间
4. 使用的数据版本
5. 使用的估值假设
6. AI 生成报告
7. 风险清单
8. 催化剂清单
9. 用户备注

未来用户再次研究同一公司时，系统可以显示：

1. 上次研究时间
2. 结论变化
3. 财务数据变化
4. 估值假设变化
5. 风险变化

---

## 10. 页面需求

## 10.1 Dashboard 首页

首页显示：

1. 搜索框
2. 常用 AI 股票列表
3. 最近研究的公司
4. Watchlist
5. AI 产业链分类
6. 最近生成的研究报告

---

## 10.2 Company Research Page

公司研究页显示：

1. 公司名称与股票代码
2. AI 产业链分类
3. AI 相关性评分
4. 一页摘要
5. 财务指标趋势
6. 估值分析
7. 风险列表
8. 催化剂列表
9. Bull / Base / Bear 情景
10. 研究报告正文
11. 来源与引用

---

## 10.3 Compare Page

公司对比页显示：

1. 多个公司选择框
2. 指标对比表
3. 估值对比表
4. AI 相关性对比
5. 风险对比
6. AI 总结

---

## 10.4 Report Page

研究报告页显示：

1. 报告标题
2. 生成时间
3. 公司信息
4. 报告正文
5. 关键数据
6. 估值假设
7. 风险与催化剂
8. 来源列表
9. 导出按钮，后续版本支持 PDF 或 Markdown

---

## 11. 数据来源需求

第一阶段优先使用以下数据来源：

1. SEC EDGAR filings
2. SEC XBRL company facts
3. 公司 Investor Relations 页面
4. 公司 10-K
5. 公司 10-Q
6. 公司 earnings release
7. 公司 investor presentation
8. FRED 宏观数据，后续版本接入
9. 用户手工上传文件，后续版本接入
10. 合规市场数据 API，后续版本接入

系统必须保存数据来源信息。

每个外部数据点都要包含：

1. source_name
2. source_url
3. published_at
4. retrieved_at
5. fiscal_period
6. currency
7. unit
8. confidence_score

---

## 12. 数据质量要求

系统必须处理以下问题：

1. 数据缺失
2. 财年不一致
3. 单位不一致
4. 币种不一致
5. 同一指标多个来源冲突
6. 公司名称和股票代码不匹配
7. 数据过期
8. 财务字段映射错误

遇到无法确认的数据时，系统必须显示：

```text
该数据暂无法可靠确认，需要人工复核。
```

而不是猜测。

---

## 13. AI Agent 需求

第一阶段只需要 4 个 Agent。

## 13.1 Company Research Agent

职责：

1. 分析公司业务
2. 判断 AI 相关性
3. 总结增长驱动
4. 识别竞争优势
5. 输出公司研究正文

---

## 13.2 Financial Analyst Agent

职责：

1. 解释财务趋势
2. 分析收入增长质量
3. 分析利润率变化
4. 分析现金流质量
5. 识别财务异常

---

## 13.3 Valuation Agent

职责：

1. 整理估值假设
2. 解释估值结果
3. 输出 Bull / Base / Bear 情景
4. 分析估值敏感性

估值计算必须由 Python 完成，Agent 只负责解释。

---

## 13.4 Risk Auditor Agent

职责：

1. 检查报告是否出现无来源结论
2. 检查是否有编造数字
3. 检查是否把假设写成事实
4. 检查是否遗漏重大风险
5. 检查是否出现买卖建议
6. 标记低置信度内容
7. 输出审计结果

---

## 14. 技术建议

建议技术栈：

1. Frontend：Next.js + TypeScript
2. Backend：FastAPI + Python
3. Database：PostgreSQL
4. ORM：SQLAlchemy
5. Migration：Alembic
6. Data Processing：Pandas
7. AI：OpenAI API 或兼容 LLM API
8. Background Jobs：Celery 或 RQ
9. Cache：Redis
10. Container：Docker Compose

---

## 15. 建议项目结构

```text
insightos/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── connectors/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── valuation/
│   │   ├── financials/
│   │   └── main.py
│   ├── tests/
│   └── pyproject.toml
├── docs/
│   ├── BRD.md
│   ├── PRD.md
│   ├── DATA_DICTIONARY.md
│   └── FORMULAS.md
├── infra/
│   └── docker-compose.yml
├── .env.example
├── AGENTS.md
└── README.md
```

---

## 16. 数据库实体建议

第一阶段需要以下核心数据表：

1. companies
2. securities
3. financial_facts
4. financial_metrics
5. filings
6. source_documents
7. evidence_items
8. valuation_models
9. valuation_assumptions
10. research_reports
11. report_sections
12. risks
13. catalysts
14. watchlist
15. ai_categories
16. company_ai_category_mapping

---

## 17. 非功能需求

### 17.1 可追溯性

所有研究结论必须能追溯到：

1. 原始数据
2. 数据来源
3. 计算公式
4. AI 生成时间
5. 使用的模型版本
6. 用户修改过的假设

---

### 17.2 可复算性

所有财务指标和估值结果必须可以重新计算。

不允许只保存 AI 输出的文字结论。

---

### 17.3 稳定性

系统第一版为个人使用，不要求高并发。

但需要保证：

1. 本地可启动
2. 数据库可持久化
3. API 错误有提示
4. 数据拉取失败时不影响已有报告查看

---

### 17.4 安全性

1. API Key 必须放在环境变量。
2. 不要把密钥提交到 Git。
3. 不要在日志中打印密钥。
4. 用户本地数据不得自动上传到未知服务。
5. 不接券商账户。
6. 不保存交易账户信息。

---

## 18. 合规边界

产品必须明确：

1. 仅用于个人研究。
2. 不构成投资建议。
3. 不提供买入、卖出、持有建议。
4. 不保证收益。
5. 不预测短期股价。
6. 不自动下单。
7. 不替用户做投资决策。

系统禁止输出以下表达：

```text
强烈买入
一定上涨
稳赚
无风险
保证收益
现在必须买
现在必须卖
```

允许输出：

```text
该公司值得进一步研究。
当前估值对增长假设高度敏感。
风险回报需要结合个人判断。
该结论依赖以下关键假设。
```

---

## 19. 成功标准

MVP 成功标准：

1. 本地系统可以正常启动。
2. 用户可以输入一个 AI 相关美股代码。
3. 系统可以返回公司基本信息。
4. 系统可以保存公司财务数据。
5. 系统可以计算核心财务指标。
6. 系统可以生成结构化公司研究报告。
7. 报告包含数据来源。
8. 报告不会输出买卖建议。
9. 用户可以查看历史研究报告。
10. 至少支持 10 家 AI 相关美股公司。

第一批测试股票：

```text
NVDA
MSFT
GOOGL
AMZN
META
AMD
AVGO
TSM
ASML
PLTR
```

---

## 20. 版本路线图

## V0.1：项目骨架

目标：

1. 创建前后端项目
2. 创建数据库
3. 创建 Docker Compose
4. 创建首页和后端 health check
5. 创建基础公司查询页面

---

## V0.2：数据模型

目标：

1. 创建公司表
2. 创建财务数据表
3. 创建研究报告表
4. 创建风险和催化剂表
5. 创建 AI 分类表

---

## V0.3：财务指标引擎

目标：

1. 支持手动导入财务数据
2. 计算核心财务指标
3. 展示财务趋势
4. 保存计算结果

---

## V0.4：SEC 数据接入

目标：

1. 接入 SEC company facts
2. 接入 SEC filings
3. 获取 10-K 和 10-Q
4. 标准化核心财务字段

---

## V0.5：AI 研究报告

目标：

1. 实现 Company Research Agent
2. 实现 Financial Analyst Agent
3. 实现 Risk Auditor Agent
4. 生成第一版研究报告

---

## V0.6：估值模型

目标：

1. 实现 PE / PS / EV/EBITDA
2. 实现简化 DCF
3. 实现 Bull / Base / Bear 情景
4. 支持用户修改假设

---

## V0.7：同业比较

目标：

1. 支持多家公司比较
2. 支持财务指标对比
3. 支持估值对比
4. 输出 AI 总结

---

## V0.8：个人研究工作台

目标：

1. Watchlist
2. 历史报告
3. 用户备注
4. 报告导出 Markdown

---

## 21. Codex 开发要求

Codex 在开发时必须遵守：

1. 先读本 BRD，再制定开发计划。
2. 不要一次性开发全部功能。
3. 按版本逐步实现。
4. 每个阶段必须有可运行结果。
5. 每个核心计算必须有单元测试。
6. 不允许硬编码 API Key。
7. 不允许伪造真实财务数据。
8. 如果没有真实数据，使用 clearly labeled synthetic data 作为测试数据。
9. 不允许把模拟数据展示为真实数据。
10. 每次完成后输出：

* 完成了什么
* 修改了哪些文件
* 如何运行
* 如何测试
* 还有什么没完成

---

## 22. Codex 第一阶段任务

请先执行 V0.1，不要直接开发后续版本。

任务：

基于本 BRD 创建 InsightOS 项目骨架。

技术栈：

* Frontend：Next.js + TypeScript
* Backend：FastAPI + Python
* Database：PostgreSQL
* Container：Docker Compose

请完成：

1. 创建项目目录结构。
2. 创建 backend FastAPI 服务。
3. 创建 `/health` API。
4. 创建 frontend 首页。
5. 前端首页可以调用后端 `/health`。
6. 创建 PostgreSQL 配置。
7. 创建 `.env.example`。
8. 创建 README。
9. 创建基础测试。
10. 不接入真实金融数据。
11. 不调用外部 API。
12. 不实现 AI Agent。
13. 不实现估值模型。

验收标准：

1. `docker compose up` 可以启动系统。
2. 前端页面可以打开。
3. 后端 `/health` 返回正常。
4. 前端可以显示后端健康状态。
5. README 中说明如何启动和测试。
6. 所有测试通过。

---

## 23. 后续开发原则

开发顺序必须是：

```text
产品骨架
↓
数据库模型
↓
财务数据
↓
财务指标计算
↓
SEC 数据接入
↓
AI 研究报告
↓
估值模型
↓
同业比较
↓
Watchlist
↓
报告导出
```

禁止跳过数据层直接做 AI 报告。

核心原则：

```text
先数据，再计算，再 AI，再产品体验。
```
