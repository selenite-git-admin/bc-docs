---
uid: DEC-d214ed
title: "BO-CO Enrichment Engine — Claude Code Generation + Gemini Verification + Audit Trail"
description: "Three-stage AI enrichment: Claude generates BO field compositions, Gemini verifies against accounting standards, audit trail preserved per enrichment."
status: superseded
subdomain: enrichment-engine
focus: bo-co-enrichment-legacy
superseded_by: DEC-e9294b
date: 2026-03-24
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D200"
  - type: decision
    label: "D108"
authority: authoritative
migrated_from: legacy v2 archive
---


# BO-CO Enrichment Engine — Claude Code Generation + Gemini Verification + Audit Trail

## Context

UPDATED: BO/CO verification must be source-agnostic. Verification references: accounting standards (IFRS, US GAAP), ISO 20022, ISO 11179, UN/CEFACT, industry models (APQC) — NOT vendor documentation. Vendor docs (SAP, Oracle) are only relevant for the source layer (D200 Step 4: AI field mapping). The business_field.source_aliases column stores vendor names as mapping convenience metadata, not as BO identity. This aligns with Foundation spec: Canonical Contract is Pattern C (source-agnostic, no source reference).

## The Problem

60 Business Objects exist but are thin (avg 7.5 fields, GL Journal Entry has only 5). 23 Canonical Contracts are empty shells (0 versions, no contract_json). D200 (Reader Creation Wizard) cannot run until BOs have realistic field compositions and canonical contracts have content.

## The Design: Three-Stage Enrichment Pipeline

```
Stage 1: GENERATE (Claude Code)         — batch-enrich BOs with full field compositions
    ↓
Stage 2: VERIFY (Gemini + Claude API)   — ground-truth check against real-world standards
    ↓
Stage 3: ACTIVATE (Auto-generate)       — create canonical contract versions + approve BOs
```

All three stages produce audit log entries. UI surfaces everything.

---

### Stage 1: GENERATE — Claude Code Batch Enrichment

Claude Code (this tool, running in session) generates enriched field compositions for each BO by:

1. Reading the current BO definition (name, function, subfunction, tier)
2. Reading existing composed fields
3. Generating a complete field composition based on domain knowledge:
   - Real-world ERP fields for this business object
   - Correct data types, semantic roles, business keys
   - ISO 11179 naming conventions
   - 15-25 fields per BO (not 5)

**Output per BO:**
- New business fields to create (if not already in the 452-field registry)
- Updated field composition (ordinals, roles, required, keys)
- BO definition text (if missing)
- Business key declaration

**Execution:** Batch script called via bc-core API endpoints:
```
POST /api/business-fields          — create missing fields
PUT  /api/business-objects/:id/fields  — bulk replace field composition
PATCH /api/business-objects/:id    — update definition, metadata
```

**Audit:** Each enrichment action logged to `operations.bo_enrichment_log`:
```
enrichment_id, object_id, action (field_added|field_removed|composition_replaced|metadata_updated),
before_json, after_json, source (claude_code|manual|gemini_verified),
session_id, created_at
```

---

### Stage 2: VERIFY — Gemini Search + Claude API Verification

Reuses the proven D108 `CatalogVerificationAgent` pattern (Gemini 2.5 Flash grounded search → HTTP fetch → Claude verify). New verification tier: `business_object`.

**Flow per BO:**

**Step 1: SEARCH (Gemini 2.5 Flash + Google Search grounding)**
```
Prompt: "What are the standard fields and attributes for a {display_name} 
in enterprise {function} systems? Include field names, data types, 
and which fields are business keys. Reference ISO standards, 
ERP vendor documentation (SAP, Oracle, NetSuite), and accounting standards."
```
Returns: grounded URLs + summary from real vendor documentation.

**Step 2: FETCH (HTTP)**
Fetches top 3 URLs, extracts text content (max 5000 chars each).

**Step 3: VERIFY (Claude API — claude-sonnet-4-6)**
```
Prompt: "You are verifying a Business Object field composition.

Business Object: {display_name} ({function}/{subfunction})
Current Fields:
{field_list with types, roles, required, keys}

Reference Documentation:
{fetched page content}

Evaluate:
1. COMPLETENESS — are critical fields missing?
2. ACCURACY — are field names, types, roles correct?
3. BUSINESS KEYS — is the key declaration correct?
4. COVERAGE — what percentage of standard fields are present?

Return JSON:
{
  verdict: 'verified' | 'needs_enrichment' | 'uncertain',
  confidence: 0-100,
  completeness_score: 0-100,
  missing_fields: [{ name, data_type, reason }],
  incorrect_fields: [{ name, issue, suggestion }],
  business_key_assessment: 'correct' | 'incomplete' | 'incorrect',
  evidence_text: '...',
  sources: [{ title, url }]
}
```

