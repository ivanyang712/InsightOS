# InsightOS Research Quality System

## Data Quality Checks

The backend quality service checks:

- missing values
- stale observations
- invalid currency codes
- missing units
- fiscal period gaps
- conflicting values for the same metric
- unavailable calculations
- future data leakage in backtests

Every issue is returned with severity, category, message, and whether human review is required.

## AI Output Audit

AI-generated or agent-generated research is checked for:

- unsupported claims
- missing citations
- assumptions written too close to facts
- unavailable financial calculations
- forbidden investment-promise language
- language that resembles personalized buy/sell advice

The report structure must separate:

- facts
- calculations
- assumptions
- interpretations
- risks
- open questions

## Backtest Guardrails

Historical testing must record:

- model version
- report generation time
- valuation assumptions
- input snapshot hash
- conclusion changes
- data availability time

If a record was not available at model run time, the quality service marks the run as
future-data leakage.

## Human Review Flags

The first version supports deterministic flags for:

- needs human confirmation
- low confidence
- data conflict
- valuation sensitivity
- calculation unavailable

## CI/CD Checks

The GitHub workflow runs:

- backend lint with Ruff
- backend type checks with mypy
- backend unit tests with pytest
- frontend lint with ESLint
- frontend type checks with TypeScript
- frontend unit tests with Node test
- Docker Compose configuration validation
- Docker image build
