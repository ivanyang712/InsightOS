# InsightOS Formula Reference

All financial metrics are calculated by deterministic Python services. LLMs may explain outputs but must not perform critical calculations.

## Financial Quality

| Metric | Formula |
| --- | --- |
| Revenue Growth | `(current_revenue - previous_revenue) / previous_revenue` |
| Gross Margin | `gross_profit / revenue` |
| Operating Margin | `operating_income / revenue` |
| Net Margin | `net_income / revenue` |
| EBITDA Margin | `ebitda / revenue` |
| ROIC | `operating_income * (1 - tax_rate) / (total_debt + shareholders_equity - cash)` |
| ROE | `net_income / shareholders_equity` |
| FCF Margin | `free_cash_flow / revenue` |
| Debt / EBITDA | `total_debt / ebitda` |
| Net Debt / EBITDA | `(total_debt - cash) / ebitda` |
| Current Ratio | `current_assets / current_liabilities` |
| Interest Coverage | `operating_income / interest_expense` |
| Share Dilution | `(current_shares - previous_shares) / previous_shares` |
| Inventory Turnover | `cost_of_goods_sold / average_inventory` |
| Receivable Days | `average_accounts_receivable / revenue * 365` |
| Cash Conversion Cycle | `inventory_days + receivable_days - payable_days` |

## Valuation

| Model | Formula |
| --- | --- |
| DCF | `sum(FCF_t/(1+r)^t) + terminal_value/(1+r)^n - net_debt` |
| PE | `earnings * selected_pe_multiple` |
| PB | `book_value * selected_pb_multiple` |
| PS | `sales * selected_ps_multiple` |
| EV/EBITDA | `ebitda * selected_ev_ebitda_multiple` |
| EV/FCF | `free_cash_flow * selected_ev_fcf_multiple` |
| Reverse DCF | Solve the growth rate where DCF enterprise value equals the target enterprise value. |

If an input is missing, zero where invalid, stale, or conflicting, the service returns `status=unavailable` and a Chinese message beginning with `无法可靠计算`.
