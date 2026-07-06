# Plan: Eliminate v1 contract god-table — complete in one session

## Locked Decisions (confirmed with user)

- master_industry → master_function → master_subfunction is final (D103)
- metric_domain / metric_subdomain removed — D103 moved to master tables
- Port 5434 is the current (and only) DB — old DB gone
- kpi_spec → metric_definition + metric_definition_knowledge (DEC-6)
- binding table → REMOVED (no replacement needed)
- findContractById requires category from caller
- API returns family-specific column names (source_contract_name, not generic name)
- Complete everything this session — no partial states

## v2 Drizzle schemas already exist and match DDL ✅

- `schema/contract/source-contract.ts` — sourceContract + version + approval
- `schema/contract/observation-contract.ts` — observationContract + version + approval + fieldMap
- `schema/contract/canonical-contract.ts` — canonicalContract + version + approval
- `schema/contract/metric-contract.ts` — metricContract + version + approval
- `schema/contract/contract-lineage.ts` — contractLineage (type-aware)
- `schema/metric/metric-definition.ts` — metricDefinition + metricDefinitionKnowledge
- `schema/metric/metric-binding.ts` — metricBinding (in metric schema, FKs to metric_contract + canonical_contract)

## Execution Steps

### Step 1: Rewrite contract.repository.ts

Category-dispatched helper. Each method takes category as first arg.

- createContract(category, data) → insert into family table
- findContractById(category, id) → select from family table
- findContractByName(category, name) → select from family table
- listContracts(params) → single category: query that table; multi-category: UNION ALL raw SQL
- updateContract(category, id, data) → update family table
- deleteContract(category, id) → delete from family table
- archiveContract / unarchiveContract → family table
- findDeleteBlockers / findArchiveBlockers → update raw SQL refs
- createVersion(category, data) → family version table
- findVersion / listVersions / updateVersionState / findLatestVersion → family version table
- createApproval / listApprovals → family approval table
- createLineageEdge / listLineageEdges → contractLineage (v2)
- createBinding / listBindings → REMOVE (binding table dropped)
- findMetaSchema / listMetaSchemas → contractMetaSchema (unchanged)

### Step 2: Rewrite kpi-spec.repository.ts → metric-knowledge.repository.ts

- Import metricDefinition + metricDefinitionKnowledge from metric schema
- All JOINs go to metricDefinition (not unified contract)
- Column mapping: contractId → metricDefinitionId, short → displayName (from metricDefinition), tier → tierCode, specState → statusCode

### Step 3: Rewrite metric-binding.repository.ts

- Import metricBinding from schema/metric (v2, already exists)
- Raw SQL: `contract.contract mc` → `contract.metric_contract mc`
- Raw SQL: `contract.contract cc` → `contract.canonical_contract cc`
- Column refs: mc.contract_id → mc.metric_contract_id, mc.contract_name → mc.metric_contract_name, etc.

### Step 4: Rewrite integrity.service.ts

- `FROM contract.contract c WHERE c.category_code = 'canonical'` → `FROM contract.canonical_contract c`
- `FROM contract.contract c WHERE c.category_code = 'metric'` → `FROM contract.metric_contract c`
- `FROM contract.contract c WHERE c.category_code = 'admission'` → `FROM contract.source_contract c`
- `contract.contract_version` → family-specific version tables
- Column refs: contract_id → family-specific ID columns

### Step 5: Update contract.service.ts + controller

- Pass category through from controller to repository
- Remove binding-related endpoints if any
- Update DTO types if needed

### Step 6: Update seed files

- seed-kpi-specs.ts → update to use new metric-knowledge repository
- Any other seeds referencing v1 tables

### Step 7: Clean barrel exports

- schema/contract/index.ts: remove line 18-23 (v1 re-exports)
- schema/registry/index.ts: remove v1 re-exports, ensure metric exports present

### Step 8: Delete v1 files

- DELETE schema/contract/contract-objects.ts
- DELETE schema/contract/kpi-spec.ts
- DELETE schema/contract/metric-reference.ts
- DELETE schema/contract/metric-binding.ts (the one in contract/, not metric/)

### Step 9: Verify

- `npx tsc --noEmit` — zero errors
- `npx vitest run` — all tests pass
- Restart bc-core, seed DB, verify API endpoints
- bc-admin pages load
