#!/usr/bin/env node
/**
 * generate_enforcement_surface_map.mjs — derive the ENFORCEMENT SURFACE MAP from the live
 * substrate and both codebases. GENERATED OUTPUT ONLY; never hand-edit the map.
 *
 * Purpose (operator decision 2026-07-26): every loop of the audit program traced to planning
 * against mental models of what the system enforces, instead of reading the enforcers. This map
 * makes the enforcement surface one grep-able document: no design, no ADR applied-instance, and
 * no population count may be claimed without citing it.
 *
 * Sources (all read-only):
 *   - bc_platform_dev  : functions, constraints, triggers for schemas metric_audit, mcf,
 *                        metric_directory (via docker exec bc-postgres psql)
 *   - bc_audit_dev     : same for schema audit_execution (the checker-side substrate)
 *   - bc-core worktree : wire validator rule codes (src/registry/metric-audit/wire/wire-validate.ts)
 *   - auditor repo     : CRV catalogue (references/contextual-reference-rule-catalog-v1.json)
 *
 * Output: docs/reference/enforcement-surface-map.md
 * Run:    node scripts/docs-control/generate_enforcement_surface_map.mjs
 */
import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = resolve(ROOT, 'docs', 'reference', 'enforcement-surface-map.md');
const BC_CORE = 'C:/MyProjects/_wt/rintake';
const AUDITOR = 'C:/MyProjects/bc-external-audit-ramp5';

function psql(db, query) {
  return execFileSync('docker', ['exec', 'bc-postgres', 'psql', '-U', 'barecount', '-d', db, '-t', '-A', '-F', '\u0001', '-c', query], { encoding: 'utf8' })
    .split(/\r?\n/).filter((l) => l.length > 0).map((l) => l.split('\u0001'));
}
function gitSha(repo) {
  try { return execFileSync('git', ['-C', repo, 'rev-parse', '--short', 'HEAD'], { encoding: 'utf8' }).trim(); }
  catch { return '(unavailable)'; }
}

const lines = [];
const push = (...xs) => lines.push(...xs);

push('# Enforcement Surface Map', '');
push('**GENERATED — do not edit.** Regenerate: `node scripts/docs-control/generate_enforcement_surface_map.mjs`', '');
push(`Generated: ${new Date().toISOString()}`);
push(`Sources: bc_platform_dev + bc_audit_dev (live), bc-core@${gitSha(BC_CORE)}, auditor@${gitSha(AUDITOR)}`, '');
push('**Usage rule (operator, 2026-07-26):** no design, no ADR applied-instance, and no population count',
  'is claimed without citing this map. Counts are computed from the gate predicates below, never from',
  'proxy tables. When the map disagrees with a memory or a memo, the map wins; when the live substrate',
  'disagrees with the map, REGENERATE, then the substrate wins.', '');

