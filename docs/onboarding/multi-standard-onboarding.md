---
id: multi-standard-onboarding
order: 63
title: "Multi-Standard Onboarding"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, business-vocabulary, business-field-and-business-object-onboarding, canonical-field-seeding, ai-gates, ai-trust-and-verification, data-model-and-schema]
governing_sources:
  - The Contract Grammar
  - Business Vocabulary
  - Business Field and Business Object Onboarding
governing_adrs:
  - DEC-9361cd (D302 cc_field_mapping; canonical uniqueness invariant)
  - DEC-9a5dc0 (D068 CF boundary; reporting standards promote to canonical fields)
  - DEC-f66378 (D292 BO-scoped BF naming applies across all tiers)
governing_sops:
  - legacy-v2/docs/sops/multi-standard-onboarding-sop.md
errata_referenced: []
v2_sources:
  - sops/multi-standard-onboarding-sop.md
diagrams: []
---

# Multi-Standard Onboarding

## Scope

This chapter generalizes Business Field and Business Object Onboarding to support multiple authoritative standards. It names the three-tier sourcing hierarchy (OAGIS at tier 1; ISO 20022, XBRL, IFRS, UN/CEFACT at tier 2; BareCount Standard as the last-resort tier 3), the exhaustion rule (tier N must be exhausted before tier N+1 is used), the universal naming rules that apply across all tiers, the overlap-detection procedure that protects against canonical fragmentation (BF overlap, BO overlap, CF synonym), the format-specific parsers per standard family, the additional five gates that BareCount Standard tier-3 BFs and BOs pass, and the verification checklist run after each standard onboarding. It records the boundary between Multi-Standard Onboarding and the OAGIS-specific tier-1 procedure governed by Business Field and Business Object Onboarding. It records the as-built drift between the procedure and the platform's current standards-loaded state.

This chapter does not redefine the BF and BO derivation rules or the certification and approval gates (Business Field and Business Object Onboarding), the Canonical Field registry (Canonical Field Seeding), or the AI maker-checker-gate envelope (AI Gates).

**Governing source.** outline.md §4.6; Business Vocabulary.

## The Three-Tier Sourcing Hierarchy

The platform sources BFs and BOs from authoritative published standards in strict tier order. Every BF and BO carries a `source_standard` tag tracing its origin.

| Tier | Source | `source_standard` value | Onboarding path | Gate level |
|---|---|---|---|---|
| 1 | OAGIS | `oagis` | OAGIS-specific procedure governed by Business Field and Business Object Onboarding | Full CR-QG-001 plus CR-QG-002 plus auto-certify for standards-sourced |
| 2 | Other published standards: ISO 20022, XBRL or US GAAP, IFRS, UN/CEFACT | `iso_20022`, `xbrl_gaap`, `ifrs`, `uncefact` | This chapter | Full CR-QG-001 plus CR-QG-002 plus standard-source auto-certify |
| 3 | BareCount Standard (last resort) | `bc_standard` | This chapter plus five additional gates | Full CR-QG plus exhaustion plus naming plus semantic plus AI verification plus synonym |

The exhaustion rule: tier N is exhausted before tier N+1 is used. Before creating a BareCount Standard BF, the actor proves the concept does not exist in OAGIS, ISO 20022, XBRL, or any other loaded standard. The exhaustion check is part of the additional gate set for tier 3.

**Governing source.** Business Vocabulary.

## Universal Naming Rules

All tiers follow the same naming rules. No standard gets special treatment.

The BF naming rules per ISO 11179:

| Rule | Form |
|---|---|
| Format | `{bo_prefix}_{field_name}` |
| Case | snake_case only; never camelCase or Title Case |
| Maximum length | 64 characters; abbreviate the BO prefix if needed |
| Shared exceptions | The five shared dimensions (`company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure`) carry no BO prefix |
| Regex | `/^[a-z][a-z0-9_]*$/`; enforced by CR-QG-001 |

The BO naming rules:

| Rule | Form |
|---|---|
| Format | snake_case |
| Display name | Title Case |
| `source_standard` | The tier tag from the table above |
| `standard_ref` | Standard-specific reference (`pain.001` for ISO 20022; `us-gaap:Assets` for XBRL; null for BareCount Standard) |

**Governing source.** Business Vocabulary.

## Overlap Detection

Before creating any BF or BO from a new standard, the actor runs three overlap checks. Skipping the checks fragments the canonical vocabulary; two BOs with overlapping field sets but different names produce the chain-mapping collision DEC-9361cd is meant to prevent.

### BF Overlap Check

For each candidate BF from the new standard:

| Step | Outcome |
|---|---|
| Search existing BFs by name | Exact match: REUSE the existing BF; do not create |
| Search existing BFs by definition similarity | High similarity match: REVIEW |
| No match | Proceed to create |

API: `GET /api/business-fields?q={field_name}` returns the candidates for review.

### BO Overlap Check

For each candidate BO from the new standard:

| Field overlap | Outcome |
|---|---|
| High overlap with an existing BO in the same function and subfunction | DO NOT CREATE; map to the existing BO |
| Moderate overlap | REVIEW; the BO may be complementary or duplicate |
| Low overlap | Proceed to create |

API: `GET /api/business-objects?functionCode={fn}&subfunctionCode={sub}` returns the candidates for composition comparison.

### CF Synonym Check (DEC-9361cd Canonical Uniqueness Invariant)

When a new BF will map to a CF:

| Step | Outcome |
|---|---|
| Check if the CF exists | REUSE; do not create new CF |
| Check if a synonym CF exists (different name, same concept) | REUSE the existing CF |
| Only create new CF if no existing CF or synonym covers the concept | Proceed to register the new CF (Canonical Field Seeding) |

Synonym detection is AI-assisted (cross-model semantic comparison via the maker-checker-gate envelope). When AI is unavailable, manual review is required; the chapter does not admit synonym creation that bypassed the check.

**Governing source.** Business Vocabulary; Canonical Field Seeding; AI Gates.

## Per-Standard Onboarding Steps

The procedure is the same regardless of standard; the parser at Step 1 varies.

### Step 1: Parse the Standard Source

The actor converts the standard's native format into a normalized intermediate that the BF and BO creation services consume. The intermediate format:

```
{
  "standard": "xbrl_gaap",
  "standardRef": "us-gaap-2025",
  "businessObjects": [
    {
      "name": "gaap_receivables",
      "displayName": "GAAP Receivables",
      "definition": "Accounts receivable concepts from US GAAP XBRL taxonomy",
      "functionCode": "finance",
      "subfunctionCode": "accounts_receivable",
      "tierCode": "basic",
      "fields": [
        {
          "name": "gaap_receivables_allowance_for_doubtful_accounts",
          "definition": "Amount of allowance for credit loss on accounts receivable",
          "dataType": "currency",
          "semanticRole": "measure",
          "standardElement": "us-gaap:AllowanceForDoubtfulAccountsReceivable"
        }
      ]
    }
  ]
}
```

Format-specific parsers:

| Standard | Native format | Parser approach |
|---|---|---|
| XBRL | Taxonomy XSD plus labels | Parse the XSD; extract concepts with labels, types, period types |
| ISO 20022 | Message XSD | Parse the XSD; extract complex types; flatten to scalar fields |
| UN/CEFACT CCL | CCL spreadsheet | Parse the spreadsheet; extract ACCs and BCCs |

### Step 2: Run the Three Overlap Checks (Step 4a-c above)

Every candidate BF and BO is classified as REUSE, CREATE, or REVIEW. The classification is recorded in the session log.

### Step 3: Create Business Fields (Bulk)

```
POST /api/business-fields/bulk
{
  "fields": [
    {
      "name": "gaap_receivables_allowance_for_doubtful_accounts",
      "definition": "Amount of allowance for credit loss on accounts receivable",
      "function": "finance",
      "objectClass": "gaap_receivables",
      "property": "allowance_for_doubtful_accounts",
      "representationTerm": "Amount",
      "dataType": "currency",
      "sourceStandard": "xbrl_gaap",
      "standardRef": "us-gaap:AllowanceForDoubtfulAccountsReceivable",
      "piiClassification": "none"
    }
  ]
}
```

