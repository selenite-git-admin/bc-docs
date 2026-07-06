-- bc-docs-v4 documentation control schema
-- SQLite is the control plane. Markdown remains the prose artifact.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT OR REPLACE INTO schema_meta(key, value) VALUES
  ('schema_name', 'bc-docs-v4-control'),
  ('schema_version', '0.1.0'),
  ('created_for', 'clean-room v4 documentation migration');

CREATE TABLE IF NOT EXISTS repositories (
  repo_id INTEGER PRIMARY KEY AUTOINCREMENT,
  repo_key TEXT NOT NULL UNIQUE,
  repo_name TEXT NOT NULL,
  root_path TEXT NOT NULL,
  role TEXT NOT NULL CHECK(role IN ('source_docs', 'target_docs', 'codebase', 'consumer', 'legacy_archive')),
  active_for_cutover INTEGER NOT NULL DEFAULT 0 CHECK(active_for_cutover IN (0, 1)),
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_runs (
  run_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_kind TEXT NOT NULL CHECK(run_kind IN ('source_inventory', 'target_inventory', 'coverage_inventory', 'audit')),
  source_repo_id INTEGER REFERENCES repositories(repo_id),
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  completed_at TEXT,
  tool_name TEXT NOT NULL,
  tool_version TEXT NOT NULL DEFAULT '0.1.0',
  status TEXT NOT NULL DEFAULT 'running' CHECK(status IN ('running', 'completed', 'failed')),
  summary_json TEXT,
  error_text TEXT
);

CREATE TABLE IF NOT EXISTS source_documents (
  source_doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES inventory_runs(run_id) ON DELETE CASCADE,
  repo_id INTEGER NOT NULL REFERENCES repositories(repo_id),
  rel_path TEXT NOT NULL,
  abs_path TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  byte_count INTEGER NOT NULL,
  line_count INTEGER NOT NULL,
  title TEXT,
  frontmatter_uid TEXT,
  frontmatter_id TEXT,
  frontmatter_status TEXT,
  frontmatter_authority TEXT,
  frontmatter_collection TEXT,
  frontmatter_order_text TEXT,
  top_level_dir TEXT,
  guessed_kind TEXT NOT NULL,
  guessed_domain TEXT,
  has_frontmatter INTEGER NOT NULL CHECK(has_frontmatter IN (0, 1)),
  imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(run_id, repo_id, rel_path)
);

CREATE INDEX IF NOT EXISTS idx_source_documents_repo_path ON source_documents(repo_id, rel_path);
CREATE INDEX IF NOT EXISTS idx_source_documents_kind ON source_documents(guessed_kind);
CREATE INDEX IF NOT EXISTS idx_source_documents_dir ON source_documents(top_level_dir);
CREATE INDEX IF NOT EXISTS idx_source_documents_sha ON source_documents(sha256);

CREATE TABLE IF NOT EXISTS migration_decisions (
  decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_doc_id INTEGER NOT NULL REFERENCES source_documents(source_doc_id) ON DELETE CASCADE,
  decision_code TEXT NOT NULL CHECK(decision_code IN (
    'migrate_current',
    'migrate_reference',
    'migrate_governance',
    'migrate_evidence',
    'archive_only',
    'regenerate_from_source',
    'superseded_do_not_migrate',
    'duplicate_do_not_migrate',
    'reject_do_not_migrate',
    'undecided'
  )),
  target_path TEXT,
  target_kind TEXT CHECK(target_kind IS NULL OR target_kind IN (
    'current_chapter',
    'generated_reference',
    'curated_reference',
    'adr',
    'errata',
    'source_system_reference',
    'evidence_dbcp',
    'evidence_closeout',
    'evidence_work_record',
    'evidence_audit',
    'evidence_ledger',
    'archive_only',
    'retired_not_migrated'
  )),
  reader_visibility TEXT NOT NULL DEFAULT 'hidden' CHECK(reader_visibility IN ('primary', 'reference', 'governance', 'evidence', 'archive', 'hidden')),
  current_truth INTEGER NOT NULL DEFAULT 0 CHECK(current_truth IN (0, 1)),
  rationale TEXT,
  decided_by TEXT NOT NULL DEFAULT 'inventory-rule',
  decided_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(source_doc_id)
);

CREATE TABLE IF NOT EXISTS target_documents (
  target_doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
  canonical_path TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  document_kind TEXT NOT NULL CHECK(document_kind IN (
    'current_chapter',
    'generated_reference',
    'curated_reference',
    'adr',
    'errata',
    'source_system_reference',
    'evidence_dbcp',
    'evidence_closeout',
    'evidence_work_record',
    'evidence_audit',
    'evidence_ledger',
    'archive_only'
  )),
  authority TEXT NOT NULL CHECK(authority IN ('authoritative', 'reference', 'evidentiary', 'informative', 'retired')),
  lifecycle_status TEXT NOT NULL CHECK(lifecycle_status IN ('drafting', 'reviewing', 'locked', 'generated', 'archived', 'retired')),
  reader_visibility TEXT NOT NULL CHECK(reader_visibility IN ('primary', 'reference', 'governance', 'evidence', 'archive', 'hidden')),
  current_truth INTEGER NOT NULL DEFAULT 0 CHECK(current_truth IN (0, 1)),
  source_doc_id INTEGER REFERENCES source_documents(source_doc_id),
  source_sha256 TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS extracted_links (
  link_id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_doc_id INTEGER NOT NULL REFERENCES source_documents(source_doc_id) ON DELETE CASCADE,
  link_text TEXT,
  raw_target TEXT NOT NULL,
  target_without_fragment TEXT,
  target_fragment TEXT,
  target_scheme TEXT,
  target_exists INTEGER CHECK(target_exists IN (0, 1)),
  target_scope TEXT CHECK(target_scope IS NULL OR target_scope IN ('internal', 'external_url', 'absolute_local', 'mcp', 'unknown')),
  finding_severity TEXT CHECK(finding_severity IS NULL OR finding_severity IN ('info', 'warning', 'error'))
);

CREATE INDEX IF NOT EXISTS idx_extracted_links_source ON extracted_links(source_doc_id);
CREATE INDEX IF NOT EXISTS idx_extracted_links_scope ON extracted_links(target_scope);

CREATE TABLE IF NOT EXISTS generated_references (
  generated_ref_id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_doc_id INTEGER REFERENCES target_documents(target_doc_id),
  reference_key TEXT NOT NULL UNIQUE,
  source_repo_key TEXT NOT NULL,
  source_commit TEXT,
  generator_name TEXT NOT NULL,
  generator_version TEXT,
  generated_at TEXT,
  source_fingerprint TEXT,
  freshness_status TEXT NOT NULL DEFAULT 'unknown' CHECK(freshness_status IN ('fresh', 'stale', 'unknown', 'regenerate_required')),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS coverage_targets (
  coverage_target_id INTEGER PRIMARY KEY AUTOINCREMENT,
  repo_key TEXT NOT NULL,
  target_type TEXT NOT NULL CHECK(target_type IN ('controller', 'route', 'schema', 'module', 'script', 'service', 'frontend_screen', 'config')),
  target_path TEXT NOT NULL,
  identifier TEXT,
  fingerprint TEXT,
  first_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_coverage_targets
  ON coverage_targets(repo_key, target_type, target_path, COALESCE(identifier, ''));

CREATE TABLE IF NOT EXISTS coverage_links (
  coverage_link_id INTEGER PRIMARY KEY AUTOINCREMENT,
  target_doc_id INTEGER REFERENCES target_documents(target_doc_id),
  source_doc_id INTEGER REFERENCES source_documents(source_doc_id),
  coverage_target_id INTEGER NOT NULL REFERENCES coverage_targets(coverage_target_id),
  relation_type TEXT NOT NULL CHECK(relation_type IN ('documents', 'mentions', 'governs', 'generated_from', 'stale_reference_to')),
  confidence TEXT NOT NULL DEFAULT 'medium' CHECK(confidence IN ('high', 'medium', 'low')),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS reader_collections (
  collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
  collection_key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS reader_nav_items (
  nav_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
  collection_id INTEGER NOT NULL REFERENCES reader_collections(collection_id),
  parent_nav_item_id INTEGER REFERENCES reader_nav_items(nav_item_id),
  target_doc_id INTEGER REFERENCES target_documents(target_doc_id),
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  visibility TEXT NOT NULL DEFAULT 'hidden' CHECK(visibility IN ('visible', 'hidden', 'planned')),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS stale_path_patterns (
  pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_text TEXT NOT NULL UNIQUE,
  severity TEXT NOT NULL CHECK(severity IN ('warning', 'error')),
  allowed_context TEXT NOT NULL DEFAULT 'explicit historical provenance only',
  replacement_guidance TEXT
);

CREATE TABLE IF NOT EXISTS audit_findings (
  finding_id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER REFERENCES inventory_runs(run_id),
  severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'error', 'blocker')),
  category TEXT NOT NULL,
  subject_path TEXT,
  subject_uid TEXT,
  message TEXT NOT NULL,
  suggested_action TEXT,
  status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open', 'accepted', 'fixed', 'deferred', 'false_positive')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO reader_collections(collection_key, label, sort_order, description) VALUES
  ('overview', 'Overview', 10, 'Reader landing and orientation'),
  ('foundation', 'Foundation', 20, 'Locked thesis and invariants'),
  ('operating_model', 'Operating Model', 30, 'How the platform works'),
  ('implementation', 'Implementation', 40, 'How the platform is built'),
  ('ai', 'AI', 50, 'AI participation and trust model'),
  ('development', 'Development', 60, 'Engineering practice and documentation system'),
  ('onboarding', 'Onboarding', 70, 'Governed build-up procedures'),
  ('operations', 'Operations', 80, 'Runtime and support operations'),
  ('compliance', 'Compliance', 90, 'Audit and control posture'),
  ('reference', 'Reference', 100, 'Generated and curated lookup material'),
  ('governance', 'Governance', 110, 'ADRs and errata'),
  ('evidence', 'Evidence Archive', 120, 'Dated evidence, DBCPs, closeouts, ledgers');

INSERT OR IGNORE INTO stale_path_patterns(pattern_text, severity, replacement_guidance) VALUES
  ('bc-docs-v2', 'error', 'Migrate, archive, or mark as historical provenance before cutover'),
  ('bc-docs-v3', 'warning', 'Allowed during v4 build; disallowed after final cutover'),
  ('BareCount-Documentation', 'error', 'Replace with v4 provenance or remove'),
  ('BareCount-Intra-Site', 'error', 'Replace with v4 provenance or remove'),
  ('documentation.cxofacts', 'error', 'Replace with v4 provenance or remove'),
  ('platform-documentation', 'error', 'Replace with v4 provenance or remove'),
  ('C:\MyProjects\bc-docs-v2', 'error', 'No absolute legacy doc roots in current docs'),
  ('C:\MyProjects\bc-docs-v3', 'warning', 'Allowed only in migration tooling before cutover');
