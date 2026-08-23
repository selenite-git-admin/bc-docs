---
uid: DEC-523a5d
title: "S/4HANA CDS View Catalog — Three Public Sources + Two Customer Access Models"
description: "Two-track CDS view strategy: public sources (GitHub JSON, CDS Finder Excel, se80.co.uk) + customer system access models"
status: implemented
subdomain: sap-catalog
focus: cds-catalog-access-models
date: 2026-03-07
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# S/4HANA CDS View Catalog — Three Public Sources + Two Customer Access Models

## Context

SAP licensing analysis reveals BareCount programmatically accessing SAP = indirect access by a third-party non-SAP application. SAP's Digital Access model exempts reads (no document creation), but the broad "Use" definition creates risk. Self-Service Transport (Model 1) is the only model with ZERO licensing exposure because BareCount never touches SAP — customer's own licensed user initiates the export, qualifying as Indirect Static Read.

Key SAP licensing references:
- SAP Digital Access: only charges for creation of 9 document types; reads/updates/deletes are free (https://redresscompliance.com/sap-digital-access-the-complete-guide/)
- SAP Note 3255746: RFC extraction by third parties is "unpermitted" (https://bryteflow.com/sap-bans-sap-rfc-extraction/)
- Indirect Static Read: SAP does not charge for read-only data exported by a licensed user (https://redresscompliance.com/sap-indirect-access-2025-rules-costs-risk/)
- Named User licensing: each user (human or system) needs individual license; sharing/multiplexing forbidden (https://saplicensingexperts.com/third-party-licensing-clauses-in-sap-contracts/)
- SAP User Types for RFC: System/Communication users still count as Named Users (https://dbosoft.eu/en-us/blog/using-sap-user-types-correctly)

S/4 coverage numbers: 7,626 released CDS views in Cloudification Repo; ~6,800 I_ interface views; 106K field mappings in CDS Finder Excel.

## Decision

S/4HANA CDS view coverage uses a two-track strategy:

**Track A — Pre-Customer (public sources, no auth required):**

1. SAP Cloudification Repository (GitHub JSON) — 7,626 released CDS views (6,801 I_ interface views) with name, module (applicationComponent), software component, and release state. NO field definitions. Direct download: https://raw.githubusercontent.com/SAP/abap-atc-cr-cv-s4hc/main/src/objectReleaseInfo_PCELatest.json
   Source: https://github.com/SAP/abap-atc-cr-cv-s4hc (Copyright 2020-2025 SAP SE)
   Viewer: https://sap.github.io/abap-atc-cr-cv-s4hc/

2. CDS Finder Excel (SAP Community) — 106,946 field-level mapping rows from S/4HANA 2023 FPS01. Maps CDS Entity → CDS Field → Base Table → Base Table Field. Includes C1 (ABAP Cloud) release status.
   Blog: https://community.sap.com/t5/technology-blog-posts-by-sap/how-to-find-a-cds-view-for-a-classic-table-in-abap-cheat-sheet/ba-p/13901500
   Download: https://sapext.sharepoint.com/:x:/s/AnonymousLinks/ETbTzSQVh9NEn1ZIsF95ckQBoDDiPYSyKdsgOnaE9tI00w (Password: CDSFinder@2025)

3. se80.co.uk S/4HANA Section — /sap-s4-hana-tables/ has S/4HANA persistence structures with full field definitions (name, description, data element, type, length, decimals, key flag). Structure names differ from CDS view names (e.g. ISSALESORDERTP → I_SALESORDER) but field content matches 1:1.
   Source: https://www.se80.co.uk/sap-s4-hana-tables/list/

**Track B — Customer Onboarding (when customer provides access):**

Primary (Model 1): Self-Service ABAP Transport — Customer installs ZBCNT_META_EXPORT report, runs it with their own licensed user, sends JSON output to BareCount. ZERO SAP licensing exposure. No indirect access. Qualifies as Indirect Static Read.

Premium (Model 4): SAP Integration Suite iFlow — BareCount Metadata Discovery iFlow deployed to customer's Integration Suite tenant. Runs inside customer's licensed SAP environment. SAP-to-SAP access. ZERO additional licensing.

**Models explicitly NOT used as primary:**
- OData API access by BareCount machine (gray area — indirect access by third-party system, defensible under Digital Access read exemption but risky)
- Named User for BareCount (wrong model — Named Users are for humans, BareCount is a machine)
- RFC-based access (BANNED by SAP Note 3255746, Feb 2024)

## Options Considered

N/A

## Consequences

N/A
