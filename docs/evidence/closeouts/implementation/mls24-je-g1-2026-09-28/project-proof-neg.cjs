// Read-only: run the served build's MetricProofProjection against tbc_kaveri_dev.
// Every query runs inside BEGIN READ ONLY ... ROLLBACK via docker exec psql.
const path = require('path');
const { execFileSync } = require('child_process');
const WT = '/Users/anant/MyProjects/_wt/freeze-e';
const { PgDialect } = require(path.join(WT, 'node_modules/drizzle-orm/pg-core'));
const { projectMetricSnapshotProof } = require(path.join(WT, 'dist/evidence/metric-proof-projection.js'));

const dialect = new PgDialect();
const lit = (v) => {
  if (v === null || v === undefined) return 'NULL';
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  return `'${String(v).replace(/'/g, "''")}'`;
};
function render(query) {
  const { sql, params } = dialect.sqlToQuery(query);
  return sql.replace(/\$(\d+)/g, (_, n) => lit(params[Number(n) - 1]));
}
const exec = {
  async execute(query) {
    const inner = render(query);
    const out = execFileSync('docker', ['exec', '-i', 'bc-postgres', 'psql', '-U', 'barecount', '-d', 'tbc_kaveri_dev', '-At', '-v', 'ON_ERROR_STOP=1'], {
      input: `BEGIN READ ONLY;\nSELECT coalesce(json_agg(t), '[]'::json) FROM (${inner}) t;\nROLLBACK;\n`,
      encoding: 'utf8',
    });
    const line = out.split('\n').find((l) => l.startsWith('['));
    return JSON.parse(line);
  },
};

const scope = {
  mcUid: 'c5ebf6d5-0a64-4efc-9415-2b7cf45e8177', mcVersion: '1.0.0', fiscalPeriod: 'FY2026-27/P04',
  legalEntityCode: process.env.LE || 'KAVERI-IN', fiscalCalendarCode: 'IN-APR-MAR-MONTHLY',
};
const binding = { factTable: 'fact.ms_total_journal_entries_v1_0_0', periodColumn: 'fiscal_period', grainColumns: [] };
(async () => {
  for (const snapshotId of process.argv.slice(2)) {
    const r = await projectMetricSnapshotProof(exec, { tenantId: 'kaveri', binding, snapshotId, expectedScope: scope });
    console.log(JSON.stringify({ snapshotId, ...r }, null, 2));
  }
})();
