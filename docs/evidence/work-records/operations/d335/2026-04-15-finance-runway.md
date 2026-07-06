# D335 Finance MC Runway

**Generated:** 2026-04-15T09:57:01.385Z
**Scope:** finance function only, latest active MC version, D335 R4 fail tier
**Process:** walk MCs through `mc-chain-integrity-sop.md` one at a time, in the order below. Bucket B0 → B5 is a heuristic; re-bucket as the SOP surfaces new problem classes.

## Bucket summary

| Bucket | MCs |
|---|---:|
| B0 — single SUM→COUNT (count_where_not_null) | 22 |
| B1 — single SUM→COUNT_DISTINCT (count_distinct) | 55 |
| B2 — single SUM→MAX (latest) | 63 |
| B3 — multiple fixes, single class | 93 |
| B4 — multiple fixes, mixed classes | 34 |
| B5 — BLOCKED (known mapping-semantic issue) | 1 |
| **Total** | **268** |

## Subfunction coverage

| Subfunction | Suspect MCs |
|---|---:|
| accounts_payable | 50 |
| general_ledger | 38 |
| revenue_accounting | 37 |
| general_finance | 35 |
| tax | 17 |
| accounts_receivable | 16 |
| treasury | 14 |
| fpa | 11 |
| financial_systems | 11 |
| payroll | 11 |
| fixed_assets | 6 |
| capital_structure_optimization | 6 |
| iso_55001 | 5 |
| credit_and_collections | 3 |
| financial_risk_management | 3 |
| cash_flow_management | 3 |
| billing | 1 |
| investor_relations | 1 |

## Runway (ordered simplest → hardest)