// ── Section 1: gate + guard function sources (verbatim — the ground truth) ─────────────────────
function functionSection(db, schema, title, nameFilter) {
  push(`## ${title}`, '');
  const fns = psql(db, `SELECT p.proname FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='${schema}' ${nameFilter} ORDER BY p.proname`);
  for (const [name] of fns) {
    const def = psql(db, `SELECT pg_get_functiondef(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='${schema}' AND p.proname='${name}'`)
      .map((r) => r.join('\u0001')).join('\n');
    // derived index: refusal codes raised/appended in this function
    const codes = [...new Set([...def.matchAll(/'((?:c\d+|[A-Z][A-Z0-9_]{3,})[a-z0-9_]*)'/g)].map((m) => m[1])
      .filter((c) => /^c\d+_/.test(c) || /^[A-Z0-9_]+$/.test(c) && def.includes(`RAISE EXCEPTION`)))]
      .filter((c) => /^c\d+_/.test(c));
    const tables = [...new Set([...def.matchAll(/(?:FROM|JOIN|UPDATE|INSERT INTO)\s+([a-z_]+\.[a-z_]+)/gi)].map((m) => m[1].toLowerCase()))].sort();
    push(`### \`${schema}.${name}\``, '');
    if (codes.length) push(`Refusal codes: ${codes.map((c) => `\`${c}\``).join(', ')}`, '');
    if (tables.length) push(`Reads/writes: ${tables.map((t) => `\`${t}\``).join(', ')}`, '');
    push('```sql', def, '```', '');
  }
}
functionSection('bc_platform_dev', 'metric_audit', '1. Platform gate + guard functions (`metric_audit.*`) — VERBATIM', '');
functionSection('bc_platform_dev', 'mcf', '2. MCF lifecycle guard functions (`mcf.fn_*`) — VERBATIM', "AND p.proname LIKE 'fn\\_%'");

// ── Section 3: substrate constraints ───────────────────────────────────────────────────────────
function constraintSection(db, schemas, title) {
  push(`## ${title}`, '');
  const inList = schemas.map((s) => `'${s}'`).join(',');
  const tables = psql(db, `SELECT n.nspname, c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE c.relkind='r' AND n.nspname IN (${inList}) ORDER BY 1,2`);
  for (const [schema, table] of tables) {
    push(`### \`${schema}.${table}\``, '');
    const cols = psql(db, `SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_schema='${schema}' AND table_name='${table}' ORDER BY ordinal_position`);
    const notNull = cols.filter((c) => c[2] === 'NO').map((c) => c[0]);
    push(`Columns: ${cols.length} | **NOT NULL:** ${notNull.map((c) => `\`${c}\``).join(', ') || '(none)'}`, '');
    const cons = psql(db, `SELECT contype, conname, pg_get_constraintdef(oid) FROM pg_constraint WHERE conrelid='${schema}.${table}'::regclass ORDER BY contype, conname`);
    if (cons.length) {
      push('| Kind | Name | Definition |', '|---|---|---|');
      const kind = { p: 'PK', f: 'FK', u: 'UNIQUE', c: 'CHECK' };
      for (const [t, name, def] of cons) push(`| ${kind[t] ?? t} | \`${name}\` | \`${def.replace(/\|/g, '\\|')}\` |`);
      push('');
    }
    const trgs = psql(db, `SELECT t.tgname, pg_get_triggerdef(t.oid) FROM pg_trigger t WHERE t.tgrelid='${schema}.${table}'::regclass AND NOT t.tgisinternal ORDER BY t.tgname`);
    if (trgs.length) {
      push('Triggers:', '');
      for (const [name, def] of trgs) push(`- \`${name}\`: \`${def.replace(/CREATE TRIGGER /, '')}\``);
      push('');
    }
  }
}
constraintSection('bc_platform_dev', ['metric_audit'], '3. Platform substrate constraints — `metric_audit` (every column nullability, FK, CHECK, trigger)');
constraintSection('bc_platform_dev', ['mcf'], '4. Platform substrate constraints — `mcf`');
constraintSection('bc_platform_dev', ['metric_directory'], '5. Platform substrate constraints — `metric_directory`');

// ── Section 6: checker-side substrate (bc_audit_dev) ───────────────────────────────────────────
functionSection('bc_audit_dev', 'audit_execution', '6. Checker-side guard functions (`audit_execution.*`, bc_audit_dev) — VERBATIM', '');
constraintSection('bc_audit_dev', ['audit_execution'], '7. Checker-side substrate constraints — `audit_execution`');

