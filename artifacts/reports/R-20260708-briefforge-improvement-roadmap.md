# BriefForge Improvement Roadmap for MetaHarvest Decision Support

Date: 2026-07-08
Status: recommendation roadmap only
Scope: architectural next workstream; no implementation authorization

## Roadmap conclusion

The next BriefForge workstream should not start with rendering, dashboards, templates, or visualization. It should start with a MetaHarvest Architectural Decision Package model.

BriefForge should become the layer that turns MetaHarvest investigations from evidence-rich documents into decision-ready architectural packages.

## Priority scale

- P0: highest-priority next architectural work; should be done before more renderer feature work.
- P1: important follow-on once P0 semantics are validated.
- P2: useful later; do not start until repeated evidence accumulates.
- Reject/defer: not justified by current evidence.

## P0 — Define a MetaHarvest Architectural Decision Package model

Problem:
- MetaHarvest reports contain evidence, patterns, and recommendations, but readers must manually assemble the decision structure.

Evidence:
- Third-generation campaign produced 50 reports, 39 source investigations, 8 domain comparisons, and 3 synthesis/final reports.
- Final/cross-domain reports identify many recurring patterns but do not consistently rank them by downstream actionability.
- Current BriefForge Presentation Grammar covers general report communication but not MetaHarvest-specific decision packaging.

Expected benefit:
- Converts large investigations into decision-support artifacts.
- Reduces first-pass reading burden.
- Gives downstream projects a clear path from evidence to action.

Implementation complexity:
- Medium.
- Mostly architectural/documentation/modeling work first; later implementation may be renderer-only or package-builder oriented if separately approved.

Architectural priority:
- P0.

Dependencies:
- Existing Presentation Grammar.
- Existing MetaHarvest project cards/component cards/reports.
- Existing BriefForge source-fidelity and traceability rules.

Belongs inside:
- BriefForge.

Reason:
- This is presentation/decision-support packaging, not evidence extraction. MetaHarvest should remain the evidence producer.

Non-goal:
- Do not modify MetaHarvest ingestion or BriefForge renderer behavior in this assessment task.

## P0 — Introduce structured recommendation objects for architectural investigations

Problem:
- Recommendations are currently prose bullets. They are not consistently actionable, ranked, scoped, or assigned.

Evidence:
- MetaHarvest final report contains recommendations such as modeling observations as context-qualified records and preserving methodology/taxonomy/version, but does not express them as decision objects with owner, complexity, confidence, dependencies, or blocker status.
- Project/component cards contain fields like confidence, adoption risk, implementation effort, and relevance, but reports do not consistently promote those into recommendations.

Expected benefit:
- Makes recommendations directly usable for MacroForge, BriefForge, KnowledgeForge, MetaHarvest, and future AtlasForge planning.
- Prevents broad architectural insights from becoming unowned advice.

Implementation complexity:
- Low to medium.
- Can begin as a documented schema/model before code.

Architectural priority:
- P0.

Dependencies:
- MetaHarvest evidence-quality and confidence fields.
- BriefForge Presentation Grammar attention hierarchy.

Belongs inside:
- BriefForge for presentation/recommendation model.
- MetaHarvest may later emit source data that maps into it, but ownership of decision packaging should sit in BriefForge.

Recommended fields:
- recommendation id;
- decision question;
- owner project;
- problem;
- recommended action;
- evidence summary;
- source diversity;
- confidence;
- expected benefit;
- complexity;
- adoption risk;
- dependencies;
- non-goals;
- next action;
- audit links.

## P0 — Add evidence-confidence and uncertainty framing to MetaHarvest presentations

Problem:
- Evidence is traceable but not weighted enough for decisions.

Evidence:
- Third-generation sources use documentation/specimen-first evidence and no repository materialization.
- Project/component cards record medium evidence quality/confidence and limitations, but reports do not consistently turn those fields into decision constraints.

Expected benefit:
- Prevents over-adoption from documentation-only evidence.
- Helps readers know what is safe to act on versus what requires materialization or follow-up.

