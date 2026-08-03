#!/usr/bin/env node
/**
 * generate_lifecycle_map.mjs — derive the LIFECYCLE MAP for the three admitted
 * authority-creating families (DEC-5a9dee / D549) from the LIVE substrate.
 * GENERATED OUTPUT ONLY; never hand-edit the map.
 *
 * Scope is bounded by the Codex Phase-2 disposition (study ledger E-6/E-10 + the
 * PR#1 merge note): MCF + Business Concept Registry + Metric Directory, DERIVATION
 * ONLY — no hand-authored matrices. Where the substrate holds no transition guard
 * for a family, the map SAYS SO (honest gaps are map content, not omissions).
 *
 * Division of labor with the enforcement-surface map (both are authority-ladder
 * level 3): the enforcement map carries VERBATIM gate/guard function bodies; this
 * map derives the per-family STATE MACHINES (states from CHECK constraints,
 * transitions parsed from the live state-machine function, enforcing objects
 * indexed by name) and cites the enforcement map for bodies — one exception: the
 * MCF state-machine function itself is included verbatim as the matrix ground truth.
 *
 * Sources (all read-only): bc_platform_dev via docker exec bc-postgres psql.
 * Output: docs/reference/lifecycle-map.md
 * Run:    node scripts/docs-control/generate_lifecycle_map.mjs
 */
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const OUT = resolve(ROOT, 'docs', 'reference', 'lifecycle-map.md');
const DB = 'bc_platform_dev';

function psql(query) {
  return execFileSync('docker', ['exec', 'bc-postgres', 'psql', '-U', 'barecount', '-d', DB, '-t', '-A', '-F', '', '-c', query], { encoding: 'utf8' })
    .split(/\r?\n/).filter((l) => l.length > 0).map((l) => l.split(''));
}
function fnDef(schema, name) {
  return psql(`SELECT pg_get_functiondef(p.oid) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='${schema}' AND p.proname='${name}'`)
    .map((r) => r.join('')).join('\n');
}
/** CHECK constraints on a column — the substrate's state vocabulary. */
function checksFor(schema, table, columnLike) {
  return psql(`SELECT con.conname, pg_get_constraintdef(con.oid) FROM pg_constraint con
    JOIN pg_class c ON c.oid=con.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='${schema}' AND c.relname='${table}' AND con.contype='c'
      AND pg_get_constraintdef(con.oid) ILIKE '%${columnLike}%' ORDER BY 1`);
}
function triggersFor(schema, table) {
  return psql(`SELECT t.tgname, p.proname FROM pg_trigger t
    JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace
    JOIN pg_proc p ON p.oid=t.tgfoid
    WHERE n.nspname='${schema}' AND c.relname='${table}' AND NOT t.tgisinternal ORDER BY 1`);
}
function statesFromCheck(defn) {
  const m = defn.match(/ARRAY\[(.*?)\]/s);
  if (!m) return [];
  return [...m[1].matchAll(/'([a-z_]+)'/g)].map((x) => x[1]);
}

const lines = [];
const push = (...xs) => lines.push(...xs);

push('# Lifecycle Map — the admitted authority-creating families', '');
push('**GENERATED — do not edit.** Regenerate: `node scripts/docs-control/generate_lifecycle_map.mjs`', '');
push(`Generated: ${new Date().toISOString()}`);
push(`Source: ${DB} (live substrate, read-only)`, '');
push('**Authority position (DEC-5a9dee / the Authority Model ladder):** this map is a level-3',
  'GENERATED rendering. Foundation names the families and their states (The Contract Grammar);',
  'this map derives the transition machinery from the substrate. Map/ADR disagreement is a',
  'finding; map/substrate disagreement means the map is stale — regenerate. Verbatim gate and',
  'guard function bodies live in the sibling `enforcement-surface-map.md`; this map indexes',
  'transitions to their enforcers. *Map beats memory, substrate beats map.*', '');