// ── Section 8: wire validators (bc-core source) ────────────────────────────────────────────────
push('## 8. Wire validators (`bc-core src/registry/metric-audit/wire/wire-validate.ts`)', '');
push('Rule codes with their emitting lines (extracted; the file is the authority):', '');
const wire = readFileSync(resolve(BC_CORE, 'src/registry/metric-audit/wire/wire-validate.ts'), 'utf8').split(/\r?\n/);
const ruleLines = [];
wire.forEach((l, i) => { if (/(V-[DR]\d+|CF-R\d+)/.test(l) && /push\(|out\.push|`|'/.test(l)) ruleLines.push([i + 1, l.trim()]); });
push('| Line | Rule text |', '|---|---|');
for (const [n, l] of ruleLines) push(`| ${n} | \`${l.replace(/\|/g, '\\|').slice(0, 180)}\` |`);
push('');

// ── Section 9: CRV catalogue (auditor) ─────────────────────────────────────────────────────────
push('## 9. Checker rule catalogue (CRV) — `references/contextual-reference-rule-catalog-v1.json`', '');
const crv = JSON.parse(readFileSync(resolve(AUDITOR, 'references/contextual-reference-rule-catalog-v1.json'), 'utf8'));
const crvRules = Array.isArray(crv.rules) ? crv.rules : Object.values(crv.rules);
push(`Status: \`${crv.status}\` | Governing framework: \`${crv.governing_framework ?? '(unset)'}\` | Rules: ${crvRules.length}`, '');
push('| Code | Requirement |', '|---|---|');
for (const r of crvRules) push(`| ${r.code} | ${String(r.requirement).replace(/\|/g, '\\|')} |`);
push('');

// ── Section 10: canonical eligibility queries ──────────────────────────────────────────────────
push('## 10. Canonical population queries (COUNT FROM THE GATE, NOT FROM A TABLE)', '');
push('The ONLY sanctioned way to claim eligibility counts. These mirror the c9 arms verbatim:', '');
push('```sql',
  `-- c9 eligibility partition over active current MCVs (arms are mutually exclusive by evidence shape)`,
  `WITH act AS (`,
  `  SELECT v.metric_contract_version_uid AS mcv, s.exactness_result AS snap_exact,`,
  `         s.binary64_activation_eligible AS b64, s.package_signature_hash AS pkg, s.disposition_code AS disp`,
  `  FROM mcf.metric_contract_version v`,
  `  LEFT JOIN mcf.mcv_package_snapshot s USING (metric_contract_version_uid)`,
  `  WHERE v.is_current AND v.governance_state_code='active')`,
  `SELECT count(*) AS active_current,`,
  `  count(*) FILTER (WHERE snap_exact='EXACT' AND b64 IS TRUE) AS arm_exact_snapshot,`,
  `  count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv`,
  `    AND e.prover_algorithm_version='mcf-exactness-v2' AND e.verdict_code='EXACT' AND e.package_signature_hash=act.pkg)) AS arm_exact_reproof,`,
  `  count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv`,
  `    AND e.prover_algorithm_version='mcf-reproducibility-v1' AND e.verdict_code='REPRODUCIBLE' AND e.package_signature_hash=act.pkg)) AS arm_reproducible,`,
  `  count(*) FILTER (WHERE disp IS DISTINCT FROM 'computed') AS no_computed_snapshot`,
  `FROM act;`,
  '```', '');
// live snapshot of that query, dated — so the map carries the current truth too
const snap = psql('bc_platform_dev', `WITH act AS (SELECT v.metric_contract_version_uid AS mcv, s.exactness_result AS snap_exact, s.binary64_activation_eligible AS b64, s.package_signature_hash AS pkg, s.disposition_code AS disp FROM mcf.metric_contract_version v LEFT JOIN mcf.mcv_package_snapshot s USING (metric_contract_version_uid) WHERE v.is_current AND v.governance_state_code='active') SELECT count(*), count(*) FILTER (WHERE snap_exact='EXACT' AND b64 IS TRUE), count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv AND e.prover_algorithm_version='mcf-exactness-v2' AND e.verdict_code='EXACT' AND e.package_signature_hash=act.pkg)), count(*) FILTER (WHERE EXISTS (SELECT 1 FROM mcf.exactness_reproof_evidence e WHERE e.metric_contract_version_uid=act.mcv AND e.prover_algorithm_version='mcf-reproducibility-v1' AND e.verdict_code='REPRODUCIBLE' AND e.package_signature_hash=act.pkg)), count(*) FILTER (WHERE disp IS DISTINCT FROM 'computed') FROM act`)[0];
push(`Live at generation time: active=${snap[0]}, arm_exact_snapshot=${snap[1]}, arm_exact_reproof=${snap[2]}, arm_reproducible=${snap[3]}, no_computed_snapshot=${snap[4]}`, '');

writeFileSync(OUT, lines.join('\n') + '\n');
console.log(`wrote ${OUT} (${lines.length} lines)`);
