---
artifact_type: analytical_artifact
schema_version: 1
id: IF-A-20260619-002
subtype: finding
status: reviewed
created_at: 2026-06-19
updated_at: 2026-06-19
title: Eurostat Germany and France quarterly GDP direction of change, 2023 Q1 to 2023 Q2
question: Within the Eurostat quarterly GDP rows in MacroForge's canonical GDP snapshot, what descriptive direction-of-change conclusion is justified for Germany and France from 2023 Q1 to 2023 Q2?
conclusion: In the Eurostat quarterly GDP rows included in MacroForge's canonical GDP snapshot, Germany's value is lower in 2023 Q2 than in 2023 Q1, while France's value is higher in 2023 Q2 than in 2023 Q1. Germany changes from 1043520.0 to 1031880.0 CP_MEUR. France changes from 684762.7 to 706147.7 CP_MEUR. This supports only a same-source, same-frequency, same-unit descriptive finding.
evidence:
  - id: E1
    source_project: MacroForge
    source_artifact: /home/mkkto/srv/EIP/projects/MacroForge/artifacts/reports/canonical-gdp-snapshot-20260604.json
    source_location: gdp_snapshot.observations rows where source_code=EUROSTAT_NAMQ_GDP, territory_code in [DEU, FRA], period_label in [2023 Q1, 2023 Q2]
    cited_fields: [source_code, territory_code, territory_name, period_label, frequency, indicator_code, indicator_name, unit_code, value, as_of_date, release_key]
    role: primary
  - id: E2
    source_project: MacroForge
    source_artifact: /home/mkkto/srv/EIP/projects/MacroForge/artifacts/reports/canonical-gdp-snapshot-20260604.json
    source_location: status, task, checks, data_quality, missingness, metadata.notes, source_lineage row where source_code=EUROSTAT_NAMQ_GDP
    cited_fields: [status, task, checks, core_query_boundary, duplicate_fact_grain_count, failing_quality_checks, missing_observation_count, generated_at, notes, dataset_release_count, lineage_event_count, latest_to_artifact]
    role: lineage
  - id: E3
    source_project: MacroForge
    source_artifact: /home/mkkto/srv/EIP/projects/MacroForge/artifacts/manifests/canonical_assets.json
    source_location: assets where asset_key=mapping.eurostat_namq_gdp.to_macro_gdp_output and report.canonical_gdp_snapshot
    cited_fields: [asset_key, role, status, notes_caveats, owner_or_review_authority]
    role: caveat
caveats:
  - This is a Eurostat-only descriptive finding over four quarterly rows in one MacroForge snapshot.
  - It covers only 2023 Q1 and 2023 Q2 for Germany and France.
  - It does not annualize quarterly data or aggregate frequency.
  - It does not compare Eurostat to WDI, OECD, or any other source.
  - It does not perform currency conversion, inflation adjustment, seasonal adjustment review, or forecasting.
  - MacroForge's canonical asset manifest says the Eurostat mapping state is provisional and current-price million euro values require conversion policy before broader comparison.
  - The conclusion must not be treated as an investment signal, thesis, or causal explanation.
confidence:
  level: medium
  justification: The same-source, same-unit, same-frequency direction comparison is direct and reproducible from four observed Eurostat rows in a succeeded MacroForge report with passing checks, but confidence remains medium because Eurostat mapping status is provisional and broader comparison/conversion policy is deferred.
reproducibility:
  method: Read the four Eurostat rows for DEU and FRA in periods 2023 Q1 and 2023 Q2; compare each territory's Q2 value numerically against its Q1 value; conclude higher/lower direction only.
  inputs:
    - /home/mkkto/srv/EIP/projects/MacroForge/artifacts/reports/canonical-gdp-snapshot-20260604.json
    - /home/mkkto/srv/EIP/projects/MacroForge/artifacts/reports/canonical-gdp-snapshot-20260604.md
    - /home/mkkto/srv/EIP/projects/MacroForge/artifacts/manifests/canonical_assets.json
  deterministic: true
  requires_external_services: false
review:
  reviewer: Hermes
  reviewed_at: 2026-06-19
  review_notes: Manual evidence/caveat/reproducibility review completed; artifact remains bounded to same-source quarterly direction-of-change.
---

# Eurostat Germany and France quarterly GDP direction of change, 2023 Q1 to 2023 Q2

## Manual comparison

| Territory | 2023 Q1 value | 2023 Q2 value | Unit | Direction |
| --- | ---: | ---: | --- | --- |
| DEU | 1043520.0 | 1031880.0 | CP_MEUR | Lower in Q2 |
| FRA | 684762.7 | 706147.7 | CP_MEUR | Higher in Q2 |

## Bounded conclusion

Germany decreases and France increases across the two selected Eurostat quarterly rows. The artifact does not assert causality, cross-source comparability, annual growth, or investment significance.