// ════ 1. MCF Metric Contract family ════════════════════════════════════════════════════════════
push('## 1. MCF Metric Contract family (`mcf.metric_contract_version`)', '');
const mcvChecks = checksFor('mcf', 'metric_contract_version', 'governance_state_code');
for (const [name, def] of mcvChecks) {
  const states = statesFromCheck(def);
  if (states.length) push(`**States (from CHECK \`${name}\`):** ${states.map((s) => `\`${s}\``).join(' · ')}`, '');
}

const smDef = fnDef('mcf', 'fn_mcv_state_transition_check');
const pairs = [...smDef.matchAll(/OLD\.governance_state_code='([a-z_]+)'\s+AND NEW\.governance_state_code='([a-z_]+)'\)(?:\s*OR)?\s*(?:--\s*(.*))?/g)]
  .map(([, from, to, note]) => ({ from, to, note: (note ?? '').trim() }));
// A pair that ALSO appears in a RAISE EXCEPTION hard-close block is closed; detect by scanning
// for a dedicated refusal on the pair after the allowed-list (e.g. audit_blocked -> audit_pending).
const hardClosed = [...smDef.matchAll(/IF\s+OLD\.governance_state_code='([a-z_]+)'\s+AND\s+NEW\.governance_state_code='([a-z_]+)'\s+THEN\s+RAISE EXCEPTION/gs)]
  .map(([, from, to]) => `${from}->${to}`);
// enforcing objects per transition: which mcf/metric_audit fn bodies mention the cert action or pair
const gateFnNames = psql(`SELECT n.nspname, p.proname FROM pg_proc p
  JOIN pg_namespace n ON n.oid=p.pronamespace
  WHERE n.nspname IN ('mcf','metric_audit') AND (p.proname LIKE 'fn\\_%') ORDER BY 1,2`);
const gateFns = gateFnNames.map(([schema, name]) => [schema, name, fnDef(schema, name)]);
function enforcersFor(from, to) {
  const needle = `'${from}' AND NEW.governance_state_code='${to}'`;
  const alt = `from_state_code='${from}' AND `; // cert/evidence guards keyed by from/to
  return gateFns
    .filter(([, , def]) => def.includes(needle) || (def.includes(`'${from}'`) && def.includes(`'${to}'`) && /RAISE EXCEPTION/.test(def) && (def.includes(alt) || def.includes(`to_state_code='${to}'`))))
    .map(([schema, name]) => `\`${schema}.${name}\``);
}
push('**Transition matrix (parsed from the live `mcf.fn_mcv_state_transition_check`; the verbatim body follows):**', '');
push('| # | From | To | Machine note (verbatim comment) | Disposition | Enforcing objects (bodies in the enforcement map) |');
push('|---|---|---|---|---|---|');
pairs.forEach((p, i) => {
  const closed = hardClosed.includes(`${p.from}->${p.to}`);
  const enf = [...new Set(enforcersFor(p.from, p.to))].join(', ') || '`mcf.fn_mcv_state_transition_check`';
  push(`| ${i + 1} | \`${p.from}\` | \`${p.to}\` | ${p.note || '—'} | ${closed ? '**HARD-CLOSED** (listed, then refused)' : 'open (subject to listed gates)'} | ${enf} |`);
});
push('');
push('**The state machine, verbatim (ground truth for this table):**', '', '```sql', smDef, '```', '');
push('**Certification-action gates on this family** (bodies in `enforcement-surface-map.md`):',
  'the C6 invalidation cascade (`metric_audit.fn_c6_run_cascade` — entry to `audit_blocked`),',
  'the C7 reintake evidence + accepted-manifest/batch gates (`metric_audit.fn_c7_require_reintake_evidence`,',
  'reintake batch/member guards — `active → audit_pending`), and the C8 activation gate',
  '(`metric_audit.fn_c8_require_admit_evidence` + `fn_intrinsic_decision_ready` — `audit_pending → active`).', '');