| # | Status | MC Name | Subfunction | Bucket | Findings | Classes | Formula |
|---|---|---|---|---|---:|---|---|
| 1 | `mc__ap_document_retention_compliance` | accounts_payable | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 2 | `mc__ar_staff_productivity` | accounts_receivable | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 3 | `mc__dispute_resolution_time` | accounts_receivable | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 4 | `mc__intercompany_reconciliation_aging` | accounts_receivable | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 5 | `mc__invoice_delivery_time` | accounts_receivable | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 6 | ⚠ | `mc__revenue_recognition_lag` | accounts_receivable | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` | *Walked 2026-04-15 SES-60f784 — FIX APPLIED, VERIFY-FAIL, ROLLED BACK. FUP-2: I1 CF→BF mapping error. See [d335-mc-log.md](2026-04-15-mc-walkthrough-log.md).* |
| 7 | `mc__automated_invoices` | billing | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 8 | `mc__invoices_disputed` | credit_and_collections | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 9 | `mc__budget_reforecast_frequency` | fpa | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1)` |
| 10 | `mc__budget_versions_produced_before_final_approval` | fpa | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1)` |
| 11 | `mc__average_contract_value_acv` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 12 | ⚠ | `mc__average_invoice_value` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` | *Walked 2026-04-15 SES-951037 — AUTO-FIXABLE + UNTESTABLE (no COs in demo-selenite). Rolled back. FUP-3. See [d335-mc-log.md](2026-04-15-mc-walkthrough-log.md).* |
| 13 | `mc__disputed_invoice_rate` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 14 | `mc__e_invoice_adoption_rate` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 15 | `mc__electronic_invoice_adoption_rate` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 16 | `mc__warehouse_cost_per_order` | general_finance | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 17 | `mc__capital_projects_completed_on_time` | general_ledger | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 18 | `mc__auto_invoice_generation_rate` | revenue_accounting | B0 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 19 | `mc__average_deal_size` | revenue_accounting | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 20 | `mc__average_ecommerce_order_value` | revenue_accounting | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 21 | `mc__average_retail_order_value` | revenue_accounting | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 22 | `mc__invoice_line_items_per_receipt` | revenue_accounting | B0 | 1 | sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 23 | `mc__expense_report_exception_line_item_pct` | accounts_payable | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 24 | `mc__invoice_line_items_per_invoice` | accounts_payable | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 25 | `mc__manual_urgent_payment_share` | accounts_payable | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 26 | `mc__self_billing_invoice_rate` | accounts_payable | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 27 | `mc__arpar` | accounts_receivable | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) - SUM(I2) - SUM(I3)` |
| 28 | `mc__accounts_receivable_turnover_ratio` | credit_and_collections | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 29 | `mc__average_payment_days_apd` | credit_and_collections | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / (SUM(I2) / C1)` |
| 30 | `mc__credit_exposure` | financial_risk_management | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) + SUM(I2) + SUM(I3)` |
| 31 | `mc__financial_system_adoption` | financial_systems | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 32 | `mc__system_downtimes` | financial_systems | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1)` |
| 33 | `mc__fixed_asset_cost_accuracy` | fixed_assets | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 34 | `mc__fixed_asset_register_completeness` | fixed_assets | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 35 | `mc__total_revenue_per_active_customer` | fpa | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 36 | `mc__audit_adjustments_count` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1)` |
| 37 | `mc__cost_per_shipment` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 38 | `mc__cost_per_transaction` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 39 | `mc__electronic_payment_adoption` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 40 | `mc__payment_processing_cost` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 41 | `mc__profit_per_customer` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 42 | `mc__tax_jurisdictions_managed` | general_finance | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1)` |
| 43 | `mc__accruals_generated_using_a_fully_automated_method` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 44 | `mc__accruals_generated_using_a_fully_manual_method` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 45 | `mc__accruals_generated_using_both_automation_and_manual_methods` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 46 | `mc__capitalize_a_fixed_asset_purchase` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 47 | `mc__control_violations_new` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 48 | `mc__control_violations_previously_identified` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 49 | `mc__fixed_asset_transactions_handled_automatically_without_human_intervention` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 50 | `mc__ftes_performing_esg_reporting_outside_the_esg_function_as_percentage_of_total` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 51 | `mc__gross_margin_per_hectare` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) - SUM(I2)) / SUM(I3)` |
| 52 | `mc__gross_profit_per_unit_gpu` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) - SUM(I2)) / SUM(I3)` |
| 53 | `mc__intercompany_transactions_processed_using_a_fully_manual_method` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 54 | `mc__intercompany_transactions_processed_using_both_automation_and_manual_methods` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 55 | `mc__journal_entries_automated_or_system_generated_at_the_finance_shared_services` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 56 | `mc__journal_entry_line_items_automated_and_recurring` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 57 | `mc__journal_entry_line_items_of_types_other_than_intercompany_corrective_adjusting` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 58 | `mc__journal_entry_line_items_processed_error_free` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 59 | `mc__journal_entry_line_items_sourced_through_methods_other_than_manual_direct_link` | general_ledger | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 60 | `mc__analyst_coverage` | investor_relations | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1)` |
| 61 | `mc__asset_disposal_efficiency` | iso_55001 | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) - SUM(I2)) / SUM(I3)` |
| 62 | `mc__asset_information_accuracy_rate` | iso_55001 | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 63 | `mc__arpu` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 64 | `mc__arpu_by_segment` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 65 | `mc__average_line_items_per_invoice` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 66 | `mc__blended_arpu` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 67 | `mc__days_cash_on_hand` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / (SUM(I2) / SUM(I3))` |
| 68 | `mc__net_revenue` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) - SUM(I2) - SUM(I3) - SUM(I4)` |
| 69 | `mc__revenue_per_customer` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 70 | `mc__revenue_per_departure` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 71 | `mc__revenue_per_employee` | revenue_accounting | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 72 | `mc__audit_defense_success_rate` | tax | B1 | 1 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 73 | `mc__tax_controversy_resolution_time` | tax | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 74 | `mc__tax_notice_response_time` | tax | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 75 | `mc__average_cycle_time_in_hours_for_the_organization_to_concentrate_physically_pool` | treasury | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 76 | `mc__average_daily_cash_balance` | treasury | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 77 | `mc__funding_diversification_index` | treasury | B1 | 1 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 78 | `mc__ap_automation_technology_cost` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) + SUM(I2) + SUM(I3) + SUM(I4)` |
| 79 | `mc__ap_staff_productivity` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 80 | `mc__ap_turnover_ratio` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 81 | `mc__no_po_invoice_rate` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 82 | `mc__payment_on_time_rate` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 83 | `mc__payment_timeliness_pct` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 84 | `mc__po_first_time_error_free_rate` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 85 | `mc__predicted_cash_outflow` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = ML_MODEL(SUM(I1), SUM(I2), SUM(I3))` |
| 86 | `mc__supplier_risk_assessment_frequency` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 87 | `mc__vendor_satisfaction_score` | accounts_payable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 88 | `mc__ar_turnover` | accounts_receivable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 89 | `mc__doubtful_debt_provision` | accounts_receivable | B2 | 1 | sum_on_latest | `O1 = SUM(I1) * SUM(I2)` |
| 90 | `mc__book_value_of_equity_per_share_bvps` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 91 | `mc__equity_turnover_ratio` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 92 | `mc__interest_rate_spread` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 93 | `mc__roa_return_on_assets` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 94 | `mc__roe_return_on_equity` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 95 | `mc__total_asset_turnover_ratio` | capital_structure_optimization | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 96 | `mc__capital_expenditure_growth_rate` | cash_flow_management | B2 | 1 | sum_on_latest | `O1 = ((SUM(I1) - SUM(I2)) / SUM(I2)) * C1` |
| 97 | `mc__gross_margin_return_on_investment_gmroi` | cash_flow_management | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 98 | `mc__transaction_volume_capacity` | financial_systems | B2 | 1 | sum_on_latest | `O1 = SUM(I1)` |
| 99 | `mc__workflow_efficiency` | financial_systems | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 100 | `mc__fixed_asset_renewal_and_replacement_reserve` | fixed_assets | B2 | 1 | sum_on_latest | `O1 = SUM(I1) * SUM(I2)` |
| 101 | `mc__return_on_assets_roa` | fixed_assets | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 102 | `mc__capital_expenditure_capex` | fpa | B2 | 1 | sum_on_latest | `O1 = SUM(I1) + SUM(I2) - SUM(I3)` |
| 103 | `mc__capital_turnover_ratio` | fpa | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 104 | `mc__cost_center_variance_distribution` | fpa | B2 | 1 | sum_on_latest | `O1 = DISTRIBUTION(SUM(I1) BY I2)` |
| 105 | `mc__time_finance_related_chatbots_bots_and_dwes_not_available_for_use` | fpa | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 106 | `mc__break_even_point` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / (SUM(I2) - SUM(I3))` |
| 107 | `mc__cost_of_deposits` | general_finance | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 108 | `mc__csm_release_rate` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 109 | `mc__days_inventory_outstanding_dio` | general_finance | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 110 | `mc__economic_value_added_eva` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM(I1) - (SUM(I2) * SUM(I3))` |
| 111 | `mc__predicted_margin_quarter_end` | general_finance | B2 | 1 | sum_on_latest | `O1 = ML_FORECAST(SUM(I1), horizon=I2, features=[I3, I4, I5])` |
| 112 | `mc__return_on_idle_cash` | general_finance | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 113 | `mc__spread_yield_on_advances_minus_cost_of_deposits` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 114 | `mc__tax_savings_from_planning` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM(I1)` |
| 115 | `mc__total_cost_of_continuing_operations_as_percentage_of_revenue` | general_finance | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 116 | `mc__weighted_average_debt_maturity` | general_finance | B2 | 1 | sum_on_latest | `O1 = SUM_PRODUCT(I1, SUM(I2)) / SUM(I1)` |
| 117 | `mc__yield_on_advances` | general_finance | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 118 | `mc__accounts_payable_turnover_ratio` | general_ledger | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 119 | `mc__complete_the_monthly_consolidated_financial_statements` | general_ledger | B2 | 1 | sum_on_latest | `O1 = SUM(I1)` |
| 120 | `mc__journal_entry_line_items_first_time_originating` | general_ledger | B2 | 1 | sum_on_latest | `O1 = SUM(I1)` |
| 121 | `mc__total_asset_turnover` | general_ledger | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 122 | `mc__capital_budgeting_efficiency` | iso_55001 | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 123 | `mc__capital_expenditure_capex_efficiency` | iso_55001 | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 124 | `mc__working_asset_turnover_ratio` | iso_55001 | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 125 | `mc__customer_pre_payment_adjustment_invoice_rate` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 126 | `mc__dso_to_payment_terms_ratio` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 127 | `mc__expansion_revenue_rate` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 128 | `mc__first_time_full_payment_invoice_rate` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 129 | `mc__mrr` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = SUM(I1) * SUM(I2)` |
| 130 | `mc__predicted_billing_volume` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = ML_FORECAST(SUM(I1), horizon=SUM(I2), features=[SUM(I3), I4, I5])` |
| 131 | `mc__revenue_churn` | revenue_accounting | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 132 | `mc__sales_use_tax_audit_exposure` | tax | B2 | 1 | sum_on_latest | `O1 = SUM(SUM(I1) * SUM(I2))` |
| 133 | `mc__tax_function_cost_to_savings_ratio` | tax | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 134 | `mc__time_to_close_tax_provision` | tax | B2 | 1 | sum_on_latest | `O1 = SUM(I1)` |
| 135 | `mc__cash_conversion_cycle_ccc` | treasury | B2 | 1 | sum_on_latest | `O1 = SUM(I1) + SUM(I2) - SUM(I3)` |
| 136 | `mc__ccc_year_over_year_change` | treasury | B2 | 1 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 137 | `mc__hedge_ratio` | treasury | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 138 | `mc__liquidity_coverage_ratio` | treasury | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 139 | `mc__ratio_of_active_currency_positions` | treasury | B2 | 1 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 140 | `mc__working_capital_turnover` | treasury | B2 | 1 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 141 | `mc__ap_balance_sheet_reconciliation_completeness` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 142 | `mc__ap_tax_compliance_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 143 | `mc__audited_invoice_pct` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 144 | `mc__auto_matched_invoice_pct` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 145 | `mc__blanket_code_approval_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 146 | `mc__disbursement_error_resolution_time` | accounts_payable | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 147 | `mc__discount_offering_invoice_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 148 | `mc__discrepancy_identification_time` | accounts_payable | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 149 | `mc__duplicate_payment_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 150 | `mc__e_invoicing_network_receipt_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 151 | `mc__electronic_disbursement_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 152 | `mc__electronic_invoice_approval_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 153 | `mc__electronic_invoice_submission_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 154 | `mc__electronic_payment_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 155 | `mc__error_free_disbursement_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 156 | `mc__error_rate_in_invoicing` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 157 | `mc__fraud_detection_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 158 | `mc__invoice_fraud_detection_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 159 | `mc__manual_payment_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 160 | `mc__missed_discount_pct` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 161 | `mc__payment_accuracy_rate` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 162 | `mc__receipt_to_payment_cycle_time` | accounts_payable | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 163 | `mc__recurring_payment_pct` | accounts_payable | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 164 | `mc__strategic_payment_timing_score` | accounts_payable | B3 | 2 | sum_on_latest | `O1 = SCORE_BASED_ON_CRITERIA(SUM(I1), SUM(I2), SUM(I3))` |
| 165 | `mc__te_reimbursement_cycle_time` | accounts_payable | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 166 | `mc__credit_risk_rating_changes` | accounts_receivable | B3 | 2 | sum_on_count_where_not_null | `O1 = SUM(I1) - SUM(I2)` |
| 167 | `mc__cash_flow_stability` | cash_flow_management | B3 | 2 | sum_on_latest | `O1 = STDDEV(SUM(I1), SUM(I2))` |
| 168 | `mc__availability_of_financial_systems` | financial_systems | B3 | 2 | sum_on_latest | `O1 = ((SUM(I1) - SUM(I2)) / SUM(I1)) * C1` |
| 169 | `mc__cost_of_financial_system_downtime_per_hour` | financial_systems | B3 | 2 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 170 | `mc__financial_reports_generated_on_time` | financial_systems | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 171 | `mc__real_time_financial_data` | financial_systems | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 172 | `mc__asset_downtime_ratio` | fixed_assets | B3 | 2 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 173 | `mc__asset_retirement_obligations_aro` | fixed_assets | B3 | 2 | sum_on_count_distinct | `O1 = SUM(I1) / ((1 + SUM(I2))^SUM(I3))` |
| 174 | `mc__complete_the_annual_budget` | fpa | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 175 | `mc__percentage_improvement_achieved_in_revenue_per_employee_from_finance_function` | fpa | B3 | 2 | sum_on_latest | `O1 = ((SUM(I1) - SUM(I2)) / SUM(I2)) * C1` |
| 176 | `mc__percentage_that_ai_in_financial_planning_and_analysis_has_reduced_the_average` | fpa | B3 | 2 | sum_on_latest | `O1 = ((SUM(I2) - SUM(I1)) / SUM(I2)) * C1` |
| 177 | `mc__percentage_that_ai_in_order_to_cash_is_estimated_to_reduce_the_total_annual` | fpa | B3 | 2 | sum_on_latest | `O1 = ((SUM(I2) - SUM(I1)) / SUM(I2)) * C1` |
| 178 | `mc__cash_runway` | general_finance | B3 | 2 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 179 | `mc__combined_ratio` | general_finance | B3 | 2 | sum_on_latest | `O1 = SUM(I1) + SUM(I2)` |
| 180 | `mc__employees_per_legal_entity_supported_by_the_finance_shared_services_center` | general_finance | B3 | 2 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 181 | `mc__operating_leverage` | general_finance | B3 | 2 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 182 | `mc__payment_error_rate` | general_finance | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 183 | `mc__price_elasticity_index` | general_finance | B3 | 2 | sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 184 | `mc__time_to_invoice` | general_finance | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 185 | `mc__account_reconciliation_completion` | general_ledger | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 186 | `mc__completion_of_annual_consolidated_financial_statements_and_the_release_of` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 187 | `mc__completion_of_quarterly_consolidated_financial_statements_and_the_release_of` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 188 | `mc__finance_shared_services_center_to_complete_the_monthly_financial_close` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 189 | `mc__identification_of_change_in_risk_until_changes_to_risk_management_policies_and` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 190 | `mc__manual_journal_entry_line_item_percentage` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) + SUM(I2)` |
| 191 | `mc__perform_annual_close_at_the_site_level` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 192 | `mc__produce_period_end_management_reports` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 193 | `mc__producing_annual_flash_reports_to_completing_consolidated_annual_financial` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 194 | `mc__producing_monthly_flash_reports_to_completing_the_monthly_consolidated` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 195 | `mc__reporting_of_a_control_violation_until_investigation_is_completed_and` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 196 | `mc__subledger_to_gl_reconciliation_delay` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 197 | `mc__the_identification_of_a_control_violation_until_the_violation_is_reported` | general_ledger | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 198 | `mc__cycle_time_in_business_days_between_the_time_period_cut_off_for_employees_and` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 199 | `mc__cycle_time_in_business_days_from_hr_benefits_system_cut_off_until_payroll` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 200 | `mc__cycle_time_in_business_days_from_the_payroll_system_cut_off_date_until_payroll` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 201 | `mc__cycle_time_in_business_days_to_process_the_payroll` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 202 | `mc__cycle_time_in_business_days_to_process_time_record_data_and_enter_into_payroll` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 203 | `mc__cycle_time_in_business_days_to_reflect_a_new_employee_in_the_payroll_system` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 204 | `mc__cycle_time_in_business_days_to_remove_a_terminated_employee_from_the_payroll` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 205 | `mc__cycle_time_in_business_days_to_resolve_a_payroll_error` | payroll | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 206 | `mc__payroll_disbursements_that_include_retroactive_pay_adjustments` | payroll | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * 100` |
| 207 | `mc__time_records_processed_first_time_error_free` | payroll | B3 | 2 | sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 208 | `mc__adjustment_resolution_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 209 | `mc__ar_and_collections_cycle_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 210 | `mc__automated_gl_entry_rate` | revenue_accounting | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 211 | `mc__billing_cycle_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 212 | `mc__billing_data_generation_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 213 | `mc__customer_pre_payment_adjustment_line_item_rate` | revenue_accounting | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 214 | `mc__discount_capture_rate_billed` | revenue_accounting | B3 | 2 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 215 | `mc__discount_offering_billed_line_item_rate` | revenue_accounting | B3 | 2 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 216 | `mc__electronic_invoicing_rate` | revenue_accounting | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 217 | `mc__invoice_line_item_error_free_rate` | revenue_accounting | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 218 | `mc__invoice_process_cycle_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 219 | `mc__invoice_to_payment_cycle_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 220 | `mc__invoice_to_shipment_cycle_time` | revenue_accounting | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 221 | `mc__receipt_error_free_rate` | revenue_accounting | B3 | 2 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 222 | `mc__ratio_of_tax_strategy_to_tax_filing_staff_at_the_finance_shared_services_center` | tax | B3 | 2 | sum_on_count_distinct | `O1 = SUM(I1) / SUM(I2)` |
| 223 | `mc__tax_department_staff_turnover_rate` | tax | B3 | 2 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 224 | `mc__cash_position_accuracy` | treasury | B3 | 2 | sum_on_latest | `O1 = C1 - (ABS(SUM(I1) - SUM(I2)) / SUM(I2)) * C1` |
| 225 | `mc__refresh_the_cash_flow_forecast` | treasury | B3 | 2 | sum_on_latest | `O1 = SUM(I1) - SUM(I2)` |
| 226 | `mc__auto_receipt_settlement_rate` | accounts_payable | B3 | 3 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 227 | `mc__duplicate_erroneous_payment_rate` | accounts_payable | B3 | 3 | sum_on_count_distinct | `O1 = ((SUM(I1) + SUM(I2)) / SUM(I3)) * C1` |
| 228 | `mc__edi_invoice_rate` | accounts_payable | B3 | 3 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 229 | `mc__electronic_invoice_receipt_rate` | accounts_payable | B3 | 3 | sum_on_count_distinct | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 230 | `mc__vendor_risk_score` | accounts_payable | B3 | 3 | sum_on_latest | `O1 = ML_MODEL(SUM(I1), SUM(I2), SUM(I3))` |
| 231 | `mc__o2c_cycle_time` | accounts_receivable | B3 | 3 | sum_on_latest | `O1 = SUM(I1) + SUM(I2) + SUM(I3)` |
| 232 | `mc__other_non_independent_members_on_the_compensation_committee` | general_ledger | B3 | 3 | sum_on_count_distinct | `O1 = (SUM(I1) / (SUM(I2) + SUM(I1) + SUM(I3))) * C1` |
| 233 | `mc__cycle_time_in_hours_to_initiate_approve_and_dispatch_a_wire_transfer` | treasury | B3 | 3 | sum_on_latest | `O1 = SUM(I1) + SUM(I2) + SUM(I3)` |
| 234 | `mc__cash_flow_impact_from_ap` | accounts_payable | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) + SUM(I2) - SUM(I3)` |
| 235 | `mc__first_time_match_rate` | accounts_payable | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 236 | `mc__forecasted_discount_opportunity` | accounts_payable | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = ML_MODEL(SUM(I1), SUM(I2), SUM(I3))` |
| 237 | `mc__third_party_ap_provider_performance` | accounts_payable | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = SUM(I1) / SUM(I2)` |
| 238 | `mc__average_invoice_processing_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 239 | `mc__billing_to_cash_cycle_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 240 | `mc__credit_approval_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 241 | `mc__credit_hold_resolution_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 242 | `mc__credit_onboarding_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 243 | `mc__customer_request_turnaround_time` | accounts_receivable | B4 | 2 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 244 | `mc__supplier_risk_audit_frequency` | financial_risk_management | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 245 | `mc__third_party_vendor_risk_assessment_frequency` | financial_risk_management | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 246 | `mc__data_processing_time` | financial_systems | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 247 | `mc__financial_transaction_error_detection_rate` | financial_systems | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 248 | `mc__frequency_of_financial_system_upgrades` | financial_systems | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 249 | `mc__cash_burn_rate` | general_finance | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = (SUM(I1) - SUM(I2)) / SUM(I3)` |
| 250 | `mc__cycle_count_accuracy` | general_finance | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 251 | `mc__tax_automation_rate` | general_finance | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 252 | `mc__accounts_standard_with_the_business_units_reporting_to_your_site` | general_ledger | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 253 | `mc__task_completion_by_deadline` | general_ledger | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 254 | `mc__time_records_entered_manually_into_the_payroll_system` | payroll | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 255 | `mc__customer_delinquency_rate` | revenue_accounting | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 256 | `mc__indirect_tax_compliance_rate` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 257 | `mc__payroll_tax_compliance_rate` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 258 | `mc__property_tax_assessment_accuracy` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 259 | `mc__tax_compliance_rate` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 260 | `mc__tax_dispute_resolution_rate` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 261 | `mc__tax_documentation_completeness` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 262 | `mc__tax_filing_timeliness` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 263 | `mc__tax_function_automation` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 264 | `mc__tax_process_digitalization_level` | tax | B4 | 2 | sum_on_count_distinct, sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` |
| 265 | `mc__total_cost_of_the_process_group_manage_treasury_operations_per_bank_used_in` | treasury | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 266 | `mc__total_cost_of_the_process_group_manage_treasury_operations_per_global_legal` | treasury | B4 | 2 | sum_on_count_distinct, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 267 | `mc__intercompany_billing_efficiency` | accounts_payable | B4 | 3 | sum_on_count_where_not_null, sum_on_latest | `O1 = SUM(I1) / SUM(I2)` |
| 268 | ⚠ | `mc__active_customer_rate` | revenue_accounting | B5 | 1 | sum_on_count_where_not_null | `O1 = (SUM(I1) / SUM(I2)) * C1` | *Walked 2026-04-15 SES-60f784 — BLOCKED, FUP-1. See [d335-mc-log.md](2026-04-15-mc-walkthrough-log.md).* |

## Walk-through protocol

1. Pick the next unwalked row from this runway.
2. Run `node scripts/mc-diagnose.mjs <metric_contract_id>` — full integrity check.
3. Classify verdict: ready / auto-fixable / human-required / blocked.
4. Apply the prescribed SOP path. Log outcome in `d335-mc-log.md`.
5. Update this runway: mark row ✅ (fixed), ⚠ (blocked, FUP opened), or ✗ (aborted with reason).

**Discipline (D268 Rule 3):** walk one MC end-to-end before starting the next.
