---
title: BCF × OAGIS Retry Ledger Seed (2026-06-24)
description: A0-generated per-row ledger seed for the BCF × OAGIS Broad Buildout program. Status proposed; each row carries packet_hash + substrate_snapshot_hash + evidence_hash. Pending operator A1-A5 program approval before any row can flip to program_authorized.
status: held
authority: a0-compile-preflight
date: 2026-06-24
project: bc-docs-v3
domain: contracts
subdomain: catalog
focus: bcf-oagis-retry-ledger
coordinator_run_id: CRR-a0c24a
substrate_snapshot_hash: sha256:8bcfa7a0bd220e304d2526574f2e0a18c8aa5bcc9a3e5bc8557d76273f46653d
related_docs:
  - bcf-oagis-broad-buildout-blueprint-2026-06-23.md
  - bcf-oagis-compile-report-2026-06-24.md
---

# BCF × OAGIS Retry Ledger Seed (2026-06-24)

> A0-generated per-row ledger seed. Every row begins at `status=proposed`. Operator A1–A5 program approval flips qualifying rows to `program_authorized`. Executable execution follows §8 row rules under the §6C coordinator / workers / single-writer model.

## Header — program completion state (A1–A5 recorded 2026-06-24)

```yaml
program_authorization: active                         # flipped from proposed → active 2026-06-24
program_authorization_at: 2026-06-24T05:10:00Z        # operator authorization timestamp
program_authorization_session: SES-934488             # session that recorded the act
program_authorization_operator: anant                 # operator of record
program_authorization_adr: DEC-f94895                 # D452 — the canonical governance record
program_authorization_compile_session: SES-3ef9dc     # A0 compile session that seeded this ledger
coordinator_run_id: CRR-a0c24a
substrate_snapshot_hash: sha256:8bcfa7a0bd220e304d2526574f2e0a18c8aa5bcc9a3e5bc8557d76273f46653d

# A5 budget / time caps (operator-stated 2026-06-24 per DEC-f94895)
budget_caps:
  total_program_spend_cap_usd: 400
  total_panel_call_cap: 1216                          # 973 executable + 25% retry buffer
  pass_level_caps:
    pass_1_c_waves: { spend_usd: 80, panel_calls: 270 }
    pass_2_e_waves: { spend_usd: 40, panel_calls: 80 }
    pass_3_bc_waves: { spend_usd: 280, panel_calls: 880 }
  per_row_latency_cap_seconds: 180                    # work_claimed_at → final_prewrite_check_at
  wall_time_cap_hours: 24                             # program_start → now

# §6C concurrency defaults (operator-accepted from §14)
concurrency:
  a0_read_classification_workers: 8                   # range 4–8; coordinator scales by CPU
  evidence_packet_workers: 4
  panel_workers_initial: 2                            # ramps to 3 after 20 consecutive clean
  panel_workers_max: 3
  panel_workers_ramp_threshold: 20                    # consecutive clean outcomes required
  writer_cardinality: 1                               # serialized single lane; immutable

# AR posture (DEC-f94895)
ar_posture:
  sufficient_default: [AR-3, AR-4]                    # entity_backbone_completeness + standards_backed_foundation
  optional_strengthening: [AR-1, AR-2, AR-5]          # known_metric_pull / source_chain_pull / operator_strategic_priority

# Open question resolutions (DEC-f94895)
oq_resolutions:
  oq_1_amber_pin_posture: per_row_pin_from_a0_5_catalogue_matrix
  oq_13_red_sequencing: sequential
  oq_14_sequencing_model: layer_first
  oq_15_first_wave: sequential_c1_then_e1_then_bc_ar
  oq_16_ar_review_depth: distribution_plus_catalogue_matrix

cumulative_progress:
  green_rows_total: 27
  green_rows_authored_active: 0
  green_rows_authored_idempotent: 0
  green_rows_parked: 0
  green_rows_rejected: 0
  green_rows_blocked_transient: 0
  amber_rows_total: 639
  amber_rows_authored_draft: 3                          # Pass 1 C1 v2 confirm batch (transportation_method_code, incoterms_code, payment_method_code) — F4-v2 S2b authored at lifecycle_state='draft'; auto-activation step pending
  amber_rows_authored_active: 0
  amber_rows_authored_idempotent: 0
  amber_rows_parked: 27                                 # Pass 1 C1: 25 v1 OPERATOR_REVIEW + 1 v1 REJECT + 2 v2 OPERATOR_REVIEW (gender_code, marital_status_code); reclassified as parked_history under v2 design
  amber_rows_rejected: 0
  amber_rows_blocked_transient: 0
  amber_rows_deferred_insufficient_evidence: 8         # Pass 1 C1 v2 reclassification
  amber_rows_mapped_to_existing: 2                      # Pass 1 C1: destination_country_code + origination_country_code → existing `country code` (ce27c255-…)
  amber_rows_operator_semantic_decision: 25             # Pass 1 C1 v2 reclassification
  red_rows_total: 67
  red_rows_held: 67
  red_rows_packet_drafted: 0
  defer_rows_total: 1700
  unknown_halt_rows_total: 288

# Per-pass DAG state (none started — recording does NOT begin execution)
pass_1_characteristic:
  state: not_started
  proposed_new_chars: 217
  cat_1_review_groups_approved: 6                     # per A0.5 catalogue §1.C1–§1.C6 (matrix is per-row pin authority)

pass_2_entity:
  state: not_started
  proposed_new_entities: 54
  simple_amber: 47
  composite_red: 7
  cat_2_slice_groups_approved: 13                     # per A0.5 catalogue §5 (entity list is per-row pin authority)
  composite_red_pending_packets: 7                    # Inventory Position · Work Order Operation · Operation · BOM Line · Inspection Lot · Test Result · Maintenance Order Operation

pass_3_bc:
  state: not_started
  total_bc_targets: 733
  idempotent_rows: 31

# Held items requiring separate operator decision packets (recording does NOT authorise these)
held:
  red_composite_identity_packets:
    - { entity: Inventory Position, slice: inventory-composite, wave: E4/BC-Inventory, bc_rows_held: 12 }
    - { entity: Work Order Operation, slice: production-composite, wave: E6/BC-Production-composite, bc_rows_held: ? }
    - { entity: Operation, slice: production-composite, wave: E6/BC-Production-composite, bc_rows_held: ? }
    - { entity: Bill of Materials Line, slice: production-composite, wave: E6/BC-Production-composite, bc_rows_held: ? }
    - { entity: Inspection Lot, slice: quality-composite, wave: E9/BC-Quality-composite, bc_rows_held: ? }
    - { entity: Test Result, slice: quality-composite, wave: E9/BC-Quality-composite, bc_rows_held: ? }
    - { entity: Maintenance Order Operation, slice: maintenance-composite, wave: E12/BC-Asset, bc_rows_held: 6 }
  known_per_row_pin_at_execution:
    - { existing_char: effective date, reason: multi-shape OAGIS proposals (date/date/temporal vs date/timestamp/temporal); matches Wave A Customer Invoice case from scope audit §3.5 }

# Execution start gate
execution_start_gate:
  state: pass_1_c1_v2_complete_held_pre_c2             # v2 batch complete; remaining 35 rows held; no C2 entry without operator authorization
  initial_unblock_event: operator instruction "Begin Pass 1 C1 under DEC-f94895" 2026-06-24T05:19Z
  pre_execution_gate_result: passed_after_service_recovery
  service_recovery_at: 2026-06-24T05:30:00Z            # bc-core PID 5900 :3100, bc-ai PID 36188 :4300, F4-v2 401 guard, JWT acquired
  service_recovery_evidence_session: SES-dfac49
  pass_1_c1_started_at: 2026-06-24T05:35:00Z
  pass_1_c1_session: SES-dfac49
  pass_1_c1_authority_adr: DEC-f94895
  pass_1_c1_substrate_snapshot_at_start: { active_entities: 26, active_characteristics: 62, active_business_concepts: 194 }
  pass_1_c1_substrate_snapshot_at_start_at: 2026-06-24T05:33:00Z
  pass_1_c1_substrate_snapshot_at_v2_complete: { active_entities: 26, active_characteristics: 62, active_business_concepts: 194, all_characteristics: 66 }   # 3 new chars at draft state from v2 confirm batch; active-state count unchanged
  pass_1_c1_substrate_snapshot_at_v2_complete_at: 2026-06-24T06:57:00Z
  pass_1_c1_v1_audit_history: bcf-oagis-pass-1-c1-closeout-2026-06-24.md   # the 28 v1 outcomes are audit history, not execution precedent
  pass_1_c1_v2_authored_drafts:
    - { bf: transportation_method_code, term: "transportation method code", characteristic_id: b5999e2e-5c04-46eb-818d-cd7ab9933131, cert_id: c8a2aaa1-d7b6-4e26-aa95-f7fe762164eb, panel_run_uid: c67cd794-778b-44fa-8d5e-793d925a14a3, source: v1_approve_holdover }
    - { bf: incoterms_code, term: "incoterms code", characteristic_id: 679cda4b-3952-4337-b6d1-8def0b2083ff, cert_id: eb41c81a-e35b-4224-8191-6d1b5cd45790, panel_run_uid: 4b47792c-5668-4aca-97fc-272df84df1ab, source: v1_approve_holdover }
    - { bf: payment_method_code, term: "payment method code", characteristic_id: 61b92f99-5450-41f0-92c0-84fd9b61aa14, cert_id: a763af37-4a43-4afd-807c-a140ecb9e781, panel_run_uid: f31f4fe7-3127-40e8-b0ae-18bcd46938e8, source: v2_panel_ready_retry }

# Fatal stops fired (§8.4)
fatal_stops:
  - fired_at: 2026-06-24T05:19:30Z
    trigger: "Service unavailable (§8.4)"
    halt_reason: |
      bc-core (port 3100) and bc-ai (port 4300) are not running.
      Pre-execution health checks via Node fetch returned "fetch failed" on both endpoints.
      Port-bind check via netstat shows neither port bound.
      F4-v2 v1 `POST /api/bcf/registry-authoring-runs` controller code exists in bc-core
      (registry-authoring-run.controller.ts:27) but the hosting service is offline.
      Per §8.4 fatal-stop list "Service unavailable" trigger this is a program-level halt,
      not a per-row park.
    pass_affected: pass_1
    wave_affected: C1
    rows_executed: 0
    rows_authored_active: 0
    rows_idempotent: 0
    rows_parked: 0
    rows_rejected: 0
    rows_blocked: 0
    substrate_mutations: 0
    panel_calls: 0
    llm_calls: 0
    db_writes: 0
    resolved: false
    unblock_condition: |
      Operator starts bc-core (requires Docker compose up -d in bc-core; then npm run start:dev)
      and bc-ai (uvicorn main:app --port 4300), verifies both reachable on health endpoints,
      then re-issues "Begin Pass 1 C1 under DEC-f94895" instruction.
      A0 / A0.5 / A1–A5 state is preserved; no re-recording needed.
    halt_session: SES-059790
```