// ════ 2. Business Concept Registry family ══════════════════════════════════════════════════════
push('## 2. Business Concept Registry family (`concept_registry.*`)', '');
const bcrTables = psql(`SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='concept_registry' AND c.relkind='r' ORDER BY 1`).map((r) => r[0]);
let bcrStateRendered = false;
for (const t of bcrTables) {
  const checks = psql(`SELECT con.conname, pg_get_constraintdef(con.oid) FROM pg_constraint con
    JOIN pg_class c ON c.oid=con.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='concept_registry' AND c.relname='${t}' AND con.contype='c' ORDER BY 1`);
  const stateChecks = checks.filter(([, d]) => /state|status|correction_class/i.test(d));
  const trigs = triggersFor('concept_registry', t);
  if (stateChecks.length || trigs.length) {
    push(`### \`concept_registry.${t}\``, '');
    for (const [name, def] of stateChecks) {
      const states = statesFromCheck(def);
      push(`- CHECK \`${name}\`: ${states.length ? states.map((s) => `\`${s}\``).join(' · ') : `\`${def.replace(/\s+/g, ' ').slice(0, 160)}\``}`);
      bcrStateRendered = bcrStateRendered || states.length > 0;
    }
    for (const [tg, fn] of trigs) push(`- trigger \`${tg}\` → \`${fn}\``);
    push('');
  }
}
push('**Honest gap (derived by absence):** the registry substrate above enforces state',
  'VOCABULARY, immutability, and amendment-class rules; no DB-side transition-ORDER guard',
  'exists for concept governance states. Transition order is enforced in the governed services',
  '(FrameworkApprovalService / operatorAdvance per DEC-47a4e7; supersession cascade per',
  'DEC-9d27a9; withdrawal per DEC-1fbaf1). This is a fact of the current substrate, rendered',
  'here so it can never be assumed otherwise.', '');

// ════ 3. Metric Directory Member family ════════════════════════════════════════════════════════
push('## 3. Metric Directory Member family (`metric_directory.*`)', '');
const dirTables = psql(`SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  WHERE n.nspname='metric_directory' AND c.relkind='r' ORDER BY 1`).map((r) => r[0]);
for (const t of dirTables) {
  const checks = psql(`SELECT con.conname, pg_get_constraintdef(con.oid) FROM pg_constraint con
    JOIN pg_class c ON c.oid=con.conrelid JOIN pg_namespace n ON n.oid=c.relnamespace
    WHERE n.nspname='metric_directory' AND c.relname='${t}' AND con.contype='c' ORDER BY 1`);
  const stateChecks = checks.filter(([, d]) => /state|status|class_code|disposition/i.test(d));
  const trigs = triggersFor('metric_directory', t);
  if (stateChecks.length || trigs.length) {
    push(`### \`metric_directory.${t}\``, '');
    for (const [name, def] of stateChecks) {
      const states = statesFromCheck(def);
      push(`- CHECK \`${name}\`: ${states.length ? states.map((s) => `\`${s}\``).join(' · ') : `\`${def.replace(/\s+/g, ' ').slice(0, 160)}\``}`);
    }
    for (const [tg, fn] of trigs) push(`- trigger \`${tg}\` → \`${fn}\``);
    push('');
  }
}
push('**Family doctrine rendered against substrate (DEC-b5c7ff, admitted per DEC-5a9dee):** a',
  'Member owns INTENT state only; realized state is DERIVED through the realization relation',
  '(`metric_directory.realization_operative` → `mcf.metric_contract_version`), never cached.',
  'Directory identity is load-bearing for MCF lifecycle acts: the C7 accepted-member tuple',
  'requires `member_uid` + `member_version_uid` (operative proof: DEC-21ca17).', '');

// ════ 4. Cross-family lifecycle spine ══════════════════════════════════════════════════════════
push('## 4. The cross-family lifecycle spine (derived reading order)', '');
push('Intent is authored in the Directory (member intent states) → meaning is bound in the',
  'Business Concept Registry (concept governance states; contract bodies reference concepts',
  'structurally) → the contract lives in MCF (seven states; certification gates activation at',
  'C8; C6 invalidates; C7 reintakes) → runtime consumers read `active` (selection into',
  'evaluation; readiness projection renders the certified/residue/unattributed split).',
  'Each arrow is a REFERENCE between families, never shared state — the families are decoupled',
  'by design (operator doctrine, 2026-08-03).', '');

writeFileSync(OUT, lines.join('\n'), 'utf8');
console.log(`wrote ${OUT} (${lines.length} lines)`);