The CR-QG-001 certification gate runs per BF: name regex, non-null definition, object class, property, representation term, data type, PII classification.

### Step 4: Certify (Auto for Standards-Sourced)

```
POST /api/business-fields/bulk-certify
{ "fieldIds": [...], "autoCertifyStandards": true }
```

Standards-sourced BFs auto-certify (the standard's published vocabulary is the certification authority); the same auto-certify discipline that applies to OAGIS BFs applies to ISO 20022, XBRL, IFRS, and UN/CEFACT BFs. An AI spot-check fires asynchronously per batch; the active sample rate belongs to implementation configuration or the governing SOP.

### Step 5: Create Business Objects with Composition

```
POST /api/business-objects
{
  "objectName": "gaap_receivables",
  "displayName": "GAAP Receivables",
  "definitionText": "Accounts receivable concepts from US GAAP XBRL taxonomy",
  "sourceStandard": "xbrl_gaap",
  "standardRef": "us-gaap-2025",
  "industryCode": "universal",
  "functionCode": "finance",
  "subfunctionCode": "accounts_receivable",
  "tierCode": "basic",
  "fields": [
    {
      "fieldName": "gaap_receivables_allowance_for_doubtful_accounts",
      "isRequired": false,
      "isBusinessKey": false,
      "semanticRole": "measure",
      "ordinalPosition": 1
    }
  ]
}
```

The CR-QG-002 approval gate runs: domain taxonomy populated, minimum composition (at least one identifier, dimension, temporal; at least one business key; at least four fields), tier validity (derived BOs require derivation edges), semantic dedup, AI verification (CR-BO-007), all BFs certified, no shared observation BFs except the five exceptions.

### Step 6: Approve

```
POST /api/business-objects/{id}/approve
```

The seven CR-QG-002 gates run. A BO that fails any gate stays in `draft`.

### Step 7: Verify Chain Integration

After onboarding, the actor checks whether the new BFs can be mapped to CFs. For each new BF, the actor inspects the CF gap query (Canonical Field Seeding Step 3) to determine whether any unmapped CF needs the new BF; if yes, the CC field-mapping gap is added to the next chain-agent run.

**Governing source.** Business Field and Business Object Onboarding; Canonical Field Seeding.

## Tier 3 (BareCount Standard): Five Additional Gates

BareCount Standard BFs and BOs go through the same seven steps PLUS five additional gates. The additional gates are blocking: a tier-3 BF or BO that fails any gate stays in `draft`.

| Gate | Check |
|---|---|
| Exhaustion | Prove the concept does not exist in any loaded standard (tier 1 plus tier 2) |
| Naming | ISO 11179 decomposition is valid; no forbidden vocabulary tokens |
| Semantic | The definition is specific (not vague); describes a real-world observable |
| AI Verification | A cross-family AI maker-checker-gate confirms the concept is valid and correctly classified |
| Synonym | No existing CF or BF covers the same concept under a different name |

BareCount Standard BOs additionally carry a `definitionText` explaining the real-world entity the BO represents and at least one domain expert justification recorded in the BO description or in an ADR.

The chapter records the additional gates because tier-3 sources do not carry external authority. A standards-sourced BF inherits the standard's authority for certification; a BareCount Standard BF must earn it through the additional gate set.

**Governing source.** Business Vocabulary; AI Gates; AI Trust and Verification.

## Verification Checklist

After onboarding any standard, the actor runs:

| Check | How |
|---|---|
| All BFs carry `source_standard` tag | `GET /api/business-fields?sourceStandard={tag}` returns the expected count |
| All BOs carry `source_standard` tag | `GET /api/business-objects?sourceStandard={tag}` returns the expected count |
| No BF name collisions | BF creation returned zero errors |
| No BO duplication | BO approval gate 6 (semantic dedup) passed |
| All BOs approved | Status equals `approved` for all new BOs |
| Chain integration verified | At least one CF-to-BF-to-CC mapping verified end-to-end |

A check that fails identifies a violation; the violation is fixed before the chapter declares the standard onboarding complete.

**Governing source.** Business Vocabulary.

## Standard-Specific Parsers (Inventory)

| Standard | Source format | Parser status | Seed collection |
|---|---|---|---|
| OAGIS | MongoDB (scraped from oagidocs.org) | Built; OAGIS Onboarding Service | `seed_oagis_components` |
| XBRL US GAAP | Taxonomy XSD plus labels | Queued | `seed_xbrl_gaap` |
| ISO 20022 | Message XSD | Queued | `seed_iso20022` |
| UN/CEFACT CCL | CCL spreadsheet | Queued | `seed_uncefact_ccl` |
| BareCount Standard | Manual definition | Via API directly | None (no seed) |

The parser inventory is the chapter's record of which standards have been wired to the platform. A queued parser is a known gap; the platform's procedure supports tier-2 standards conceptually, but the loader has not been built. The chapter records this honestly per pattern 81.

**Governing source.** Business Vocabulary.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Business Field and Business Object Onboarding | Governs the OAGIS-specific tier-1 procedure; this chapter generalizes it to tier 2 and tier 3 with the same gates plus the additional tier-3 set |
| Canonical Field Seeding | Cross-tier CFs are the synonym-check anchor; the canonical uniqueness invariant from DEC-9361cd applies across all tiers |
| Source and Admission Contract Creation | Independent; SC and AC operate on the source catalog regardless of which standard sourced the BFs and BOs |
| Observation Contract Creation | Consumes the BFs the standard onboarded; OC creation does not distinguish by standard |
| Canonical Contract Creation | Consumes the BOs the standard onboarded; CC creation does not distinguish by standard |

**Governing source.** Business Field and Business Object Onboarding; Canonical Field Seeding; Observation Contract Creation; Canonical Contract Creation.

## Drift Inventory

| Drift item | Form |
|---|---|
| Tier-2 parser coverage is partial | OAGIS is loaded; ISO 20022 is partially loaded (a small set of payment messages); XBRL US GAAP is loaded as reference for metric naming validation but no BFs are derived from it; IFRS and UN/CEFACT have not been loaded as BF and BO sources |
| Exhaustion check accuracy depends on tier-1 and tier-2 completeness | A BareCount Standard BF can pass the exhaustion gate when a tier-2 standard would have covered the concept but is not yet loaded; the gate is honest at the moment but may be over-permissive until the tier-2 loaders are complete |
| AI synonym detection accuracy varies | The cross-model semantic comparison is good for the common cases but may miss novel synonyms that no standard covers; manual review is the backup |
| BareCount Standard BF count is small | The exhaustion rule keeps the tier-3 count low by design; the chapter does not assert a target count for BareCount Standard BFs |
| Standard authority dynamics | Tier-1 (OAGIS) and tier-2 (ISO, IFRS) standards are revised by their stewards on cycles independent of BareCount; a standard revision may add or rename concepts that the platform does not pick up automatically. The chapter records the platform's policy as on-demand re-load when a standard revision lands |

**Governing source.** Business Vocabulary; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-9361cd | Establishes the canonical uniqueness invariant; the synonym check at tier 2 and tier 3 is the operational form of this invariant |
| DEC-9a5dc0 | Establishes the CF boundary for reporting standards (US GAAP, IFRS, COSO, IIA); reporting-standard concepts promote to Canonical Fields rather than Business Fields |
| DEC-f66378 | Establishes BO-scoped BF naming and the five shared dimension exceptions; the rule applies across all tiers, not only tier 1 |

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Business Vocabulary
- Business Field and Business Object Onboarding
- Canonical Field Seeding
- Canonical Contract Creation
- AI Gates
- AI Trust and Verification
- Data Model and Schema
- DEC-9361cd: cc_field_mapping (canonical uniqueness invariant)
- DEC-9a5dc0: CF boundary; reporting standards promote to canonical fields
- DEC-f66378: BO-scoped BF naming
- legacy-v2/docs/sops/multi-standard-onboarding-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