> **Pass 1 C1 did NOT execute.** Pre-execution service-health gate failed; bc-core and bc-ai are not running. Per §8.4 + §8.5, the program halted before any panel call, substrate write, or row state change. A1–A5 `program_authorization=active` is preserved; resume requires the operator to start the services and re-issue the execution instruction.

## Ledger rows (Pass 3 BC binding view — primary)

Total 1112 non-metadata/runtime rows. Each row's full provenance available via candidateId + oagis_provenance JSON; full schema per blueprint §6.3.

**Note on row volume.** The ledger contains many rows. Sections below split by execution class for readability. The full row set lives in this file; an A0 Phase 2 DBCP candidate would persist these to `concept_registry.oagis_retry_ledger` (per blueprint §6.4 Phase 2).

### GREEN rows (27) — autonomous-safe

| candidate_id | wave | entity | char | rep_term/data_type/sem_role | packet_hash | terminal? |
|---|---|---|---|---|---|---|
| LDG-00009 | BC-AR | Customer Invoice | document date | date/timestamp/temporal | `sha256:755b55783f6fd6bbe559e4170adb5ac0` | authored_idempotent |
| LDG-00009 | BC-AP | Supplier Invoice | document date | date/timestamp/temporal | `sha256:ef77ae011b0e22c7d252ac65d5d77689` | authored_idempotent |
| LDG-00028 | BC-AR | Customer Invoice Line Item | line number | identifier/string/identifier | `sha256:ac65f6861097bc6e2fbd39bb9c1dadca` | authored_idempotent |
| LDG-00028 | BC-AP | Supplier Invoice Line | line number | identifier/string/identifier | `sha256:e803e57b74737c719ef24ba986d6e093` | authored_idempotent |
| LDG-00173 | BC-GL | Journal Entry | document date | date/timestamp/temporal | `sha256:55c9074bd0649d4d44b19bd0d2ba5131` | authored_idempotent |
| LDG-00186 | BC-GL | Journal Entry Line | line number | identifier/string/identifier | `sha256:d1b7f11abcf64a002fed9efdaa1e6829` | authored_idempotent |
| LDG-00233 | BC-AR | Credit Application | tax | identifier/string/identifier | `sha256:75527aec52375f6032215b3df5d16b40` |  |
| LDG-00258 | BC-AR | Credit Status | document date | date/timestamp/temporal | `sha256:9448cf8cf5afa4c63af41bda88e43594` |  |
| LDG-00268 | BC-AR | Remittance Advice | document date | date/timestamp/temporal | `sha256:6eb140d739e2c1e79d3a64855a04debe` | authored_idempotent |
| LDG-00277 | BC-AR | Remittance Advice | line number | identifier/string/identifier | `sha256:0ffd2265bf3255d8fb5cf0dfb9248a88` |  |
| LDG-00362 | BC-GL | GL Account | currency code | code/code/dimension | `sha256:1232fd39150c261dd6e2342a453e6c79` |  |
| LDG-00384 | BC-AR | Customer Payment | document date | date/timestamp/temporal | `sha256:e47a618356f035c765c49790fdcf53ea` | authored_idempotent |
| LDG-00384 | BC-AP | Vendor Payment | document date | date/timestamp/temporal | `sha256:111c55a66c5a3b3c85509f1e692cbab5` | authored_idempotent |
| LDG-00483 | BC-AP | Purchase Order | document date | date/timestamp/temporal | `sha256:b783bc32e128b597cda8c18c6a68f644` | authored_idempotent |
| LDG-00502 | BC-AP | Purchase Order Line | line number | identifier/string/identifier | `sha256:80a1e42f9aabdb762070c2966ac02831` | authored_idempotent |
| LDG-00729 | BC-AR | Customer Shipment | document date | date/timestamp/temporal | `sha256:da3c48bb2d79ac7be95f52becd2eba09` | authored_idempotent |
| LDG-00744 | BC-AR | Customer Shipment | country code | code/code/dimension | `sha256:2b2bc50c44b3ac5c177fac40e0a28bc0` |  |
| LDG-00998 | BC-AP | Goods Receipt | document date | date/timestamp/temporal | `sha256:cf01495a277fe92ea2137dfbe2063546` | authored_idempotent |
| LDG-01013 | BC-AP | Goods Receipt | country code | code/code/dimension | `sha256:5431eea4bbd1fb4621329014c677a0b1` |  |
| LDG-01045 | BC-AP | Goods Receipt Line | country code | code/code/dimension | `sha256:38c518d465f1bbcc70b7877adeba8bce` |  |
| LDG-01099 | BC-AP | Goods Receipt Line | line number | identifier/string/identifier | `sha256:17867acbe9a3acfe066cb690461dd666` | authored_idempotent |
| LDG-01410 | BC-AR | Sales Order | document date | date/timestamp/temporal | `sha256:0fc8fe9ccc8096523bfcd1076baaa2cc` | authored_idempotent |
| LDG-01427 | BC-AR | Sales Order Line | line number | identifier/string/identifier | `sha256:fabd81f8161aa002fd5dcc53621001fb` | authored_idempotent |
| LDG-02530 | BC-AP | Supplier | tax | identifier/string/identifier | `sha256:a859c3f9194f33630aed7e9bf123b0a0` |  |
| LDG-02546 | BC-AP | Supplier | currency code | code/code/dimension | `sha256:f0fbdf7a2fdd16ae91fd98b3bfb49aa5` | authored_idempotent |
| LDG-02556 | BC-AR | Customer | tax | identifier/string/identifier | `sha256:21e04c40f6b585b434696d6d97410c6b` |  |
| LDG-02572 | BC-AR | Customer | currency code | code/code/dimension | `sha256:910afaa153e1f963cb20ab544bb0db72` | authored_idempotent |


### AMBER rows (639) — require pin_evidence_text before autonomous execution