Implementation complexity:
- Low to medium.
- Mostly a presentation model/report hierarchy issue initially.

Architectural priority:
- P0.

Dependencies:
- MetaHarvest `evidence_quality`, `confidence`, `analysis_limitations`, and materialization rationale fields.

Belongs inside:
- BriefForge for display/framing.
- MetaHarvest for upstream field availability and correctness.

## P0 — Require downstream implication mapping

Problem:
- Current reports often say findings are EIP/MacroForge relevant but do not distinguish which project should act.

Evidence:
- Representative component cards give MacroForge relevance scores but also mention report architecture, knowledge identity, and presentation implications that may belong to BriefForge or KnowledgeForge.
- The cross-domain synthesis lists opportunities for future primitive evaluation but does not partition by downstream project owner.

Expected benefit:
- Reduces ambiguity and prevents ProjectForge/BriefForge/MetaHarvest scope drift.
- Turns synthesis into a project-specific planning input.

Implementation complexity:
- Low.
- Can be specified as a required section of MetaHarvest decision packages.

Architectural priority:
- P0.

Dependencies:
- EIP project boundary knowledge.
- Existing downstream-boundary doctrine in BriefForge.

Belongs inside:
- BriefForge for report packaging.
- Consuming projects decide whether to adopt.

## P1 — Create a cross-source comparison matrix model

Problem:
- Domain comparisons are consistent but insufficiently comparative.

Evidence:
- Third-generation domain comparison reports list sources and candidate abstractions but do not show capability overlap, uniqueness, maturity, integration cost, or adoption risk side by side.

Expected benefit:
- Makes source families easier to compare.
- Helps identify adoption clusters and repeated strengths/weaknesses.

Implementation complexity:
- Medium.
- Requires a stable matrix schema and rules for not fabricating missing comparison dimensions.

Architectural priority:
- P1.

Dependencies:
- P0 recommendation object and evidence-confidence model.
- MetaHarvest project/component card fields.

Belongs inside:
- BriefForge for presentation model.
- MetaHarvest may later provide normalized input fields if needed.

Suggested dimensions:
- source;
- domain;
- capability solved;
- unique contribution;
- repeated pattern support;
- evidence mode;
- confidence;
- integration cost;
- adoption risk;
- EIP owner;
- recommended action.

## P1 — Add pattern recurrence and adoption-cluster maps

Problem:
- Pattern lists are long and not sufficiently operational.

Evidence:
- Third-generation final and synthesis reports list dozens of patterns and recurring abstractions.
- Readers must infer which patterns recur independently and which belong together as implementation opportunities.

Expected benefit:
- Converts vocabulary into architecture strategy.
- Helps identify common abstractions and candidate primitives without premature canonization.

Implementation complexity:
- Medium.
- Requires careful distinction between observed recurrence and adoption recommendation.

Architectural priority:
- P1.

Dependencies:
- MetaHarvest component-card pattern fields.
- P0/P1 comparison model.

Belongs inside:
- BriefForge for report surface.
- MetaHarvest remains source of pattern evidence.

## P1 — Define progressive disclosure levels for architectural investigations

Problem:
- Current reports are audit-friendly but not layered enough for different reader tasks.

Evidence:
- A reader must navigate final report, synthesis, comparison reports, individual reports, project cards, and component cards manually.
- Existing Presentation Grammar already distinguishes primary, secondary, supporting, and discoverable-on-demand material.

Expected benefit:
- Supports executive, architect, and auditor workflows without adding browser interactivity.

Implementation complexity:
- Low to medium.
- Can begin as report hierarchy and section model.

Architectural priority:
- P1.

Dependencies:
- Existing Presentation Grammar attention levels.
- Recommendation and evidence models.

Belongs inside:
- BriefForge.

Suggested layers:
- decision brief;
- recommendation index;
- synthesis layer;
- comparison layer;
- evidence layer;
- audit layer.

## P1 — Add an uncertainty and blocker register

Problem:
- Blind spots are present but not converted into operational blockers or follow-up queues.

