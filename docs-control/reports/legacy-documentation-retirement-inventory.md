# Legacy Documentation Retirement Inventory

Generated: `2026-07-06T11:57:12.992587+00:00`

## Safety Boundary

- Inventory only; this report does not move, delete, rename, or repoint any root.
- `bc-docs-v3` remains an active hold while Claude sessions rely on it.
- Roots already under `bc-docs-safe-delete` stay staged until the user approves physical deletion.
- Before deletion, run the cutover-reference plan and an external reference scan across repos, MCP configs, and Claude-facing files.

## Roots

| Name | State | Path | Files | Doc Files | Markdown | HTML | Size | Git Branch | Dirty Entries | Recommended Action |
|---|---|---|---|---|---|---|---|---|---|---|
| BareCount-Documentation | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\BareCount-Documentation | 104 | 60 | 59 | 0 | 2.1 MB | main | 16 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| BareCount-Intra-Site | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\BareCount-Intra-Site | 435 | 155 | 153 | 1 | 1.8 MB | main | 5 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| bc-docs | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\bc-docs | 1685 | 1445 | 1445 | 0 | 38.3 MB | main | 38 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| bc-docs-site | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\bc-docs-site | 304 | 257 | 0 | 257 | 41.3 MB |  | 0 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| bc-docs-v2 | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\bc-docs-v2 | 2853 | 2281 | 1177 | 1103 | 135.3 MB | main | 19 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| documentation.cxofacts | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\documentation.cxofacts | 854 | 538 | 254 | 283 | 35.3 MB | main | 156 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| platform-documentation | staged_safe_delete | C:\MyProjects\bc-docs-safe-delete\platform-documentation | 1481 | 1269 | 655 | 612 | 65.8 MB | main | 227 | already staged in bc-docs-safe-delete; verify no live references before physical deletion |
| bc-docs-v3 | active_v3_hold | C:\MyProjects\bc-docs-v3 | 1074 | 1013 | 1013 | 0 | 17.5 MB | docs/the-governed-selection | 37 | hold active v3 source; do not move, rename, or repoint while Claude sessions rely on it |
| bc-docs-v4 | active_v4 | C:\MyProjects\bc-docs-v4 | 1046 | 999 | 999 | 0 | 26.5 MB | main | 7 | active isolated successor; no cutover rename until explicitly approved |