| candidate_id | wave | entity | char/proposed_term | rep_term/data_type | bucket | packet_hash |
|---|---|---|---|---|---|---|
| LDG-00012 | BC-AR | Customer Invoice | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:4006115a1c6ffeeeed426533d70a85a5` |
| LDG-00012 | BC-AP | Supplier Invoice | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:53f91236640e77bc357664e332714e04` |
| LDG-00015 | BC-AR | Customer Invoice | 🆕 total_charge_amount | amount/number | existing entity new characteristic | `sha256:7695b64b7860e72646dec56607b81acf` |
| LDG-00015 | BC-AP | Supplier Invoice | 🆕 total_charge_amount | amount/number | existing entity new characteristic | `sha256:a890aabbc5ee4c7c84b400dffce09804` |
| LDG-00016 | BC-AR | Customer Invoice | 🆕 total_allowance_amount | amount/number | existing entity new characteristic | `sha256:de7c3466c26033a1e326ab329b42f1c0` |
| LDG-00016 | BC-AP | Supplier Invoice | 🆕 total_allowance_amount | amount/number | existing entity new characteristic | `sha256:735bc1b1208f2d62e9a837d891707f03` |
| LDG-00017 | BC-AR | Customer Invoice | 🆕 transportation_method_code | code/code | existing entity new characteristic | `sha256:60f15c1fba82166922f1ac3c8b0e0183` |
| LDG-00017 | BC-AP | Supplier Invoice | 🆕 transportation_method_code | code/code | existing entity new characteristic | `sha256:99529ef229c096324bb6268b1493905c` |
| LDG-00018 | BC-AR | Customer Invoice | 🆕 dunnage_weight_measure | quantity/number | existing entity new characteristic | `sha256:d7dc2d6650a3763e47abcc30dfa1b25d` |
| LDG-00018 | BC-AP | Supplier Invoice | 🆕 dunnage_weight_measure | quantity/number | existing entity new characteristic | `sha256:9c6833bba37317c650532c54613ca653` |
| LDG-00019 | BC-AR | Customer Invoice | 🆕 tare_weight_measure | quantity/number | existing entity new characteristic | `sha256:e2fc021aab7af1c5ff4e1a9c7c2bb0cb` |
| LDG-00019 | BC-AP | Supplier Invoice | 🆕 tare_weight_measure | quantity/number | existing entity new characteristic | `sha256:111c11a282f079a6c72edaa0ceb6e7b9` |
| LDG-00020 | BC-AR | Customer Invoice | net weight | quantity/number | existing entity existing characteristic bc | `sha256:9ee06ccdbd2bd66438fbfcbe05dd2b8a` |
| LDG-00020 | BC-AP | Supplier Invoice | net weight | quantity/number | existing entity existing characteristic bc | `sha256:05889c7331c4b4fd43ec9c3637d35378` |
| LDG-00021 | BC-AR | Customer Invoice | gross weight | quantity/number | existing entity existing characteristic bc | `sha256:0b79ae2f39ed713343e65c22c2fb2184` |
| LDG-00021 | BC-AP | Supplier Invoice | gross weight | quantity/number | existing entity existing characteristic bc | `sha256:ce5c019386621d2b9ace5727c8e8dceb` |
| LDG-00022 | BC-AR | Customer Invoice | volume | quantity/number | existing entity existing characteristic bc | `sha256:a38bd6e7dd02284a900b1bab7164d11e` |
| LDG-00022 | BC-AP | Supplier Invoice | volume | quantity/number | existing entity existing characteristic bc | `sha256:0b5a6ce10fb1aec9a6bfdba0408d4d6b` |
| LDG-00024 | BC-AR | Customer Invoice | 🆕 requested_delivery_date | date/date | existing entity new characteristic | `sha256:273e669380a7287ccff85ab560dea063` |
| LDG-00024 | BC-AP | Supplier Invoice | 🆕 requested_delivery_date | date/date | existing entity new characteristic | `sha256:1f259733bfef2f1935801cc377c69e8e` |
| LDG-00025 | BC-AR | Customer Invoice | delivery date | date/timestamp | existing entity existing characteristic bc | `sha256:ba033f8e866be2922d3610d6cc2d8dbb` |
| LDG-00025 | BC-AP | Supplier Invoice | delivery date | date/timestamp | existing entity existing characteristic bc | `sha256:472ec9ae8d632cd7e008ab95c9517f1b` |
| LDG-00026 | BC-AR | Customer Invoice Line Item | 🆕 type_code | code/code | existing entity new characteristic | `sha256:83e5e4c3904cc8381d6b3532875e04dd` |
| LDG-00026 | BC-AP | Supplier Invoice Line | 🆕 type_code | code/code | existing entity new characteristic | `sha256:33817864ded806bc6d5cb76793b6abfa` |
| LDG-00031 | BC-AR | Customer Invoice Line Item | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:bd6fd3719f0f1536469aebfa925c582e` |
| LDG-00031 | BC-AP | Supplier Invoice Line | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:b241cf3dc36308e0a71ca427ff158b76` |
| LDG-00033 | BC-AR | Customer Invoice Line Item | 🆕 goods_receipt_date_time | date/timestamp | existing entity new characteristic | `sha256:e08393a83dba30e7a7681dad089fdbf2` |
| LDG-00033 | BC-AP | Supplier Invoice Line | 🆕 goods_receipt_date_time | date/timestamp | existing entity new characteristic | `sha256:d3d1c8551c0e06606c9ef1064fc4720b` |
| LDG-00034 | BC-AR | Customer Invoice Line Item | 🆕 services_receipt_date_time | date/timestamp | existing entity new characteristic | `sha256:c246e31ea7d05778bef0f623a03c8b89` |
| LDG-00034 | BC-AP | Supplier Invoice Line | 🆕 services_receipt_date_time | date/timestamp | existing entity new characteristic | `sha256:88fc5dcd674e475d606e8236bf88ef5d` |
| LDG-00035 | BC-AR | Customer Invoice Line Item | 🆕 requested_delivery_date | date/date | existing entity new characteristic | `sha256:a86e312a371d0bd0edc6ffa5485d47e1` |
| LDG-00035 | BC-AP | Supplier Invoice Line | 🆕 requested_delivery_date | date/date | existing entity new characteristic | `sha256:e972c6df6ac2329eb5f57fa5f658455d` |
| LDG-00036 | BC-AR | Customer Invoice Line Item | delivery date | date/timestamp | existing entity existing characteristic bc | `sha256:9b146b5f75b3ba56e288528df4b04067` |
| LDG-00036 | BC-AP | Supplier Invoice Line | delivery date | date/timestamp | existing entity existing characteristic bc | `sha256:1a34ee5c9f6cdbaf3e2977071fdcd793` |
| LDG-00048 | BC-AP | Supplier Invoice | 🆕 ledger_identifier | identifier/string | existing entity new characteristic | `sha256:98149431fb11b50911df986c0d92a6f8` |
| LDG-00049 | BC-AP | Supplier Invoice | 🆕 gl_entity_identifier | identifier/string | existing entity new characteristic | `sha256:555923e8717673d2bba21a1eb31ad120` |
| LDG-00050 | BC-AP | Supplier Invoice | 🆕 amount | amount/number | existing entity new characteristic | `sha256:0739180a91d41823efe0d02c7bfd706a` |
| LDG-00051 | BC-AP | Supplier Invoice | debit credit code | code/code | existing entity existing characteristic bc | `sha256:d94e24df72ec2a173b2c358e3e39c69e` |
| LDG-00052 | BC-AP | Supplier Invoice | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:b50ee52982525dbcc8d6c742f2b7254b` |
| LDG-00053 | BC-AP | Supplier Invoice | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:61f46d73581c06dd620a7e0b15cbea17` |
| LDG-00054 | BC-AP | Supplier Invoice | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:c2b7e0457b2acefaf724c58e4bf5bfde` |
| LDG-00060 | BC-AP | Supplier Invoice Line | 🆕 gl_destination_entity_identifier | identifier/string | existing entity new characteristic | `sha256:85dbf03c013f68ebc94d2ebed31befea` |
| LDG-00061 | BC-AP | Supplier Invoice Line | 🆕 amount | amount/number | existing entity new characteristic | `sha256:ba23825c62b2a7ceb46ae73687f3e56f` |
| LDG-00062 | BC-AP | Supplier Invoice Line | debit credit code | code/code | existing entity existing characteristic bc | `sha256:df11b4656474a9a03a8167421e481672` |
| LDG-00063 | BC-AP | Supplier Invoice Line | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:e389f8f54092e2ef3f373b2aee8f5d53` |
| LDG-00064 | BC-AP | Supplier Invoice Line | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:4bd4c7680d312d1874f8024123903305` |
| LDG-00065 | BC-AP | Supplier Invoice Line | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:1a9246b65d3ad33aa180e730c03d5ff3` |
| LDG-00099 | BC-AP | Supplier Invoice Line | ship date | date/timestamp | existing entity existing characteristic bc | `sha256:7aa39a92fd1d648ae1b973e82fa8e4d3` |
| LDG-00100 | BC-AP | Supplier Invoice Line | 🆕 dunnage_weight_measure | quantity/number | existing entity new characteristic | `sha256:1e54c753dd88126ac61889879e78fff6` |
| LDG-00101 | BC-AP | Supplier Invoice Line | 🆕 tare_weight_measure | quantity/number | existing entity new characteristic | `sha256:350c372ccf2d30bb0db8a200f51c2a85` |
| LDG-00102 | BC-AP | Supplier Invoice Line | net weight | quantity/number | existing entity existing characteristic bc | `sha256:60b9968b330a2437ae70234153ea2830` |
| LDG-00103 | BC-AP | Supplier Invoice Line | gross weight | quantity/number | existing entity existing characteristic bc | `sha256:db96da398018a69f89b399d111866e23` |
| LDG-00104 | BC-AP | Supplier Invoice Line | volume | quantity/number | existing entity existing characteristic bc | `sha256:4a7aaf37964f039d9a51e313ae0e8679` |
| LDG-00121 | BC-AR | Customer Invoice | 🆕 total_value_amount | amount/number | existing entity new characteristic | `sha256:bf47493ea51427d2924358e33552a74c` |
| LDG-00121 | BC-AP | Supplier Invoice | 🆕 total_value_amount | amount/number | existing entity new characteristic | `sha256:846857a1e42746e51f3ab2610022b6bc` |
| LDG-00127 | BC-AR | Customer Invoice Line Item | 🆕 harmonized_tariff_schedule_code | code/code | existing entity new characteristic | `sha256:a2ba5b7d8abbb70ebe3568392c769896` |
| LDG-00127 | BC-AP | Supplier Invoice Line | 🆕 harmonized_tariff_schedule_code | code/code | existing entity new characteristic | `sha256:8a9e2a156a457af99d5d0c7e0005dc7d` |
| LDG-00128 | BC-Logistics | Three-Way Match Document | 🆕 type_code | code/code | new entity new characteristic | `sha256:1278fc8cc527e85f2862a0c561fcf51c` |
| LDG-00138 | BC-Logistics | Three-Way Match Document | document date | date/timestamp | new entity existing characteristic | `sha256:eb256f5433f789eccefeb0cbe181b48e` |
| LDG-00141 | BC-Logistics | Three-Way Match Document | 🆕 document_type | text/string | new entity new characteristic | `sha256:ec5ed50025f0117542c8ef7c7e29bd03` |
| LDG-00142 | BC-Logistics | Three-Way Match Document | 🆕 ledger_identifier | identifier/string | new entity new characteristic | `sha256:1987e2fabcd368aa98ddb43d596ebb3b` |
| LDG-00143 | BC-Logistics | Three-Way Match Document | 🆕 amount | amount/number | new entity new characteristic | `sha256:8fbe25a43195ee0deea658e070a04b3e` |
| LDG-00144 | BC-Logistics | Three-Way Match Document | debit credit code | code/code | new entity existing characteristic | `sha256:45af29607938dc9b37105ae3f0c8627e` |
| LDG-00145 | BC-Logistics | Three-Way Match Document | 🆕 tax_base_amount | amount/number | new entity new characteristic | `sha256:7d36fa0394b4e14e18fa75818b23552a` |
| LDG-00146 | BC-Logistics | Three-Way Match Document | 🆕 functional_amount | amount/number | new entity new characteristic | `sha256:c5c9a2db6f2a9c8c97799b95b0d7aa44` |
| LDG-00147 | BC-Logistics | Three-Way Match Document | 🆕 tax_base_functional_amount | amount/number | new entity new characteristic | `sha256:0788ae11027ff16f3350c22c447f0f58` |
| LDG-00148 | BC-Logistics | Three-Way Match Document | 🆕 gl_entity_identifier | identifier/string | new entity new characteristic | `sha256:3bf97c9e7c304fb430a99f3f0759f939` |
| LDG-00149 | BC-Logistics | Three-Way Match Document | 🆕 remittance_identifier | identifier/string | new entity new characteristic | `sha256:ddd3a296d380cf17598e93a8b1f0dfef` |
| LDG-00150 | BC-Logistics | Three-Way Match Document | 🆕 payment_method_code | code/code | new entity new characteristic | `sha256:ffab95755eb9cce1f6462ccdb8d5502d` |
| LDG-00151 | BC-Logistics | Three-Way Match Document | 🆕 special_price_authorization_code | code/code | new entity new characteristic | `sha256:f7134344222d87f00247ba0bed989147` |
| LDG-00152 | BC-Logistics | Three-Way Match Document | 🆕 release_number_identifier | identifier/string | new entity new characteristic | `sha256:199e7d93701501af285dab22b2b3bf69` |
| LDG-00153 | BC-Logistics | Three-Way Match Document Line | 🆕 type_code | code/code | new entity new characteristic | `sha256:cb01c62ebd028c996710acd741312f46` |
| LDG-00155 | BC-Logistics | Three-Way Match Document Line | line number | identifier/string | new entity existing characteristic | `sha256:95d8da009ec563884067bf689dadc78c` |
| LDG-00158 | BC-Logistics | Three-Way Match Document Line | 🆕 financial_match_code | code/code | new entity new characteristic | `sha256:ca64726225ae1f64481c917dfb2faeb8` |
| LDG-00159 | BC-Logistics | Three-Way Match Document Line | 🆕 amount | amount/number | new entity new characteristic | `sha256:22122fdc964ecc5ff491221a4a0919f1` |
| LDG-00160 | BC-Logistics | Three-Way Match Document Line | debit credit code | code/code | new entity existing characteristic | `sha256:5335538458599b953148b359334dcfa9` |
| LDG-00161 | BC-Logistics | Three-Way Match Document Line | 🆕 tax_base_amount | amount/number | new entity new characteristic | `sha256:2cb5d27aaf0d99b62c85b82788cc9811` |
| LDG-00162 | BC-Logistics | Three-Way Match Document Line | 🆕 functional_amount | amount/number | new entity new characteristic | `sha256:30d9ee120dfc45adca55ec97b605d991` |
| LDG-00163 | BC-Logistics | Three-Way Match Document Line | 🆕 tax_base_functional_amount | amount/number | new entity new characteristic | `sha256:9c2205dba4880fde6812aaaa9e735d4e` |
| LDG-00164 | BC-Logistics | Three-Way Match Document Line | 🆕 gl_destination_entity_identifier | identifier/string | new entity new characteristic | `sha256:66c05b05ac1d410638b133d02a6b92b1` |
| LDG-00176 | BC-GL | Journal Entry | 🆕 ledger_identifier | identifier/string | existing entity new characteristic | `sha256:94c66a4ab67f36755dfe1e5d8fcd6ca0` |
| LDG-00177 | BC-GL | Journal Entry | 🆕 gl_entity_identifier | identifier/string | existing entity new characteristic | `sha256:a7ee948f8d98c97120a2999c571a738d` |
| LDG-00178 | BC-GL | Journal Entry | 🆕 amount | amount/number | existing entity new characteristic | `sha256:9a0e6812114f3c18f4822153a5e9a8dd` |
| LDG-00179 | BC-GL | Journal Entry | debit credit code | code/code | existing entity existing characteristic bc | `sha256:9d48e01b76e3804582137bf12bba933b` |
| LDG-00180 | BC-GL | Journal Entry | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:8ae4813c90efc783d50b119c74b2908e` |
| LDG-00181 | BC-GL | Journal Entry | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:c1d090929aa9a7f4f34f2e3930ea7bef` |
| LDG-00182 | BC-GL | Journal Entry | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:279287fc5d7c2612746c5360d69a88b4` |
| LDG-00183 | BC-GL | Journal Entry | 🆕 remittance_identifier | identifier/string | existing entity new characteristic | `sha256:476e2f0115898b98501785c7194fa4e0` |
| LDG-00184 | BC-GL | Journal Entry Line | 🆕 type_code | code/code | existing entity new characteristic | `sha256:6c46ad084e7aecc25319be94cab38613` |
| LDG-00189 | BC-GL | Journal Entry Line | 🆕 gl_destination_entity_identifier | identifier/string | existing entity new characteristic | `sha256:5674f23b74b588406ace40450f010757` |
| LDG-00190 | BC-GL | Journal Entry Line | 🆕 amount | amount/number | existing entity new characteristic | `sha256:0a95527982d1b35b51445288dea79cef` |
| LDG-00191 | BC-GL | Journal Entry Line | debit credit code | code/code | existing entity existing characteristic bc | `sha256:7a4862f07739d523fd1a25422b919006` |
| LDG-00192 | BC-GL | Journal Entry Line | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:788a84e7af4ccbbc1da6e10d5256942d` |
| LDG-00193 | BC-GL | Journal Entry Line | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:17d325f66d438244d4b1a643319ab73f` |
| LDG-00194 | BC-GL | Journal Entry Line | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:29e9b966319bb18f4a3db521b6d377b9` |
| LDG-00207 | BC-AR | Customer Invoice | 🆕 ledger_identifier | identifier/string | existing entity new characteristic | `sha256:6493f90299b51a04f1af037a14441b1a` |
| LDG-00208 | BC-AR | Customer Invoice | 🆕 gl_entity_identifier | identifier/string | existing entity new characteristic | `sha256:47d996d70e9e3eba2241bc35aac89592` |
| LDG-00209 | BC-AR | Customer Invoice | 🆕 amount | amount/number | existing entity new characteristic | `sha256:e99da0c5a562b40aaa59b3aa0cda99e1` |
| LDG-00210 | BC-AR | Customer Invoice | debit credit code | code/code | existing entity existing characteristic bc | `sha256:187188b365b1ca41f2b4dad2b8e25cf4` |
| LDG-00211 | BC-AR | Customer Invoice | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:ccb2083f3ed9c59887e463ad321e733c` |
| LDG-00212 | BC-AR | Customer Invoice | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:c1d5590e385ce9788180611968f86916` |
| LDG-00213 | BC-AR | Customer Invoice | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:831cb534a31aa0ee85b1aba8399d0d79` |
| LDG-00219 | BC-AR | Customer Invoice Line Item | 🆕 gl_destination_entity_identifier | identifier/string | existing entity new characteristic | `sha256:c3c8750b1f36ad864a7494ab0e9ae676` |
| LDG-00220 | BC-AR | Customer Invoice Line Item | 🆕 amount | amount/number | existing entity new characteristic | `sha256:8da0f6511472cd6273c8d3fd18bff4a8` |
| LDG-00221 | BC-AR | Customer Invoice Line Item | debit credit code | code/code | existing entity existing characteristic bc | `sha256:a5bec7dee61cbda28d9b35f3ef975752` |
| LDG-00222 | BC-AR | Customer Invoice Line Item | 🆕 tax_base_amount | amount/number | existing entity new characteristic | `sha256:e24e530c5584f29e98c3dd7cca2d4004` |
| LDG-00223 | BC-AR | Customer Invoice Line Item | 🆕 functional_amount | amount/number | existing entity new characteristic | `sha256:bb475f2fddd006245982a02bce1c1966` |
| LDG-00224 | BC-AR | Customer Invoice Line Item | 🆕 tax_base_functional_amount | amount/number | existing entity new characteristic | `sha256:c814e5a4a6bad674fe40bcb71e642e0b` |
| LDG-00226 | BC-AR | Credit Application | 🆕 type_code | code/code | existing entity new characteristic | `sha256:b3517f76717ff8b76fe17b361b0c108f` |
| LDG-00231 | BC-AR | Credit Application | 🆕 account_identifier | identifier/string | existing entity new characteristic | `sha256:666546023a63eeec94559251a2de1a54` |
| LDG-00240 | BC-AR | Credit Application | 🆕 government_issued_party_identifier | identifier/string | existing entity new characteristic | `sha256:5f4f03629d48debe0976172b2966bc4a` |
| LDG-00244 | BC-AR | Credit Status | 🆕 type_code | code/code | existing entity new characteristic | `sha256:05e157bfebe60e3da8631f9f19602fd9` |
| LDG-00252 | BC-AR | Credit Status | 🆕 open_item_amount | amount/number | existing entity new characteristic | `sha256:ce189f600205a22b0a03eb5f05ff0b7b` |
| LDG-00253 | BC-AR | Credit Status | 🆕 order_amount | amount/number | existing entity new characteristic | `sha256:5eac27c2f81ffe05711784916d5c57c4` |
| LDG-00254 | BC-AR | Credit Status | 🆕 approved_order_amount | amount/number | existing entity new characteristic | `sha256:3b124624b16e785ba4c43ea5b864d629` |
| LDG-00255 | BC-AR | Credit Status | 🆕 available_amount | amount/number | existing entity new characteristic | `sha256:43d78f56b84ef4af9ab8064b8a1f4076` |
| LDG-00256 | BC-AR | Credit Status | 🆕 order_limit_amount | amount/number | existing entity new characteristic | `sha256:867392bfd577bb1d18b07794b87d09ab` |
| LDG-00257 | BC-AR | Credit Status | 🆕 total_credit_limit_amount | amount/number | existing entity new characteristic | `sha256:4f702f9bbfd51928dbd78ee92b0232ba` |
| LDG-00259 | BC-AR | Credit Status | 🆕 ledger_identifier | identifier/string | existing entity new characteristic | `sha256:4b66323dab3a98feb466b5127e4616e6` |
| LDG-00271 | BC-AR | Remittance Advice | effective date | date/date | existing entity existing characteristic bc | `sha256:ae4910b9228954fb871fe1d793893d05` |
| LDG-00272 | BC-AR | Remittance Advice | 🆕 payment_method_code | code/code | existing entity new characteristic | `sha256:d47462bcaa26c032aca01c2197509894` |
| LDG-00274 | BC-AR | Remittance Advice | 🆕 transaction_identifier | identifier/string | existing entity new characteristic | `sha256:585cd4b25b487f2c4bd6d5516ddc4e51` |
| LDG-00275 | BC-AR | Remittance Advice | 🆕 type_code | code/code | existing entity new characteristic | `sha256:73377c8d2130ad141635d7ab900e1d03` |
| LDG-00280 | BC-AR | Remittance Advice | payment amount | amount/number | existing entity existing characteristic bc | `sha256:5f206a037781db2558032a657de9922d` |
| LDG-00311 | BC-GL | Journal Entry | 🆕 type_code | code/code | existing entity new characteristic | `sha256:0e48fe6a0e6f66a544e17a462ceca1a0` |
| LDG-00324 | BC-GL | Journal Entry | 🆕 gl_destination_entity_identifier | identifier/string | existing entity new characteristic | `sha256:5a77db4f1b232116e5f0318af4f4a09a` |
| LDG-00326 | BC-GL | Journal Entry | 🆕 transaction_analysis_code | code/code | existing entity new characteristic | `sha256:ec36903dd0612c9881dbc5d3e15a08af` |
| LDG-00335 | BC-Reference | Budget Ledger Entry | document date | date/timestamp | new entity existing characteristic | `sha256:8e6306f2bbe2c0471025c8e833950fbc` |
| LDG-00339 | BC-Reference | Budget Ledger Entry | 🆕 journal_entry_identifier | identifier/string | new entity new characteristic | `sha256:9b808e34d1d3ec58bc85588adb10a7fb` |
| LDG-00340 | BC-Reference | Budget Ledger Entry | 🆕 ledger_identifier | identifier/string | new entity new characteristic | `sha256:152cf299c2c0e2bba703979c4a1f766c` |
| LDG-00341 | BC-Reference | Budget Ledger Entry | 🆕 gl_entity_identifier | identifier/string | new entity new characteristic | `sha256:c3bd3dd78eb11129d40ccb6da26cf77f` |
| LDG-00342 | BC-Reference | Budget Ledger Entry | 🆕 transaction_analysis_code | code/code | new entity new characteristic | `sha256:5bcd0626423e6103d9daa984e61b2471` |
| LDG-00343 | BC-Reference | Budget Ledger Entry Line | 🆕 type_code | code/code | new entity new characteristic | `sha256:ffb094d7d3e02e97c47bf816cfa02bd7` |
| LDG-00345 | BC-Reference | Budget Ledger Entry Line | line number | identifier/string | new entity existing characteristic | `sha256:00cd70839d4cfe05bac1f31aed945387` |
| LDG-00348 | BC-Reference | Budget Ledger Entry Line | 🆕 amount | amount/number | new entity new characteristic | `sha256:4700c0fcb391dfd2f2c09b7e46044d76` |
| LDG-00349 | BC-Reference | Budget Ledger Entry Line | debit credit code | code/code | new entity existing characteristic | `sha256:b9fb1d9fac308eb66a1d60f84cd48583` |
| LDG-00350 | BC-Reference | Budget Ledger Entry Line | 🆕 tax_base_amount | amount/number | new entity new characteristic | `sha256:271e671283bd77fed4cd1a5605ceff34` |
| LDG-00351 | BC-Reference | Budget Ledger Entry Line | 🆕 functional_amount | amount/number | new entity new characteristic | `sha256:55b95aecd5ce0dbab448454a26ccb5dc` |
| LDG-00352 | BC-Reference | Budget Ledger Entry Line | 🆕 tax_base_functional_amount | amount/number | new entity new characteristic | `sha256:a9c976a3d33947fb0b08d739271b78a2` |
| LDG-00353 | BC-GL | GL Account | 🆕 type_code | code/code | existing entity new characteristic | `sha256:085314dfdc1ffa16d744b84b0f53896a` |
| LDG-00359 | BC-GL | GL Account | 🆕 gl_entity_identifier | identifier/string | existing entity new characteristic | `sha256:380417a25a0b43633bf5c24c3b220c9d` |
| LDG-00360 | BC-GL | GL Account | 🆕 general_ledger_nominal_account | text/string | existing entity new characteristic | `sha256:533fa9ba429c58e17c955e58407686f1` |
| LDG-00361 | BC-GL | GL Account | account type code | code/code | existing entity existing characteristic bc | `sha256:7a66a25e7dabbb0fcb0f535f2670ed3a` |
| LDG-00375 | BC-GL | GL Account | 🆕 date_time | date/timestamp | existing entity new characteristic | `sha256:4ef15c957d5b346f347dba2e0e100223` |
| LDG-00387 | BC-AR | Customer Payment | 🆕 authorization_identifier | identifier/string | existing entity new characteristic | `sha256:c69bf6a23479c5d93181c9eaf72c394a` |
| LDG-00387 | BC-AP | Vendor Payment | 🆕 authorization_identifier | identifier/string | existing entity new characteristic | `sha256:4650cfb996593a3b2025d9ac1ec6a9e4` |
| LDG-00388 | BC-AR | Customer Payment | 🆕 type_code | code/code | existing entity new characteristic | `sha256:f3c2f824197bf69693e737358566b338` |
| LDG-00388 | BC-AP | Vendor Payment | 🆕 type_code | code/code | existing entity new characteristic | `sha256:171fa7a4d09343969add1ac85e2c6239` |
| LDG-00394 | BC-AR | Customer Payment | 🆕 requested_execution_date_time | date/timestamp | existing entity new characteristic | `sha256:9a6a39eb47f05dcc642db6dd9baea2f9` |
| LDG-00394 | BC-AP | Vendor Payment | 🆕 requested_execution_date_time | date/timestamp | existing entity new characteristic | `sha256:c0e3cef3f5e1e4383f6b1d61e832cb67` |
| LDG-00395 | BC-AR | Customer Payment | 🆕 first_agent_payment_method_code | code/code | existing entity new characteristic | `sha256:c0960cb54d5513f9f88411abdbad2c84` |
| LDG-00395 | BC-AP | Vendor Payment | 🆕 first_agent_payment_method_code | code/code | existing entity new characteristic | `sha256:8c4cd52e2e32c7809221d438afaa4476` |
| LDG-00441 | BC-Bank | Currency Exchange Rate | 🆕 type_code | code/code | existing entity new characteristic | `sha256:ec4f012cad0957b3a79db40b80d6eda1` |
| LDG-00447 | BC-Bank | Currency Exchange Rate | source currency code | code/code | existing entity existing characteristic bc | `sha256:951ec9834925386ffdfae9c4e6a3f3aa` |
| LDG-00448 | BC-Bank | Currency Exchange Rate | target currency code | code/code | existing entity existing characteristic bc | `sha256:17d3cff6a4a12dba4d9a103893071035` |
| LDG-00449 | BC-Bank | Currency Exchange Rate | 🆕 set_date_time | date/timestamp | existing entity new characteristic | `sha256:1c92bed81af29d8b2fcad35ab9e374fa` |
| LDG-00450 | BC-Master | Cost Centre | 🆕 type_code | code/code | new entity new characteristic | `sha256:aadf48b2b8fe4026d632c4b9a030eee1` |
| LDG-00457 | BC-Master | Cost Centre | 🆕 gl_entity_identifier | identifier/string | new entity new characteristic | `sha256:afa49d948f6591aa7e5ac488bbe91995` |
| LDG-00458 | BC-Master | Cost Centre | document date | date/timestamp | new entity existing characteristic | `sha256:8bab085537e127650e8bc862323008d7` |
| LDG-00460 | BC-Master | Cost Centre | 🆕 activity_date_time | date/timestamp | new entity new characteristic | `sha256:4ca6a1eb979a368823c7a3eefdd726d2` |
| LDG-00461 | BC-Master | Project | 🆕 type_code | code/code | new entity new characteristic | `sha256:2dca592a82e166f44f241ad64e38b36a` |
| LDG-00468 | BC-Master | Project | 🆕 amount | amount/number | new entity new characteristic | `sha256:004b981b13ca2e67d9fdaa691e006f1b` |
| LDG-00468 | BC-Master | Cost Centre | 🆕 amount | amount/number | new entity new characteristic | `sha256:8724ccc9c1fb21539df88bd98e3c3fdc` |
| LDG-00469 | BC-Master | Project | 🆕 activity_identifier | identifier/string | new entity new characteristic | `sha256:2796c921288b37a5619bf297cf421ccf` |
| LDG-00469 | BC-Master | Cost Centre | 🆕 activity_identifier | identifier/string | new entity new characteristic | `sha256:73095ce651389693fdc3b583e29916c1` |
| LDG-00470 | BC-Master | Project | 🆕 payment_date_time | date/timestamp | new entity new characteristic | `sha256:19276f3db5c6a775b1d2ebc8da51cff1` |
| LDG-00470 | BC-Master | Cost Centre | 🆕 payment_date_time | date/timestamp | new entity new characteristic | `sha256:5ec2578572c2d1f4ece853a783a7864e` |
| LDG-00472 | BC-Master | Project | 🆕 employee_identifier | identifier/string | new entity new characteristic | `sha256:9b66a8d5f592d542d2589fcee6a79fff` |
| LDG-00472 | BC-Master | Cost Centre | 🆕 employee_identifier | identifier/string | new entity new characteristic | `sha256:824476d4f813d7c8312a6b64007a31c1` |
| LDG-00473 | BC-Master | Project | 🆕 fixed_asset_identifier | identifier/string | new entity new characteristic | `sha256:a8ede06ecba89e58d81355aac664d985` |
| LDG-00473 | BC-Master | Cost Centre | 🆕 fixed_asset_identifier | identifier/string | new entity new characteristic | `sha256:dbb7267403941c559d075e9e50587670` |
| LDG-00474 | BC-Master | Project | 🆕 job_code | code/code | new entity new characteristic | `sha256:1199e1142c70eafe2eee4993d21c4da1` |
| LDG-00474 | BC-Master | Cost Centre | 🆕 job_code | code/code | new entity new characteristic | `sha256:e14e20aa12b535465940583896a3f3f4` |
| LDG-00486 | BC-AP | Purchase Order | 🆕 system_identifier | identifier/string | existing entity new characteristic | `sha256:df41493f94fee9fd328960cf60946727` |
| LDG-00487 | BC-AP | Purchase Order | 🆕 cost_center_identifier | identifier/string | existing entity new characteristic | `sha256:4c811636ffb2ffe8383222b839d54a8e` |
| LDG-00488 | BC-AP | Purchase Order | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:9908663b593da47ad606b062c9a8fdb9` |
| LDG-00490 | BC-AP | Purchase Order | 🆕 special_price_authorization_code | code/code | existing entity new characteristic | `sha256:0242a1734107aecee7ccd33eb1f7d522` |
| LDG-00491 | BC-AP | Purchase Order | 🆕 earliest_ship_date_time | date/timestamp | existing entity new characteristic | `sha256:a016da13136c730572e5344b0209fa83` |
| LDG-00492 | BC-AP | Purchase Order | ship date | date/timestamp | existing entity existing characteristic bc | `sha256:6b055eb2887afc4a2bddb6453276db4c` |
| LDG-00493 | BC-AP | Purchase Order | 🆕 promised_ship_date_time | date/timestamp | existing entity new characteristic | `sha256:1e20684cbeb41b31fe070a90cb87b2c6` |
| LDG-00494 | BC-AP | Purchase Order | 🆕 promised_delivery_date_time | date/timestamp | existing entity new characteristic | `sha256:13c3cd21728f4f3baa078cffb37411bf` |
| LDG-00495 | BC-AP | Purchase Order | 🆕 payment_method_code | code/code | existing entity new characteristic | `sha256:5a08151bf955d62c40941733ca438719` |
| LDG-00496 | BC-AP | Purchase Order | 🆕 shipping_instructions | text/string | existing entity new characteristic | `sha256:bf259d026bf7d7f1a442911b3f2d98b4` |
| LDG-00498 | BC-AP | Purchase Order | 🆕 accept_by_date_time | date/timestamp | existing entity new characteristic | `sha256:85d7a6e132252380e0135037b0a07ee9` |
| LDG-00499 | BC-AP | Purchase Order | 🆕 release_number_identifier | identifier/string | existing entity new characteristic | `sha256:9ba290f6405c7d8da45cdee2dc8f57cf` |
| LDG-00500 | BC-AP | Purchase Order Line | 🆕 type_code | code/code | existing entity new characteristic | `sha256:d73754ab617f202853668248bb00c30b` |
| LDG-00505 | BC-AP | Purchase Order Line | line extension amount | amount/number | existing entity existing characteristic bc | `sha256:89dc2a7d42dc348ec4fc6950f51fefca` |
| LDG-00507 | BC-AP | Purchase Order Line | 🆕 required_delivery_date_time | date/timestamp | existing entity new characteristic | `sha256:ec9a0d8ae97b70ff3b02861782b7838c` |
| LDG-00508 | BC-AP | Purchase Order Line | 🆕 special_price_authorization_code | code/code | existing entity new characteristic | `sha256:8ddf2c675d03d0b3ddb7bec819d3579f` |
| LDG-00509 | BC-AP | Purchase Order Line | 🆕 promised_ship_date_time | date/timestamp | existing entity new characteristic | `sha256:a65b3d3e9e267cc376970d081a7fb71e` |
| LDG-00510 | BC-AP | Purchase Order Line | 🆕 promised_delivery_date_time | date/timestamp | existing entity new characteristic | `sha256:4d85db80648f3e597dcada362f6d8097` |
| LDG-00511 | BC-AP | Purchase Order Line | 🆕 shipping_instructions | text/string | existing entity new characteristic | `sha256:642a0fa346132d6eb60c1cf6be433bc6` |
| LDG-00520 | BC-Procurement | Purchase Requisition | document date | date/timestamp | new entity existing characteristic | `sha256:9a8c4f6128ad303701dbe4b85650715e` |
| LDG-00523 | BC-Procurement | Purchase Requisition | 🆕 system_identifier | identifier/string | new entity new characteristic | `sha256:0075220bf3d3326f76e40c198362d0d0` |
| LDG-00524 | BC-Procurement | Purchase Requisition | 🆕 cost_center_identifier | identifier/string | new entity new characteristic | `sha256:4df0c15861b4991e49f04472ed5663d8` |
| LDG-00525 | BC-Procurement | Purchase Requisition | line extension amount | amount/number | new entity existing characteristic | `sha256:76c3d1d26ffe8f3f9a95713565937d3b` |
| LDG-00527 | BC-Procurement | Purchase Requisition | 🆕 required_delivery_date_time | date/timestamp | new entity new characteristic | `sha256:be388b03bfcca7aece78fa8e91396287` |
| LDG-00528 | BC-Procurement | Purchase Requisition Line | 🆕 type_code | code/code | new entity new characteristic | `sha256:d0b2aa1cee5f8d9cd995082a185f2308` |
| LDG-00530 | BC-Procurement | Purchase Requisition Line | line number | identifier/string | new entity existing characteristic | `sha256:2c6480ba1dd3ec13cb9039b0ddbf5b63` |
| LDG-00533 | BC-Procurement | Purchase Requisition Line | line extension amount | amount/number | new entity existing characteristic | `sha256:db8c78b45b848d3ccac05667f1deb119` |