**Storage:** Results go to `operations.bo_verification_log` (same pattern as `catalog_verification_log`):
```
verification_id, object_id, tier_code ('business_object'),
result_code (verified|needs_enrichment|uncertain|error),
confidence_score, completeness_score,
corrections_json, evidence_text, notes_text,
model_id, input_tokens, output_tokens,
agent_trace_json, created_at, resolved_at, resolved_by
```

**Bundled execution:** After Stage 1 enriches a BO, Stage 2 verification runs automatically (no user action needed). The "bundle" is: enrich → verify → log.

---

### Stage 3: ACTIVATE — Auto-Generate Canonical Contract Versions + Approve BOs

After verification passes (verdict = 'verified', confidence ≥ 80):

**3a. Generate Canonical Contract Version:**
For each of the 23 canonical contracts that reference a verified BO:
```
POST /api/contracts/canonical/:id/versions
body: {
  version_code: "1.0.0",
  contract_json: {
    "$contract": "barecount/canonical/v1",
    "resolved_schema": {
      // Auto-populated from BO field composition
      "fields": [
        { "name": "company_code", "data_type": "string", "required": true, "business_key": true, "semantic_role": "identifier" },
        ...
      ]
    },
    "business_key_fields": ["company_code", "fiscal_year", "document_number"],
    "semantic_rules": [
      { "field": "currency_code", "rule": "iso_4217" },
      { "field": "posting_date", "rule": "valid_date" },
      { "field": "amount_local", "rule": "numeric_non_null" }
    ]
  },
  governance_state_code: "active"
}
```

**3b. Approve BOs:**
```
PATCH /api/business-objects/:id
body: { statusCode: "approved" }
```

Only BOs with verification verdict = 'verified' get auto-approved.

---

### UI Design (bc-admin)

#### Business Object Detail Page — Enhanced

Current: read-only field composition table.
New additions:

**1. Enrichment Status Banner (top of page)**
```
┌─────────────────────────────────────────────────────────┐
│  ● Enriched (18 fields)  ● Verified (confidence: 92%)   │
│  Last enriched: 2026-03-24 by Claude Code               │
│  Last verified: 2026-03-24 by Gemini+Claude             │
│  [Re-Verify]  [View Audit Log]                          │
└─────────────────────────────────────────────────────────┘
```

Status badges:
- `Not Enriched` (grey) — original thin composition
- `Enriched` (blue) — Claude Code added fields
- `Verified` (green) — Gemini+Claude confirmed
- `Needs Enrichment` (amber) — verification found gaps
- `Uncertain` (yellow) — verification inconclusive

**2. Re-Verify Button**
Triggers: `POST /api/business-objects/:id/verify`
- Calls the Gemini+Claude verification agent on-demand
- Shows loading spinner with step progress (Searching... Fetching... Verifying...)
- Updates verification status + badge on completion
- Result appears in verification panel

**3. Verification Panel (collapsible section)**
```
┌─ Verification Result ──────────────────────────────────┐
│  Verdict: Verified ✓        Confidence: 92%             │
│  Completeness: 88%          Business Keys: Correct ✓    │
│                                                         │
│  Missing Fields (2):                                    │
│  • clearing_date (date) — standard AP aging field       │
│  • payment_reference (string) — cross-reference to AR   │
│                                                         │
│  Sources:                                               │
│  • SAP S/4HANA FI Documentation (help.sap.com)         │
│  • Oracle EBS AP Tables Reference (docs.oracle.com)    │
│                                                         │
│  [Accept] [Dismiss] [Apply Suggestions]                 │
└─────────────────────────────────────────────────────────┘
```

"Apply Suggestions" button: auto-creates missing fields and adds them to the BO composition.

