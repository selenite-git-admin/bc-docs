# Metric Work Records

Operational memory for metric workstream activity. A record captures the **logic studied**, the **assumptions made**, the **interpretations rejected**, the **drift / damage risks** identified, and the **guardrails** future operators must respect — alongside the standard summary, findings, evidence pointers, and follow-ups. Records are metric-indexed orientation documents linking back to canonical artifacts (DevHub session change records, ADRs, commits, `evidence.evidence_object` rows, contract versions).

**Records are orientation memory, not contract authority.** A record does **not** redefine a Metric Contract, restate Foundation, or substitute for an ADR. If a record conflicts with the Metric Contract, an ADR, Foundation chapters, `evidence.evidence_object`, or an authoritative onboarding SOP, those sources win. The record is corrected to match canonical state, not the other way.

Authority and scope are defined in `bc-docs-v3/docs/onboarding/metric-workstream.md` §11. Read that section first; this README only operationalizes it.

## Directory layout

```
metric-work-records/
├── README.md                          (this file)
├── _template.md                       (copy when authoring a new record)
├── <metric_slug>/                     (one directory per MC, slug = name minus mc__ prefix)
│   ├── YYYY-MM-DD-<work_type>-<session_uid>.md
│   └── ...
└── _cross/                            (work that does not pivot on a single metric)
    └── YYYY-MM-DD-<work_type>-<session_uid>.md
```

### Filename convention

```
<metric_slug>/YYYY-MM-DD-<work_type>-<session_uid>.md
```

- `<metric_slug>` — stable machine name of the MC minus the `mc__` prefix. Lowercase, underscore-separated. Examples: `days_sales_outstanding`, `ap_turnover_ratio`, `accounts_receivable_turnover_ratio`.
- `YYYY-MM-DD` — calendar date the record was authored. ISO 8601 dates only; no slashes, no underscores.
- `<work_type>` — one of the seven work types named in `metric-workstream.md` §1:
  - `new-mc`
  - `version-bump`
  - `tenant-onboarding`
  - `rejection-investigation`
  - `grammar-extension`
  - `projection-bug`
  - `cleanup`
- `<session_uid>` — the DevHub session UID that produced the record (e.g., `SES-b7db1a`).

Use `_cross/` (no metric slug subdirectory) when the work explicitly covers many metrics or does not anchor on one — for example, an engine-wide diagnostic. Records in `_cross/` are exceptional; the dominant access pattern is per-metric.

### When a record is mandatory vs optional

See `metric-workstream.md` §11 — "When a record is MANDATORY" and "When a record is OPTIONAL". Triggers 1–7 in the playbook map 1:1 to the seven mandatory cases listed below. The short version:

**Mandatory:**
1. New MC authored
2. MC version bump changing formula / variables / grain / temporal / thresholds
3. Tenant or system onboarding for an existing MC
4. Rejection investigation that concludes with a decision (including "no change — correct behavior")
5. Grammar or evaluator extension
6. Stale-data cleanup decision, including any DBCP authored
7. Foundation Gate redirect — where the original suspected layer was wrong, especially "not SDG / not fact / not read model"

**Optional:** read-only audits without decisions, plan-only sessions, tool/diagnostic improvements not tied to a specific metric.

### When the logic-study sections are mandatory

The template's standard sections (Summary, Foundation Gate Result, Findings, Decision / Recommendation, Evidence, Non-decisions, Follow-ups) are required on every record.

The **logic-study sections** — Metric Logic Studied, Assumptions, Rejected Interpretations, Drift / Damage Risks, Guardrails For Future Work — are additionally required when the record covers any of:

- A new MC being authored.
- An MC version bump that changes formula, variables, grain, temporal semantics, unit semantics, threshold semantics, or co_bindings.
- A rejected-evaluation diagnosis (whether or not it concludes with a change).
- Grammar or evaluator design / extension work.
- A semantic dispute — i.e., disagreement about what a metric, CF, BF, or mapping means.
- A live-MC fix (anything that touches a live MC version's behavior, even indirectly via an upstream artifact).

For other work types — purely procedural tenant onboarding, projection bugs that did not change semantic behavior, stale-data cleanup — the logic-study sections are encouraged but not required. If a section is genuinely not applicable, write `n/a` and a one-line reason rather than silently omitting.

### Authoring flow

1. Copy `_template.md` into the right `<metric_slug>/` subdirectory with the conventional filename.
2. Fill the frontmatter — all required keys, `n/a` where genuinely not applicable.
3. Fill the required sections — Summary, Foundation Gate Result, Findings, Decision / Recommendation, Evidence, Non-decisions, Follow-ups. Each may be short; orientation, not exhaustive prose.
4. Set `status:` appropriately:
   - `draft` while still being written
   - `decision-pending` if waiting on user/operator approval
   - `decided` once the decision is in place
   - `superseded` once a newer record or ADR replaces it (link the successor in Findings or Follow-ups)
   - `abandoned` if the work was dropped (note why)
5. Cross-link from the related DevHub session's change record, the relevant ADR, and any follow-up tasks. Use `devhub_change_record_save` with the record's path in `report_json.metric_work_record` or equivalent.
6. Commit alongside the related artifact (commit, ADR, etc.). A standalone record commit is acceptable but the canonical artifact should land in the same operator turn whenever possible.

### Record vs canonical sources — quick map

| Question | Authoritative source | Record's role |
|---|---|---|
| What changed in the code? | git commit | Cite SHA + one-line summary |
| What did the eval engine decide? | `evidence.evidence_object` | Cite row ID(s); never paste row contents |
| What architectural decision was made? | ADR in `bc-docs-v3/docs/adrs/` | Cite `DEC-uid` and link |
| What operational session ran the work? | DevHub session + `CHG-uid` change record | Cite `SES-uid` and `CHG-uid` |
| What is the metric contract currently? | `contract.metric_contract_version` | Cite metricContractId + version_code |
| What follow-up work was filed? | DevHub `TSK-uid` | Cite all TSK-uids |

The record carries no canonical content. It carries pointers and a one-paragraph orientation per section so that a future reader does not need to chase every canonical source to know what happened.

### Indexing

Records are picked up by `devhub_doc_scan` like any other doc under `bc-docs-v3/docs/`. They become addressable via `devhub_doc_get` and listable via `devhub_doc_list`. To find every record for a metric, list the directory under that metric's slug. To find every record of a type across metrics, filter by frontmatter `work_type`.

### Do not

- Do not duplicate canonical content into the record (full code diffs, full evidence-row JSON, full ADR bodies). Link instead.
- Do not edit a record after `status: decided` to retcon the history. If a finding turns out to be wrong, file a new record with `status: superseded` on the old one and link forward.
- Do not author a record that announces an architectural decision without also authoring the ADR. Records are orientation; ADRs are authority.
- Do not use a record to bypass the Foundation Gate. The gate is required *before* code; the record summarizes the gate result and what followed.
