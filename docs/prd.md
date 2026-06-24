# InsightOS MVP PRD

## 1. Product Positioning

InsightOS is an AI-assisted investment research operating system for US-listed companies
and US macro data. The MVP focuses on evidence-backed company research, industry context,
financial analysis, valuation scenarios, risk review, and auditability.

InsightOS does not execute trades, connect brokerage accounts, or provide personalized
buy/sell recommendations. Its core promise is verifiable research conclusions, where every
claim can be traced to source metadata, raw data, formulas, assumptions, and generation time.

## 2. Target Users

| User | Need | MVP Fit |
| --- | --- | --- |
| Buy-side analyst | Faster first-pass research with citations and model checks. | Company reports, evidence chunks, financial calculations. |
| Portfolio manager | Track thesis changes, risks, and catalysts. | Watchlists, alerts, bull/base/bear scenarios. |
| Independent researcher | Understand companies without losing source traceability. | Demo UI, source lists, formula docs. |
| Research operations lead | Enforce data quality and review rules. | Quality checks, audit reports, CI gates. |

## 3. Core Use Cases

1. Enter a US ticker, load SEC profile, filings, XBRL facts, and relevant US macro series.
2. Normalize raw data into traceable financial facts.
3. Calculate financial quality metrics and valuation scenarios using deterministic Python.
4. Generate a research packet that separates facts, calculations, assumptions,
   interpretations, risks, and open questions.
5. Run data quality and AI output audits before a report is treated as review-ready.
6. Track a company or industry through watchlists and alerts.

## 4. Feature Priority

### Must Have

- Monorepo with Next.js frontend, FastAPI backend, PostgreSQL, Redis, Docker Compose.
- Evidence-chain database models and migrations.
- SEC EDGAR, SEC XBRL, and FRED connector interfaces.
- Raw layer and normalized layer separation.
- Deterministic financial quality and valuation services.
- Industry archetype matching and metric rules.
- Multi-agent research orchestration skeleton.
- Quality checks for data, AI output, and backtest leakage.
- Synthetic fixtures and automated tests.

### Should Have

- Persist connector runs to PostgreSQL instead of in-memory task state.
- User-uploaded documents with chunking and evidence retrieval.
- Editable valuation assumptions in frontend.
- Report version comparison.
- Human review queue.

### Later

- Live market data vendor integrations.
- Real-time alert delivery.
- Portfolio-level exposure analytics.
- Collaboration workflows.
- Role-based permissions.
- Production-grade background worker deployment.

## 5. Company Page Information Architecture

1. Header: company name, ticker, exchange, CIK, archetype, data freshness.
2. Research summary: conclusion status, confidence score, open questions, review flags.
3. Business model: revenue segments, unit economics, management commentary labels.
4. Industry and competition: archetype template, peers, competitive advantages, cycle context.
5. Financial quality: five-year metrics, formula links, unavailable metrics.
6. Valuation: DCF, PE, PB, PS, EV/EBITDA, EV/FCF, reverse DCF, sensitivity.
7. Risk audit: red flags, conflicting evidence, missing data, stale data.
8. Catalysts and monitoring: watchlist rules, alerts, upcoming events.
9. Evidence panel: filings, source documents, evidence chunks, raw response hashes.

## 6. Industry Page Information Architecture

1. Industry map: upstream, midstream, downstream, company examples.
2. Archetype rules: applicable metrics, unavailable metrics, fallback metrics.
3. Market drivers: demand, supply, regulation, macro sensitivity.
4. Competitive landscape: concentration, barriers, regional differences.
5. Cycle indicators: leading and lagging indicators to track.
6. Company comparison: peer principles and score matrix.
7. Risks and catalysts: three-year framework.
8. Evidence panel: source documents, confidence, retrieval timestamps.

## 7. Ticker-To-Report Flow

1. User enters ticker.
2. System resolves company and CIK.
3. Connector stores raw SEC/FRED responses with source URL, retrieval time, and hash.
4. Normalizer converts raw records into standardized financial facts and macro observations.
5. Quality checks flag missing, stale, conflicting, or abnormal data.
6. Financial engine calculates metrics and valuations with formulas and input snapshots.
7. Archetype engine selects the right analysis template.
8. Agents assemble facts, calculations, assumptions, interpretations, risks, and questions.
9. Risk auditor blocks unsupported claims and forbidden recommendation language.
10. User receives a report with sources, confidence, and review flags.

## 8. Data Source Strategy

| Layer | Sources | Rule |
| --- | --- | --- |
| Official raw | SEC EDGAR, SEC XBRL, FRED | Highest priority; always store raw payload and hash. |
| Company materials | Investor relations materials, user uploads | Label management claims as management views. |
| Normalized facts | Derived from raw layer | Never edited by LLMs. |
| Calculations | Deterministic Python services | Store formula, inputs, output, calculated_at. |
| AI interpretations | Generated from stored facts/evidence | Never treated as primary source. |

## 9. Risk And Compliance Boundaries

- No personalized investment advice.
- No automated trading or brokerage connection.
- No buy now, sell now, guaranteed return, or target-price command language.
- No fabricated numbers, citations, dates, competitors, or events.
- Missing or conflicting data must be shown explicitly.
- Management statements are marked as management views, not verified facts.
- Synthetic fixtures are allowed only for tests and demos.

## 10. Roadmap

### Version 0.1

Runnable skeleton, evidence-chain schema, SEC/FRED connector interfaces, deterministic
financial engine, archetypes, multi-agent skeleton, quality checks, demo workflow.

### Version 0.2

Persistent ingestion jobs, report versioning, editable assumptions, user-uploaded documents,
human review queue, richer company page.

### Version 0.3

Live scheduled refresh, alert delivery, industry dashboards, peer comparison workflows,
backtest UI, team collaboration controls.

## First Version Explicitly Does Not Do

- No paid market-data APIs.
- No live brokerage/trading.
- No personalized buy/sell advice.
- No production authentication.
- No production document storage.
- No LLM-generated financial numbers.
- No unsupported non-US company coverage in the first phase.