**4. Audit Log Tab (new tab on detail page)**
```
Tab: Overview | Fields | Relations | Used By | Audit Log

┌─ Audit Log ────────────────────────────────────────────┐
│  2026-03-24 10:15  ENRICHED  Claude Code                │
│    Added 13 fields, updated 5 field roles               │
│    [View Diff]                                          │
│                                                         │
│  2026-03-24 10:16  VERIFIED  Gemini+Claude              │
│    Verdict: verified (92%), 2 suggestions               │
│    Sources: help.sap.com, docs.oracle.com               │
│    [View Full Trace]                                    │
│                                                         │
│  2026-03-24 10:20  APPROVED  System (auto)              │
│    Status: draft → approved                             │
│    Reason: verification passed (confidence ≥ 80%)       │
└─────────────────────────────────────────────────────────┘
```

**5. Field Composition Editor (inline on Fields tab)**
- Add Field button → search existing business fields or create new
- Remove Field button (on each row)
- Inline edit: required toggle, business key toggle, semantic role dropdown
- Reorder via ordinal position
- Bulk actions: "Enrich with AI" button triggers Stage 1+2

#### Business Objects List Page — Enhanced

New columns:
- `Enrichment` — badge (Not Enriched / Enriched / Verified / Needs Enrichment)
- `Fields` — count with completeness bar (e.g., 18/20 = 90%)
- `Verification` — confidence score badge

New filter:
- Enrichment status filter chips

Bulk action:
- "Enrich All Draft BOs" — triggers batch enrichment for all unverified BOs

---

### API Endpoints (New)

```
POST /api/business-objects/:id/enrich          — trigger Stage 1 enrichment (Claude Code)
POST /api/business-objects/:id/verify          — trigger Stage 2 verification (Gemini+Claude)
POST /api/business-objects/enrich/batch        — batch enrich multiple BOs
POST /api/business-objects/verify/batch        — batch verify multiple BOs
GET  /api/business-objects/:id/verification    — latest verification result
GET  /api/business-objects/:id/audit-log       — enrichment + verification audit trail
POST /api/business-objects/:id/activate        — Stage 3: generate canonical version + approve

POST /api/canonical-contracts/:id/generate-version  — auto-generate version from BO
```

### Audit Tables (New)

**`operations.bo_enrichment_log`**
```sql
CREATE TABLE operations.bo_enrichment_log (
  enrichment_id    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  object_id        uuid NOT NULL REFERENCES contract.business_object(object_id),
  action_code      text NOT NULL,  -- field_added, field_removed, composition_replaced, metadata_updated, status_changed
  before_json      jsonb,
  after_json       jsonb,
  source_code      text NOT NULL,  -- claude_code, manual, gemini_verified, auto_activate
  session_ref      text,           -- DevHub session ID or API request ID
  note_text        text,
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_bo_enrichment_log__object ON operations.bo_enrichment_log(object_id);
CREATE INDEX idx_bo_enrichment_log__created ON operations.bo_enrichment_log(created_at DESC);
```

**`operations.bo_verification_log`** (mirrors `catalog_verification_log` shape)
```sql
CREATE TABLE operations.bo_verification_log (
  verification_id   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  object_id         uuid NOT NULL REFERENCES contract.business_object(object_id),
  result_code       text NOT NULL,  -- verified, needs_enrichment, uncertain, error
  confidence_score  integer,        -- 0-100
  completeness_score integer,       -- 0-100
  business_key_assessment text,     -- correct, incomplete, incorrect
  corrections_json  jsonb,          -- { missing_fields: [...], incorrect_fields: [...] }
  evidence_text     text,
  notes_text        text,
  sources_json      jsonb,          -- [{ title, url }]
  model_id          text,
  input_tokens      integer,
  output_tokens     integer,
  agent_trace_json  jsonb,
  resolved_at       timestamptz,
  resolved_by       text,
  resolution_code   text,           -- accepted, dismissed, applied
  created_at        timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX idx_bo_verification_log__object ON operations.bo_verification_log(object_id);
CREATE INDEX idx_bo_verification_log__result ON operations.bo_verification_log(result_code);
CREATE INDEX idx_bo_verification_log__created ON operations.bo_verification_log(created_at DESC);
```

---

### Execution Order

```
Phase 1: DB tables (bo_enrichment_log + bo_verification_log)
Phase 2: BO Verification Agent (reuse D108 pattern, new tier: business_object)
Phase 3: Enrichment + Verification API endpoints
Phase 4: Canonical contract version auto-generation
Phase 5: bc-admin UI (enrichment banner, verification panel, re-verify button, audit log tab, field editor)
Phase 6: Batch enrichment run (enrich all 60 BOs, verify, activate)
```

## Consequences

N/A