Evidence:
- Third-generation reports identify blind spots such as filing-level examples, release calendar/revision examples, buy-side/sell-side report structure, implementation-level tradeoffs, and legal/licensing gaps.
- These are scattered across final/synthesis reports and individual reports.

Expected benefit:
- Prevents premature adoption.
- Gives MetaHarvest precise follow-up campaigns.

Implementation complexity:
- Low.

Architectural priority:
- P1.

Dependencies:
- Evidence-confidence model.

Belongs inside:
- BriefForge as presentation and planning surface.
- MetaHarvest for future investigation execution.

## P2 — Improve long-investigation navigation in static reports

Problem:
- Large investigations need navigation help, but current evidence points first to semantic layering rather than UI.

Evidence:
- Existing renderer backlog RB-008 says long-document navigation remains below operational recurrence threshold.
- Third-generation MetaHarvest expansion increases pressure, but the failure is decision hierarchy before interactivity.

Expected benefit:
- Better reading path for large reports after the semantic model is clear.

Implementation complexity:
- Medium if static only; high if interactive.

Architectural priority:
- P2.

Dependencies:
- P0/P1 semantic hierarchy.

Belongs inside:
- BriefForge renderer only if later approved.

Boundary:
- Do not implement interactive search/collapse/sticky navigation yet.

## P2 — Reassess static exhibits only after decision model exists

Problem:
- Exhibits may help quantitative or comparative evidence, but not if the underlying recommendation hierarchy is weak.

Evidence:
- TASK-032 and TASK-033 show bounded exhibit value for table/time-series evidence.
- The MetaHarvest expansion mostly exposes synthesis/comparison/decision-support gaps, not a missing chart engine.

Expected benefit:
- Avoids spending effort on visuals before knowing which comparisons matter.

Implementation complexity:
- Medium.

Architectural priority:
- P2.

Dependencies:
- P0 recommendation model and P1 comparison matrix.

Belongs inside:
- BriefForge renderer only if future evidence proves static exhibits materially improve decision quality.

## Rejected or deferred ideas

### Reject for now — Dashboard or portal architecture

Problem claimed:
- Large investigations may need navigation and search.

Evidence against immediate adoption:
- Current bottleneck is decision semantics, not browser interaction.
- BriefForge governance explicitly rejects dashboards/portals by default.

Expected benefit if built now:
- Low confidence; risks complexity without fixing prioritization.

Decision:
- Reject for this phase.

### Reject for now — JavaScript expand/collapse or interactive drill-down

Problem claimed:
- Reports are long and need progressive disclosure.

Evidence against immediate adoption:
- Progressive disclosure can first be modeled as report layers and indexes.
- Existing constraints forbid browser-app drift absent stronger evidence.

Decision:
- Reject for this phase.

### Defer — Graph visualization / dependency visualization

Problem claimed:
- Architectural relationships may need visual maps.

Evidence against immediate adoption:
- No current artifact proves that graph visualization is the highest-impact next step.
- A pattern/source/project matrix is simpler and more auditable.

Decision:
- Defer until matrix-based comparison fails.

### Defer — New renderer templates

Problem claimed:
- MetaHarvest reports need a distinct presentation shape.

Evidence against immediate adoption:
- The needed distinction is semantic hierarchy. Templates would be premature before the decision package model is defined.

Decision:
- Defer.

## Ranked next workstream

1. Define MetaHarvest Architectural Decision Package model.
2. Define structured recommendation objects.
3. Define evidence-confidence/uncertainty framing.
4. Define downstream implication mapping.
5. Define cross-source comparison matrix.
6. Define pattern recurrence/adoption-cluster maps.
7. Define static progressive disclosure levels.
8. Re-evaluate renderer/navigation/exhibit needs only after the model is validated on the third-generation MetaHarvest campaign.

## Success criteria for next phase

The next phase is successful if a reader can open one BriefForge-produced MetaHarvest decision package and answer within minutes:

- What are the top conclusions?
- What should be done next?
- Which EIP project owns each action?
- What evidence supports the recommendation?
- How confident are we?
- What blocks adoption?
- Where do I drill down if I need audit evidence?

No implementation is authorized by this roadmap alone.
