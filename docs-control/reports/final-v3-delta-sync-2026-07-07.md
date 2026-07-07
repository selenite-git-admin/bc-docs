# Final v3 Delta Sync — 2026-07-07

This report records the freeze-window delta sync from `bc-docs-v3` into `bc-docs-v4`.

- Inventory run id: `81`
- Source files copied/classified: `69`
- Method: copy latest v3 source bytes into v4 target path; add fresh source/decision rows in `docs-control.db`; update/insert target document provenance.

## Copied Sources

| Source | Target | Kind | SHA256 |
|---|---|---|---|
| `adrs/ADR-09f86b.md` | `docs/governance/adrs/ADR-09f86b.md` | `adr` | `5d4c33fcfcbdcaa44324297e3880b17a48e20307b6683ede2b2ff30f2ad7adbc` |
| `adrs/ADR-0cdfed.md` | `docs/governance/adrs/ADR-0cdfed.md` | `adr` | `da91dfaafba9c2c335369d5562d2a65f491e695a4b8c338d4d0e08ebb6768212` |
| `adrs/ADR-20eefe.md` | `docs/governance/adrs/ADR-20eefe.md` | `adr` | `2fff2b409f44712de29e7789393285d35cee69bc526691476c9aefe3ecf6e1ee` |
| `adrs/ADR-354552.md` | `docs/governance/adrs/ADR-354552.md` | `adr` | `053b889bc2d0a277fc9ef3187496313f37f698c97883f46dcad40b2eda61b9f9` |
| `adrs/ADR-4472ca.md` | `docs/governance/adrs/ADR-4472ca.md` | `adr` | `80731105f0105ba232f6b8702f23e80c32722c431300f1438a628fe9de4362de` |
| `adrs/ADR-61850f.md` | `docs/governance/adrs/ADR-61850f.md` | `adr` | `2fd3c9c603b4bf58cc6b08a14391ad2a5d899f918dedf4bf0fb6e306fb8b1957` |
| `adrs/ADR-95687d.md` | `docs/governance/adrs/ADR-95687d.md` | `adr` | `a4605b110b3eb2e08b4136f0fdd9281c128e7cb70d9a529a2ece9d7f31d86227` |
| `adrs/ADR-ebb3cd.md` | `docs/governance/adrs/ADR-ebb3cd.md` | `adr` | `72f87bed45a13d08153686f0ee3cda0b8f6993b21252d235dfba879584824211` |
| `adrs/README.md` | `docs/governance/adrs/README.md` | `adr` | `3f7d73ef5fd2230613d30f3711ceee824ccdf6125d452b7342da34e682fe69c5` |
| `implementation/data-model-and-schema.md` | `docs/implementation/data-model-and-schema.md` | `current_chapter` | `3c611a89bdb6ecea6ffc342815ff12a7f13d771a37c466a37d21863435d50bb0` |
| `implementation/mcf-re-entry-index.md` | `docs/reference/technical-notes/implementation/mcf-re-entry-index.md` | `curated_reference` | `8772c2d8877c7a66b1d0fb3f829a0d66961a543f0d87a9fe5437371a459aa431` |
| `implementation/synthetic-data-and-testing.md` | `docs/implementation/synthetic-data-and-testing.md` | `current_chapter` | `39958935613c338405bc28694412687bcd1e2904877b687945a45574465d70bc` |
| `onboarding/business-field-and-business-object-onboarding.md` | `docs/onboarding/business-field-and-business-object-onboarding.md` | `current_chapter` | `ec36623df7aea69c213c7664be9a6becac7b41228da6553febd47512cba7272f` |
| `onboarding/observation-contract-creation.md` | `docs/onboarding/observation-contract-creation.md` | `current_chapter` | `f9dfabccedd306d21e022a4b1f64470ee69fb5e87c058e1a67d86ad67ed00c6e` |
| `source-systems/sap-ecc.md` | `docs/reference/source-systems/sap-ecc.md` | `source_system_reference` | `9040b172f0a73143250af60369eba61a58be2fc7ec4aa98003309d09afb0da23` |
| `adrs/ADR-291614.md` | `docs/governance/adrs/ADR-291614.md` | `adr` | `aacf1ea2c9e06c88e1dcabcbfc97e0e779ff8d3f8772fde6744b0d46b58fd63b` |
| `adrs/ADR-2c2849.md` | `docs/governance/adrs/ADR-2c2849.md` | `adr` | `94e6ef0cb83b4e0be8381e26c0503b80b900129d68ed55bdcb8ef6c9ee29dfd8` |
| `adrs/ADR-3300f3.md` | `docs/governance/adrs/ADR-3300f3.md` | `adr` | `3d3ad9f8195a1f96e432eaff42afa30598a049bb749bbd656b344f8ffe463bef` |
| `adrs/ADR-4aa2fd.md` | `docs/governance/adrs/ADR-4aa2fd.md` | `adr` | `4d93d706875351f1d4da173001e035684224fd6af7eb82ba5c90c70adae07d8c` |
| `adrs/ADR-57c6d9.md` | `docs/governance/adrs/ADR-57c6d9.md` | `adr` | `0af04d0ee2f12b2c786d37dfc8fed0693c25a3db44d60fdef4cc2acd1a167983` |
| `adrs/ADR-75cb8a.md` | `docs/governance/adrs/ADR-75cb8a.md` | `adr` | `7e04a6c8272740e968112e8c329994a88b6881ccd62d6f0e64cfcf1102bf4471` |
| `adrs/ADR-a1290e.md` | `docs/governance/adrs/ADR-a1290e.md` | `adr` | `08c61b14fda94e4344ca870ab7a9bf97e01089b161b9f375cd570bd99dca3ebf` |
| `adrs/ADR-ada203.md` | `docs/governance/adrs/ADR-ada203.md` | `adr` | `f8af476e3218baf990f9373ee9ec2e5e6b732b6c3091edcab4ae316858d8b96c` |
| `adrs/ADR-ced5dc.md` | `docs/governance/adrs/ADR-ced5dc.md` | `adr` | `42b31ac9dfbb05e4290d394dd3d4cc33b8aadab5fdfcfcbfaf7ee07844ccf8b1` |
| `adrs/ADR-dbb511.md` | `docs/governance/adrs/ADR-dbb511.md` | `adr` | `d5b8f14aca08c314ab826ba876298f05b613e25a245f6ad335253f38a87d5496` |
| `adrs/ADR-e87701.md` | `docs/governance/adrs/ADR-e87701.md` | `adr` | `4adaf15d2dc3c5abf0a5aa8ffc609c2081f0f567fe59281b6a63ee77e93883b4` |
| `adrs/ADR-f4b2b0.md` | `docs/governance/adrs/ADR-f4b2b0.md` | `adr` | `767d7b2c901e6c312e2204f036f6133f3f7beab23933317aeeab7b10b5164dfc` |
| `adrs/ADR-f90ba3.md` | `docs/governance/adrs/ADR-f90ba3.md` | `adr` | `d06426fdbeb761e4da5e1f035e50c28a3e81b80239b4ae68b0e8d09b68149b8e` |
| `implementation/bcf-bc-coverage-ledger-view-2026-06-25.md` | `docs/evidence/ledgers/implementation/bcf-bc-coverage-ledger-view-2026-06-25.md` | `evidence_ledger` | `1feae1b2bc68d33dad048c0381754eee1f46633f9fb7540b6960d6eed12af7db` |
| `implementation/bcf-bc-coverage-ledger.json` | `docs/evidence/ledgers/implementation/bcf-bc-coverage-ledger.json` | `evidence_ledger` | `ee2c202e867c8746f638260cac11679c9834774c0fcba58791299b57d42f9a4d` |
| `implementation/bcf-desktop-prep-handoff-contract-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-desktop-prep-handoff-contract-2026-06-25.md` | `evidence_work_record` | `9c7f7edab9cd46caa2e6b155d006a055464ff4da054ca4db32a7973026ea7563` |
| `implementation/bcf-oagis-a0.5-template-catalogue-2026-06-24.md` | `docs/evidence/work-records/implementation/bcf-oagis-a0.5-template-catalogue-2026-06-24.md` | `evidence_work_record` | `7dc5a0002c6948de0eaf8e1157b4c1e71dac6cebf61f1356aa9b34a941329363` |
| `implementation/bcf-oagis-broad-buildout-blueprint-2026-06-23.md` | `docs/evidence/work-records/implementation/bcf-oagis-broad-buildout-blueprint-2026-06-23.md` | `evidence_work_record` | `39328384d367f46a14d364e77d6d83205cb6611fdb6b90191d90fa8df24220e6` |
| `implementation/bcf-oagis-compile-report-2026-06-24.md` | `docs/evidence/work-records/implementation/bcf-oagis-compile-report-2026-06-24.md` | `evidence_work_record` | `728026cbc228ee95d3f89963028996be7c7b8d4696297b4f4f1b383d4e9eddb6` |
| `implementation/bcf-oagis-pass-1-c1-closeout-2026-06-24.md` | `docs/evidence/closeouts/implementation/bcf-oagis-pass-1-c1-closeout-2026-06-24.md` | `evidence_closeout` | `a233ce91f2eace981fd3fd333857dab38c5fa64c2f9bee6d0172f8d5e893cbee` |
| `implementation/bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-closure-checkpoint-2026-06-25.md` | `evidence_work_record` | `fafc5fe67f59262d9ceb1d7c3d06310a6dfdee08116b30e98fa9a71aeb872110` |
| `implementation/bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-operator-decision-packet-2026-06-25.md` | `evidence_work_record` | `5f4c269b6c404e64ea6dbdd95a0a5a92f1e12279a9f47a1c03df61c1633be809` |
| `implementation/bcf-oagis-pass-1-c1-packet-builder-v2-design-2026-06-24.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-packet-builder-v2-design-2026-06-24.md` | `evidence_work_record` | `9b12eae282a1f27e94d3426094d54484080e52523c7a6c49180ee2a769959a75` |
| `implementation/bcf-oagis-pass-1-c1-repair-pass-2-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-repair-pass-2-2026-06-25.md` | `evidence_work_record` | `bafc8fe67832226ec2d301a7918c82565cc2751ec31cfe0f93727f53e614b376` |
| `implementation/bcf-oagis-pass-1-c1-repair-pass-2-packet-prep-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-repair-pass-2-packet-prep-2026-06-25.md` | `evidence_work_record` | `cd999817def10a2b3fe4ddc86256141a6165e6b6840c8e2ecafa591197a68117` |
| `implementation/bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-rp2-parked-row-analysis-2026-06-25.md` | `evidence_work_record` | `26d5742bf4bd3f6a4b9727dffd9cb794b3fff4a4f20a675941597eb7393c9201` |
| `implementation/bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md` | `docs/evidence/work-records/implementation/bcf-oagis-pass-1-c1-rp3-packet-prep-2026-06-25.md` | `evidence_work_record` | `1a3f6a5b8f44df54032a5bc0de46709e29e5b023c38e2bc740717b871d1f81eb` |
| `implementation/bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md` | `docs/evidence/closeouts/implementation/bcf-oagis-pass-1-c1-v2-closeout-2026-06-24.md` | `evidence_closeout` | `665e988de9eeefb03181c70c2ae76145e7207b8e25c7dc57423262e0764a94a4` |
| `implementation/bcf-oagis-retry-ledger-2026-06-24.md` | `docs/evidence/ledgers/implementation/bcf-oagis-retry-ledger-2026-06-24.md` | `evidence_ledger` | `18486f791107be796499ed6c5ce6aad1581498f97e4004bcf08cac906e394ecd` |
| `adrs/ADR-14f5b6.md` | `docs/governance/adrs/ADR-14f5b6.md` | `adr` | `6bd7a7b82c671c497d7d2c304cd6be476022c3f9fc126157de6d675b2ed0d95f` |
| `implementation/bcf-audit-remediation-closeout-2026-07-07.md` | `docs/evidence/closeouts/implementation/bcf-audit-remediation-closeout-2026-07-07.md` | `evidence_closeout` | `cbf97c0c26f73423c6a5ad62c1c14aed7cd510aa522b6f93aae81cd5d36be2c3` |
| `operations/d335/2026-04-15-audit-results.csv` | `docs/evidence/audits/operations/d335/2026-04-15-audit-results.csv` | `evidence_audit` | `eb53c0ec9b4e5703a660fd239a816ae6ad667b35d66dfe8ba5825fa491ee4cc9` |
| `operations/d335/2026-04-15-runway-diagnose.json` | `docs/evidence/audits/operations/d335/2026-04-15-runway-diagnose.json` | `evidence_audit` | `a91eb1b132eae54bdafb744b84e94075bfac0f188e00e919e5f556c72f91ba8d` |
| `operations/d335/chain-agent-results/chain-agent-results-accounts_payable.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-accounts_payable.json` | `evidence_audit` | `db03d71dda15b0f5da90933c83e1f76a58dd76eb9919aeb90408b099b4a3123f` |
| `operations/d335/chain-agent-results/chain-agent-results-accounts_receivable.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-accounts_receivable.json` | `evidence_audit` | `e640b1214628d26b30f8be08f37c0e50d7ae4dcfc1bfe8414fddb91a524de8a9` |
| `operations/d335/chain-agent-results/chain-agent-results-billing.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-billing.json` | `evidence_audit` | `fa8a6e89061146e2a4fac0cf25b5b449bf7462b353356810c9cf087b947e03d8` |
| `operations/d335/chain-agent-results/chain-agent-results-capital_structure_optimization.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-capital_structure_optimization.json` | `evidence_audit` | `82c87a6db0a45def3719f05394bbf5c9e4ab88d7974bce7fa899c8f9db03cf4c` |
| `operations/d335/chain-agent-results/chain-agent-results-cash_flow_management.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-cash_flow_management.json` | `evidence_audit` | `af00a5c08e72960b78f825ae71da90af730409d34c8fb3cdea0313b86effcef1` |
| `operations/d335/chain-agent-results/chain-agent-results-cost_accounting.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-cost_accounting.json` | `evidence_audit` | `cd0a1a93dc5d654ea93a4716947ae33f76bf45d9be0db58efad0ff55c4e9ba85` |
| `operations/d335/chain-agent-results/chain-agent-results-credit_and_collections.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-credit_and_collections.json` | `evidence_audit` | `353d3cc712ed6f078ac8e8a198d14cf2902994694e87038af5d0bba9d1ca2689` |
| `operations/d335/chain-agent-results/chain-agent-results-financial_reporting.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-financial_reporting.json` | `evidence_audit` | `4ebb1e3e7d62a5bccfd54651fc9ec76eba20b3bbd362fd770275a5f7eb004f5b` |
| `operations/d335/chain-agent-results/chain-agent-results-financial_risk_management.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-financial_risk_management.json` | `evidence_audit` | `e8d2c22ede96bb54d75a59aefd50d2231b3de07ccbe0b7e1936c0c7528b80ecf` |
| `operations/d335/chain-agent-results/chain-agent-results-financial_systems.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-financial_systems.json` | `evidence_audit` | `851281952686cd15a10aa6b38db3cab981febdb7f6b1596e371d3709fc7b2c86` |
| `operations/d335/chain-agent-results/chain-agent-results-fixed_assets.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-fixed_assets.json` | `evidence_audit` | `3344112307d33bd23963f2a143076a2883a2e192710af999124529de7dd9ed03` |
| `operations/d335/chain-agent-results/chain-agent-results-fpa.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-fpa.json` | `evidence_audit` | `c214b2d1f1873a5b89d7f01e72edc5c8b941a4a33a90d138d29b55de9a98f03c` |
| `operations/d335/chain-agent-results/chain-agent-results-general_finance.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-general_finance.json` | `evidence_audit` | `e48a6c540577d9f95bb97a6d2092d61107a490911235bdbdc2b7e2183949f6e8` |
| `operations/d335/chain-agent-results/chain-agent-results-general_ledger.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-general_ledger.json` | `evidence_audit` | `dbf7047b3c47a92465256d0f21cd8acd456735e9e2322a95dadabf3cd99d766a` |
| `operations/d335/chain-agent-results/chain-agent-results-internal_audit.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-internal_audit.json` | `evidence_audit` | `bb770dec81e6ad1f08d946012c3fa3e44cf4415be7c54f5b74eb2b38b5582109` |
| `operations/d335/chain-agent-results/chain-agent-results-investor_relations.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-investor_relations.json` | `evidence_audit` | `5336888a3a871b62c79e833c31348a37ede89dcc4ae4f6afb43723fdac4b17b9` |
| `operations/d335/chain-agent-results/chain-agent-results-iso_55001.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-iso_55001.json` | `evidence_audit` | `4553e581b938a177b4b13843572f16d5dade087f8093bd59d9d8b57cce0b76be` |
| `operations/d335/chain-agent-results/chain-agent-results-payroll.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-payroll.json` | `evidence_audit` | `504a6eaa3c4d72dd0e6f960e8fc041f4a0ea562f79af7b624737ccdd58aad15c` |
| `operations/d335/chain-agent-results/chain-agent-results-revenue_accounting.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-revenue_accounting.json` | `evidence_audit` | `f2f105f78d26fc3f87e408d3821b593b858e86baeeea047a28b96393b1296990` |
| `operations/d335/chain-agent-results/chain-agent-results-tax.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-tax.json` | `evidence_audit` | `b2a4e30c08ac403432a145a31a9c4b36a20eacc9bc0f504b4aaf3afc7c34e301` |
| `operations/d335/chain-agent-results/chain-agent-results-treasury.json` | `docs/evidence/audits/operations/d335/chain-agent-results/chain-agent-results-treasury.json` | `evidence_audit` | `77075e3e28e6eec3d0bdb223c77c6386c2f3a6c222f3cd0b4621d217d986b1aa` |

## Non-MD Evidence Decision

Raw JSON/CSV evidence that was outside the original md-only inventory is preserved under `docs/evidence/audits/` or `docs/evidence/ledgers/` with explicit `migrate_evidence` decisions in the final delta run.

## Asset Coverage Note

The original migration copied supporting assets under `docs/assets/` even when they were not first-class `source_documents`. The diagram check on 2026-07-07 verified `docs/assets/diagrams` has 11 files in v3 and 11 files in v4, with zero missing files and zero SHA256 differences. BCF UI screenshots, the conceptual deck, build script, and TSV data asset are also present under `docs/assets/`.