_+ 439 more AMBER rows omitted for brevity._


### RED rows (67) — held; composite-identity entity decision required

| candidate_id | wave | entity | proposed_char/existing_char | reason |
|---|---|---|---|---|
| LDG-00617 | BC-Inventory | Inventory Position | 🆕 type_code | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00628 | BC-Inventory | Inventory Position | 🆕 uid | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00630 | BC-Inventory | Inventory Position | 🆕 serial_number_identifier | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00631 | BC-Inventory | Inventory Position | 🆕 reference_designator_identifier | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00632 | BC-Inventory | Inventory Position | 🆕 find_number_identifier | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00635 | BC-Inventory | Inventory Position | country code | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00636 | BC-Inventory | Inventory Position | 🆕 expiration_date | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00637 | BC-Inventory | Inventory Position | 🆕 best_used_by_date | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00638 | BC-Inventory | Inventory Position | 🆕 gl_entity_identifier | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00640 | BC-Inventory | Inventory Position | 🆕 transaction_date_time | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00641 | BC-Inventory | Inventory Position | 🆕 storage_uom_code | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-00642 | BC-Inventory | Inventory Position | 🆕 actual_temperature | composite-identity entity (inventory-composite) — operator decision packet required |
| LDG-01106 | BC-Quality-composite | Inspection Lot | 🆕 type_code | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01115 | BC-Quality-composite | Inspection Lot | 🆕 title | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01116 | BC-Quality-composite | Inspection Lot | document date | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01119 | BC-Quality-composite | Inspection Lot | line number | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01591 | BC-Production-composite | Work Order Operation | 🆕 type_code | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01593 | BC-Production-composite | Work Order Operation | line number | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01596 | BC-Production-composite | Work Order Operation | 🆕 need_delivery_date | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01597 | BC-Production-composite | Work Order Operation | due date | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01598 | BC-Production-composite | Work Order Operation | 🆕 required_date_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01599 | BC-Production-composite | Work Order Operation | 🆕 available_date_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01649 | BC-Production-composite | Bill of Materials Line | 🆕 type_code | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01660 | BC-Production-composite | Bill of Materials Line | 🆕 uid | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01662 | BC-Production-composite | Bill of Materials Line | 🆕 serial_number_identifier | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01663 | BC-Production-composite | Bill of Materials Line | 🆕 reference_designator_identifier | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01664 | BC-Production-composite | Bill of Materials Line | 🆕 find_number_identifier | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01667 | BC-Production-composite | Bill of Materials Line | country code | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01668 | BC-Production-composite | Bill of Materials Line | 🆕 expiration_date | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01669 | BC-Production-composite | Bill of Materials Line | 🆕 best_used_by_date | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01670 | BC-Production-composite | Bill of Materials Line | 🆕 lead_time_duration | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01671 | BC-Production-composite | Bill of Materials Line | 🆕 required_percent | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01672 | BC-Production-composite | Bill of Materials Line | 🆕 substitute_item_identifier | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01702 | BC-Production-composite | Operation | 🆕 type_code | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01704 | BC-Production-composite | Operation | 🆕 year | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01705 | BC-Production-composite | Operation | 🆕 month | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01706 | BC-Production-composite | Operation | 🆕 start_date_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01707 | BC-Production-composite | Operation | 🆕 start_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01708 | BC-Production-composite | Operation | 🆕 duration | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01709 | BC-Production-composite | Operation | 🆕 end_date_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01710 | BC-Production-composite | Operation | 🆕 end_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01732 | BC-Production-composite | Work Order Operation | line extension amount | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01734 | BC-Production-composite | Work Order Operation | 🆕 required_delivery_date_time | composite-identity entity (production-composite) — operator decision packet required |
| LDG-01913 | BC-Quality-composite | Inspection Lot | 🆕 lab_request_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01914 | BC-Quality-composite | Inspection Lot | 🆕 lot_batch_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01916 | BC-Quality-composite | Inspection Lot | 🆕 received_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01917 | BC-Quality-composite | Inspection Lot | 🆕 scheduled_delivery_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01918 | BC-Quality-composite | Inspection Lot | 🆕 desired_completion_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-01919 | BC-Quality-composite | Inspection Lot | 🆕 planned_completion_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02069 | BC-Quality-composite | Test Result | document date | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02073 | BC-Quality-composite | Test Result | 🆕 lab_request_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02074 | BC-Quality-composite | Test Result | 🆕 inspection_order_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02075 | BC-Quality-composite | Test Result | 🆕 lot_batch_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02076 | BC-Quality-composite | Test Result | 🆕 manufacture_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02077 | BC-Quality-composite | Test Result | 🆕 received_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02078 | BC-Quality-composite | Test Result | 🆕 estimated_completion_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02079 | BC-Quality-composite | Test Result | 🆕 type_code | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02081 | BC-Quality-composite | Test Result | line number | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02084 | BC-Quality-composite | Test Result | 🆕 parent_sample_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02085 | BC-Quality-composite | Test Result | 🆕 parent_sample_container_identifier | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02086 | BC-Quality-composite | Test Result | 🆕 sampled_date_time | composite-identity entity (quality-composite) — operator decision packet required |
| LDG-02286 | BC-Asset | Maintenance Order Operation | 🆕 type_code | composite-identity entity (maintenance-composite) — operator decision packet required |
| LDG-02288 | BC-Asset | Maintenance Order Operation | line number | composite-identity entity (maintenance-composite) — operator decision packet required |
| LDG-02291 | BC-Asset | Maintenance Order Operation | 🆕 actual_duration | composite-identity entity (maintenance-composite) — operator decision packet required |
| LDG-02292 | BC-Asset | Maintenance Order Operation | 🆕 remaining_duration | composite-identity entity (maintenance-composite) — operator decision packet required |
| LDG-02293 | BC-Asset | Maintenance Order Operation | 🆕 estimated_duration | composite-identity entity (maintenance-composite) — operator decision packet required |
| LDG-02294 | BC-Asset | Maintenance Order Operation | 🆕 completion_date_time | composite-identity entity (maintenance-composite) — operator decision packet required |

