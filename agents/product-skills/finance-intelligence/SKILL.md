---
name: finance-intelligence
description: >-
  Finance Intelligence OS — AI skill invocation profile for personal portfolio
  analysis. Bridges FinanceDataService → LLM → structured output (narrative,
  facts, inference, confidence, review_step). Enforces finance_output_policy:
  no advice, no buy/sell recommendations, no guaranteed returns.
when_to_use: >-
  Use when a task requires explaining portfolio concentration, income forecasts,
  simulation scenarios, FX exposure, or reconciliation findings using the user's
  live portfolio data. All output is data-driven and goes through the Finance
  output policy before surfacing to the user.
---

# Finance Intelligence Profile

Runtime profile for the Finance Intelligence OS layer. Not a financial advisor —
an evidence-first data analyst that explains what the numbers show.

## Skill taxonomy

### Internal skills (POST /v1/finance/intelligence)

| skill_id | LLM task | Trigger |
|---|---|---|
| `finance.portfolio.explain_concentration` | finance_risk_explanation | Risk block tapped in UI |
| `finance.portfolio.explain_risk_block` | finance_risk_explanation | Generic risk block |
| `finance.portfolio.explain_income` | finance_income_narrative | Income hero tapped |
| `finance.income.forecast_narrative` | finance_income_narrative | Income forecast card |
| `finance.income.event_explanation` | finance_income_narrative | Calendar event tapped |
| `finance.simulation.scenario_narrative` | finance_simulation_narrative | Scenario result card |
| `finance.reconciliation.explain_mismatch` | finance_risk_explanation | Reconciliation finding |
| `finance.portfolio.analysis` | finance_portfolio_analysis | General portfolio analysis |

### External skills (MCP tools)

| tool name | description |
|---|---|
| `neyra_finance_portfolio_summary` | Serialized PortfolioSnapshot (positions, totals, run-rate) |
| `neyra_finance_income_events` | Upcoming income events with status/amount/pay_date |
| `neyra_finance_insight_analysis` | Cached or fresh intelligence result for a skill_id |
| `neyra_finance_ask` | Free-form question answered against live portfolio context |

## Output contract

All intelligence responses must contain:
```json
{
  "narrative": "Plain-language explanation",
  "facts": ["Observable data point 1", "…"],
  "inference": ["Interpretation 1", "…"],
  "confidence": 0.0,
  "review_step": "What the user should verify independently",
  "caveats": [{"type": "disclaimer", "text": "…"}]
}
```

## Output policy rules

- NEVER use: "you should buy", "recommend", "guarantee", "will return", "advice",
  "invest in", "sell your", "best choice", "expected to grow"
- ALWAYS separate facts from inferences
- ALWAYS include a review_step
- ALWAYS add caveats when confidence < 0.7 or inference list is non-empty
- If data is missing → say so explicitly, do not fabricate

## Architecture

```
User action → FinanceIntelligenceRequest
  → FinanceContextBuilder (PII-safe context from FinanceDataService)
  → Cache check (FinanceIntelligenceResult, 6h TTL, SHA-256 key)
  → FinanceLLMBridge (task-routed via SKILL_TASK_MAP → LLMProviderConfig)
  → _enforce_output_policy (FORBIDDEN_RECOMMENDATION_PHRASES scan)
  → FinanceInsightMemoryWriter (upsert cache + EventLog audit)
  → FinanceIntelligenceResponse → iOS / MCP consumer
```

## Data access rules

- Read from `finance_data_service` only — no direct ORM in skills
- Context includes: portfolio snapshot (always), risk blocks (risk skills),
  income events (income skills)
- PII-safe: no names, emails, account numbers in LLM context
- Numerical/categorical data only: symbol, asset_class, currency, market_value,
  share, event_type, status, amount, pay_date

## Cache strategy

- TTL: 6 hours from generation
- Cache key: SHA-256(JSON(context_dict, sort_keys=True))
- force_refresh=true bypasses cache (used by pull-to-refresh)
- Stale results served during LLM downtime (LLMBridge fallback)

## Integration points

- **iOS**: `FinanceIntelligenceClient` → `FinanceIntelligenceView` (bottom sheet)
  - Triggered from risk blocks, income hero, calendar events in `FinanceDashboardView`
- **MCP**: `plugins/neyra-cursor-plugin/mcp-server/index.mjs`
  - Tools: `neyra_finance_portfolio_summary`, `neyra_finance_income_events`,
    `neyra_finance_insight_analysis`, `neyra_finance_ask`
- **Backend**: `POST /v1/finance/intelligence` (requires auth)

## Delivery checklist

- [x] `FinanceDataService` — single data access layer
- [x] `FinanceAnalyticsService` — XIRR / TWR / FX / income buckets
- [x] `FinanceIntelligenceRuntime` — full LLM orchestration pipeline
- [x] `LLMProviderConfig` — 4 new Finance task types
- [x] Django migration 0039 — FinanceIncomeEvent, FinanceAllocationSnapshot, FinanceIntelligenceResult
- [x] Endpoints: GET /v1/finance/income-events, GET /v1/finance/allocations,
      GET /v1/finance/positions/{id}/performance, POST /v1/finance/intelligence
- [ ] MCP tools (neyra_finance_*)
- [ ] iOS FinanceIntelligenceClient + FinanceIntelligenceView
- [ ] Wire AI buttons into FinanceDashboardView