### UNKNOWN rows (288) — fatal-stop trigger; operator triage required

| candidate_id | noun | component | bf_name | reason |
|---|---|---|---|---|
| LDG-00955 | carrier-route | carrier-route | type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00965 | carrier-route | carrier-route | document_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00968 | carrier-route | carrier-route | tracking_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00969 | carrier-route | carrier-route | pro_number_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00970 | carrier-route | carrier-route | actual_ship_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00971 | carrier-route | carrier-route | scheduled_delivery_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00972 | carrier-route | carrier-route | actual_delivery_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00973 | carrier-route | carrier-route | required_delivery_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00974 | carrier-route | carrier-route | promised_delivery_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00975 | carrier-route | carrier-route | loading_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00976 | carrier-route | carrier-route | earliest_ship_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00977 | carrier-route | carrier-route | promised_ship_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00978 | carrier-route | carrier-route | scheduled_ship_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00979 | carrier-route | carrier-route | point_of_loading_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00980 | carrier-route | carrier-route | point_of_shipment_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00981 | carrier-route | carrier-route | point_of_staging_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00982 | carrier-route | carrier-route | transportation_method_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00983 | carrier-route | carrier-route | dunnage_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00984 | carrier-route | carrier-route | tare_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00985 | carrier-route | carrier-route | net_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00986 | carrier-route | carrier-route | gross_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00987 | carrier-route | carrier-route | net_volume_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-00989 | carrier-route | carrier-route | latest_start_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01191 | shippers-export-declaration | shippers-export-declaration-header | document_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01194 | shippers-export-declaration | shippers-export-declaration-header | gross_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01195 | shippers-export-declaration | shippers-export-declaration-header | actual_ship_date | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01196 | shippers-export-declaration | shippers-export-declaration-line | type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01198 | shippers-export-declaration | shippers-export-declaration-line | line_number_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01201 | shippers-export-declaration | shippers-export-declaration-line | harmonized_tariff_schedule_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01210 | shippers-letter-of-instruction | shippers-letter-of-instruction-header | document_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01213 | shippers-letter-of-instruction | shippers-letter-of-instruction-header | gross_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01214 | shippers-letter-of-instruction | shippers-letter-of-instruction-header | actual_ship_date | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01215 | shippers-letter-of-instruction | shippers-letter-of-instruction-header | shipping_instructions | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01217 | shippers-letter-of-instruction | shippers-letter-of-instruction-line | type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01219 | shippers-letter-of-instruction | shippers-letter-of-instruction-line | line_number_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01222 | shippers-letter-of-instruction | shippers-letter-of-instruction-line | declared_value_amount | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01223 | shippers-letter-of-instruction | shippers-letter-of-instruction-line | harmonized_tariff_schedule_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01232 | hazardous-material-shipment-document | hazardous-material-shipment-document-header | document_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01235 | hazardous-material-shipment-document | hazardous-material-shipment-document-header | actual_ship_date | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01236 | hazardous-material-shipment-document | hazardous-material-shipment-document-header | gross_weight_measure | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01238 | hazardous-material-shipment-document | hazardous-material-shipment-document-header | transport_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01239 | hazardous-material-shipment-document | hazardous-material-shipment-document-line | type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01241 | hazardous-material-shipment-document | hazardous-material-shipment-document-line | line_number_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01244 | hazardous-material-shipment-document | hazardous-material-shipment-document-line | country_of_origin_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01253 | planning-schedule | planning-schedule-header | document_date_time | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01256 | planning-schedule | planning-schedule-header | date_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01257 | planning-schedule | planning-schedule-header | schedule_type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01258 | planning-schedule | planning-schedule-line | type_code | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01260 | planning-schedule | planning-schedule-line | line_number_identifier | noun not mapped (skip-class or unmapped); operator triage |
| LDG-01263 | planning-schedule | planning-schedule-line | engineering_change_date_time | noun not mapped (skip-class or unmapped); operator triage |

_+ 238 more UNKNOWN rows omitted for brevity._


### DEFER rows (91) — source-diagnostic / awaits pull

| candidate_id | noun | component | bf_name | bucket |
|---|---|---|---|---|
| LDG-00014 | invoice | invoice-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00066 | payable | payable-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00080 | freight-invoice | freight-invoice-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00195 | invoice-ledger-entry | invoice-ledger-entry-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00225 | receivable | receivable-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00234 | credit | credit-party | dunsid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00235 | credit | credit-party | cageid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00236 | credit | credit-party | dodaacid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00237 | credit | credit-party | bicid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00238 | credit | credit-party | scacid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00310 | journal-entry | journal-entry-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00325 | actual-ledger | actual-ledger | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00551 | rfq | rfq-header | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00625 | inventory-balance | inventory-balance | upcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00626 | inventory-balance | inventory-balance | epcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00639 | inventory-balance | inventory-balance | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00661 | inventory-consumption | inventory-consumption-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00680 | inventory-count | inventory-count-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00693 | issue-inventory | issue-inventory-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00700 | issue-inventory | issue-inventory-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00719 | move-inventory | move-inventory-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00764 | shipment | shipment-header | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00782 | shipment | shipment-item | upcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00783 | shipment | shipment-item | epcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00892 | shipment-schedule | shipment-schedule-line | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00929 | shipment-unit | shipment-unit-item | upcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-00930 | shipment-unit | shipment-unit-item | epcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01035 | receive-delivery | receive-delivery-item | upcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01036 | receive-delivery | receive-delivery-item | epcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01103 | receive-item | receive-item-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01141 | pick-list | pick-list-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01271 | planning-schedule | planning-schedule-line | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01301 | move-product | move-product-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01334 | move-product-forecast | move-product-forecast-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01354 | require-product | require-product | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01376 | product-availability | product-availability | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01458 | sales-lead | sales-lead-header | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01486 | opportunity | opportunity-header | stage_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01584 | production-order | production-order-header | priority_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01589 | production-order | production-order-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01657 | bom | bom-item-data | upcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01658 | bom | bom-item-data | epcid | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01746 | work-center | work-center | wage_group_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01794 | confirm-wip | confirm-wip-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01801 | confirm-wip | confirm-wip-line | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01814 | merge-wip | merge-wip-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01838 | move-wip | move-wip-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01855 | recover-wip | recover-wip-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01872 | split-wip | split-wip-header | reason_code | SOURCE_DIAGNOSTIC_DEFER |
| LDG-01898 | wip-status | wip-status | reason_code | SOURCE_DIAGNOSTIC_DEFER |

_+ 41 more DEFER rows omitted for brevity._


## Provenance + reproducibility

- **Coordinator run id:** `CRR-a0c24a`
- **Substrate snapshot hash:** `sha256:8bcfa7a0bd220e304d2526574f2e0a18c8aa5bcc9a3e5bc8557d76273f46653d`
- **OAGIS extract version:** OAGIS 10.12 / enriched 2026-05-15
- **A0 compile script:** `barecount-devhub/scripts/_a0-compile.mjs` (scratch; not committed)
- **Idempotent operation:** re-running A0 against an unchanged extract + unchanged substrate produces a bit-identical ledger seed (same candidateIds + same hashes).

## What this seed is NOT

- Not a panel run.
- Not a substrate write.
- Not an admission act.
- Not a certification.
- Not authorisation to execute. A1–A5 program approval is required.
