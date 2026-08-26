# Architectural Decision Package Model

Date: 2026-07-08
Status: architectural model definition; no runtime implementation
Scope: BriefForge semantic decision-support architecture

## Executive conclusion

BriefForge should adopt the Architectural Decision Package Model (ADPM) as its canonical decision-support semantic layer.

The smallest complete package of information required for an architect to make a high-confidence architectural adoption decision without reading an entire investigation is:

1. a bounded decision question;
2. a recommended disposition;
3. a planning horizon;
4. affected scope and ownership;
5. evidence for and against;
6. confidence and uncertainty;
7. assumptions;
8. risks and consequences;
9. alternatives considered;
10. dependencies;
11. downstream architectural and implementation impacts;
12. follow-up actions and open questions;
13. traceability to source provenance and audit evidence.

Everything else is either presentation, navigation, renderer behavior, or implementation convenience.

ADPM is not a report template. It is not a renderer contract. It is not a dashboard model. It is a semantic model for packaging architectural decisions so that downstream projects and human architects can decide what to adopt, reject, defer, investigate, or ignore.

## Architectural motivation

BriefForge already improved coherence, source fidelity, evidence visibility, and report organization. The latest large upstream investigation corpus showed that these improvements are necessary but insufficient. Readers can follow the evidence, but they still must manually infer:

- which conclusions matter most;
- which action is recommended;
- which project should act;
- how confident the recommendation is;
- which uncertainty should block adoption;
- what happens if nothing is done;
- whether a recommendation is urgent, near-term, speculative, rejected, or superseded.

That inference burden is architectural, not cosmetic. Improving visual layout alone would not answer the decision question.

## Problem statement

Current report-oriented presentation packages are coherent documents. They are not yet complete architectural decision objects.

A coherent report can still fail as a decision-support artifact if it lacks:

- an explicit decision question;
- ranked recommendation semantics;
- evidence opposition, not only supporting evidence;
- confidence and uncertainty separation;
- planning horizon;
- owner/project impact;
- alternatives and consequences;
- dependency and follow-up structure;
- traceability from recommendation back to evidence.

The architectural problem is therefore to define a renderer-independent semantic package that allows a reader to decide without reading the entire investigation first, while preserving auditability for deeper review.

## Design goals

ADPM must:

1. improve architectural decision-making, not appearance;
2. remain renderer-independent;
3. preserve upstream ownership of evidence and domain judgments;
4. make recommendations complete enough for governance use;
5. expose confidence, uncertainty, risks, assumptions, and consequences early;
6. distinguish accepted recommendation from observation, hypothesis, evidence, and follow-up;
7. generalize across all current and future EIP projects;
8. scale to hundreds of projects and thousands of findings;
9. allow future renderers to consume the model without influencing it;
10. reject any field that merely supports UI decoration.

## Non-goals

ADPM does not define:

- HTML;
- dashboards;
- charts;
- templates;
- CSS;
- JavaScript;
- expandable sections;
- search;
- portals;
- graph visualization;
- presentation components;
- runtime behavior;
- data ingestion;
- upstream evidence extraction;
- consumer-project implementation tasks.

## Rejected alternatives

### Alternative 1: Improve renderer/navigation first

Rejected.

Reason:
- current evidence shows the missing layer is decision compression, not visual mechanics;
- renderer features cannot determine recommendation completeness, confidence, ownership, or consequences;
- UI-first evolution risks encoding premature report shapes before the semantic decision model is stable.

### Alternative 2: Treat ADPM as a report template

Rejected.

Reason:
- templates define recurring layout;
- ADPM defines semantic responsibilities and completeness constraints;
- multiple templates or renderers may later express the same ADPM differently.

### Alternative 3: Push decision support into upstream evidence producers

Rejected.

Reason:
- upstream projects own evidence, analysis, source provenance, and domain interpretation;
- BriefForge owns presentation/decision packaging semantics;
- consumer projects own adoption decisions;
- conflating these responsibilities would weaken repository sovereignty.

### Alternative 4: Use only prose executive summaries

Rejected.

Reason:
- prose summaries improve readability but do not create a complete decision object;
- architectural governance needs structured fields for evidence, uncertainty, risks, dependencies, and traceability;
- summaries without invariants are not enough for validation.

### Alternative 5: Create a generic knowledge graph model

Rejected/deferred.

Reason:
- graph structure may become useful later, but current evidence requires decision objects, not graph visualization;
- graph models add abstraction before proving the decision completeness contract;
- ADPM can later be mapped into graph form without being designed as a graph engine.

## Phase 1: Decision ontology

ADPM uses a small ontology. Objects are included only when they materially improve decision quality.

### 1. Architectural Decision Package

Responsibility:
- the bounded semantic container for one architectural decision-support package.

It answers:
- what decision space is being packaged;
- why the package exists;
- which recommendations it contains;
- what evidence, confidence, uncertainty, and impacts govern those recommendations.

It must not become:
- a rendered report;
- a dashboard;
- a project backlog;
- a task tracker;
- a source repository index.

### 2. Decision Question

Responsibility:
- defines the exact architectural question the package helps answer.

A package without a decision question is just a report.

Examples:
- Should a downstream project adopt this architectural pattern?
- Should this capability be built now, deferred, or rejected?
- Which source family should influence the next architectural model?

### 3. Decision Disposition

Responsibility:
- states the recommended outcome for the decision question.

Canonical dispositions:
- adopt;
- adapt;
- investigate;
- defer;
- reject;
- monitor;
- supersede.

Disposition is distinct from planning horizon. A recommendation may be accepted but long-term, rejected immediately, or deferred pending evidence.

### 4. Recommendation

Responsibility:
- the actionable proposal inside the package.

A recommendation connects a decision question to an action, owner, evidence basis, confidence, risks, assumptions, alternatives, consequences, dependencies, and follow-up.

Recommendations are the central operational object of ADPM.

### 5. Evidence Reference

Responsibility:
- identifies upstream-owned evidence that supports, weakens, contextualizes, or constrains a recommendation.

Evidence references must preserve source provenance. BriefForge may package evidence references but does not convert upstream evidence into BriefForge-owned analytical truth.

Evidence roles:
- supports;
- opposes;
- qualifies;
- background;
- missing.

### 6. Confidence Assessment

Responsibility:
- states how strongly the package supports the recommendation and why.

Confidence must not collapse uncertainty. A recommendation may have medium confidence because support is strong but evidence mode is limited, or high confidence for public architecture but low confidence for implementation internals.

Confidence includes:
- level;
- rationale;
- evidence mode;
- evidence diversity;
- confidence reducers;
- confidence improvers.

### 7. Uncertainty

Responsibility:
- records what remains unknown and whether it should block action.

Uncertainty categories:
- blocker;
- material but non-blocking;
- monitoring required;
- acceptable residual uncertainty;
- unknown due to missing evidence.

### 8. Assumption

Responsibility:
- records a proposition the recommendation depends on but has not fully proven.

Assumptions make decision risk explicit and reviewable.

### 9. Risk

Responsibility:
- records a possible negative outcome if the recommendation is accepted, delayed, or rejected.

Risks must be tied to consequences and mitigation/follow-up where possible.

### 10. Alternative

Responsibility:
- records plausible competing choices and why they were not chosen.

Alternatives prevent recommendation monoculture and make tradeoffs explicit.

### 11. Consequence

Responsibility:
- records expected outcomes of accepting the recommendation, rejecting it, or doing nothing.

ADPM requires explicit no-action consequences because many architectural decisions decay silently when not acted upon.

### 12. Dependency

Responsibility:
- records prerequisites or coupled work needed before a recommendation can be executed safely.

Dependencies may be evidence, architecture, project ownership, sequencing, or governance dependencies.

### 13. Impact

Responsibility:
- describes affected architectural and implementation areas without assigning implementation authority.

Impact categories:
- architectural impact;
- implementation impact;
- operational impact;
- validation impact;
- governance impact;
- downstream project impact.

### 14. Follow-up Action

Responsibility:
- defines bounded next work that would increase confidence, reduce risk, or execute an accepted recommendation.

Follow-up actions are not tasks unless separately accepted by the owning project.

### 15. Open Question

Responsibility:
- records a question that remains unresolved after the package.

Open questions prevent weak recommendations from appearing more certain than they are.

### 16. Traceability Link

Responsibility:
- connects each recommendation to evidence, source provenance, prior decisions, and downstream implications.

Traceability is mandatory because ADPM must remain auditable even when it reduces first-pass reading burden.

### 17. Source Provenance

Responsibility:
- records where evidence came from and what kind of evidence it is.

Source provenance belongs to upstream evidence ownership. BriefForge preserves it.

### 18. Planning Horizon

Responsibility:
- classifies when and how a recommendation should influence planning.

Planning horizon is included because it materially improves governance and backlog prioritization.

## Removed or merged candidate concepts

The following concepts are not first-class ADPM objects:

- Observation: represented as evidence or source note unless it affects a recommendation.
- Finding: represented as evidence-backed claim inside a recommendation or package summary.
- Hypothesis: represented as recommendation with investigate/defer disposition plus assumptions/open questions.
- Capability map: deferred as a possible aggregate view derived from multiple packages.
- Visualization: excluded; presentation concern.
- Navigation path: excluded; renderer/presentation concern.
- Executive summary: not a semantic object; future presentations may summarize ADPM objects.

## Phase 2: Decision completeness

A recommendation is architecturally complete only when it answers the minimum decision questions below.

### Mandatory recommendation completeness requirements

Every recommendation must include:

1. Recommendation identity
   - stable id;
   - title;
   - package membership.

2. Decision question
   - the architectural decision being proposed.

3. Disposition
   - adopt, adapt, investigate, defer, reject, monitor, or supersede.

4. Recommended action
   - what should be done or not done.

5. Why now
   - why the recommendation matters at this point in the project lifecycle.

6. Owner / affected scope
   - project, domain, or decision owner most likely affected;
   - explicitly may be none if the recommendation is informational.

7. Planning horizon
   - blocker, immediate, near-term, medium-term, long-term, deferred, rejected, or superseded.

8. Evidence for
   - at least one supporting evidence reference or an explicit statement that evidence is absent.

9. Evidence against / limiting evidence
   - contradictory, weak, missing, or confidence-reducing evidence.

10. Confidence assessment
   - level and rationale.

11. Remaining uncertainty
   - blocker or non-blocker classification.

12. Assumptions
   - explicit assumptions or `none identified`.

13. Risks
   - risks of accepting, delaying, or rejecting where applicable.

14. Consequences
   - expected consequence of acceptance;
   - expected consequence of no action.

15. Dependencies
   - prerequisites or `none identified`.

16. Alternatives considered
   - at least one plausible alternative or `none identified` with rationale.

17. Future work displacement
   - which future work becomes unnecessary, safer, or newly required if accepted.

18. Confidence improvement path
   - what additional investigation would increase confidence.

19. Traceability
   - links to source evidence, prior decisions, reports, or upstream artifacts.

### Why these are mandatory

These fields are not bureaucratic completeness. They correspond to the human decision process:

- decide what is being proposed;
- know why it matters now;
- inspect why the proposal is credible;
- see what could make it wrong;
- understand cost of action and inaction;
- know who owns the next move;
- know what evidence would change the decision.

A recommendation missing these fields may still be useful prose, but it is not an architecturally complete ADPM recommendation.

## Phase 3: Decision horizon

ADPM should include an explicit planning horizon.

### Rationale

Planning horizon improves governance because it separates importance from timing.

A recommendation can be:

- important but not urgent;
- urgent but low-complexity;
- rejected but still useful as a guardrail;
- deferred until evidence improves;
- superseded by a stronger later decision.

Without horizon, backlogs tend to mix blockers, opportunities, research ideas, and rejected concepts into one queue.

### Canonical horizon categories

1. Immediate architectural blocker
   - must be resolved before safe continuation or adoption.

2. Immediate high-value capability
   - should be considered next because evidence and benefit are strong.

3. Near-term improvement
   - valuable after the current blocker/high-value work.

4. Medium-term capability
   - useful but depends on prior model, evidence, or implementation maturity.

5. Long-term research
   - important uncertainty but not ready for operational execution.

6. Deferred investigation
   - intentionally postponed until trigger evidence appears.

7. Rejected
   - not recommended; retained to prevent repeated reconsideration.

8. Superseded
   - replaced by a newer decision or stronger model.

### Interaction with backlog prioritization

Planning horizon is not the backlog priority by itself.

Backlog priority should derive from:

- horizon;
- confidence;
- expected benefit;
- risk of inaction;
- dependency readiness;
- affected owner capacity;
- strategic relevance.

ADPM provides the semantics; the owning project decides backlog acceptance.

## Phase 4: Generality and project independence

ADPM must not be source-specific.

The model generalizes because every current and future EIP project may produce or consume architectural decisions:

- MetaHarvest may produce evidence-heavy architecture investigations.
- MacroForge may need source/domain adoption decisions.
- InsightForge may need analytical finding publication decisions.
- KnowledgeForge may need knowledge-structure and retrieval decisions.
- ProjectForge may need methodology/governance decisions.
- BriefForge may need presentation/decision-package decisions.
- Future projects may need adoption, deferral, rejection, or investigation decisions.

The package is therefore defined around universal architectural decision semantics:

- decision question;
- recommendation;
- evidence;
- confidence;
- uncertainty;
- ownership;
- impacts;
- consequences;
- follow-up.

No field requires a specific upstream project, source type, rendering target, or investigation corpus.

## Phase 5: Separation of concerns

ADPM defines semantic information only.

### Semantic layer

ADPM owns:

- object identity;
- decision question;
- recommendation semantics;
- evidence roles;
- confidence/uncertainty semantics;
- risk/assumption/consequence semantics;
- owner/impact semantics;
- traceability requirements;
- invariants and completeness rules.

### Presentation layer

Presentation may decide:

- ordering;
- summarization;
- attention level;
- narrative framing;
- progressive disclosure in a medium-independent sense.

Presentation must not change ADPM meaning.

### Rendering layer

Rendering may decide:

- HTML, Markdown, PDF, terminal, slide, or other target;
- visual layout;
- typography;
- static navigation;
- formatting.

Rendering must consume ADPM objects, not define them.

### Interaction layer

Interaction may later decide:

- expand/collapse;
- filtering;
- search;
- sorting;
- graph exploration;
- dashboard behavior.

Interaction is explicitly out of scope for ADPM.

### Visualization layer

Visualization may later express:

- matrices;
- maps;
- graphs;
- timelines;
- dependency diagrams.

Visualization must be derived from ADPM semantics and must not create semantic authority.

## Scalability analysis

ADPM scales better than linear reports because it creates stable units of decision rather than relying on document traversal.

At small scale:
- a single package can summarize one investigation and provide a recommendation index.

At medium scale:
- multiple recommendations can be filtered by owner, horizon, confidence, risk, or source evidence.

At large scale:
- packages can be aggregated into owner-specific queues, capability maps, recurring pattern views, and audit trails without changing the semantic contract.

The key scalability benefit is not shorter text. It is that the reader can enter through the decision object and drill down only when needed.

## Constitutional implications

ADPM expands BriefForge's semantic foundation from general Presentation Package communication toward decision-support packaging.

This does not make BriefForge the owner of upstream analytical truth, evidence extraction, project adoption, backlog execution, rendering, or UI.

It means BriefForge may define and validate structured decision-support packages that preserve upstream evidence ownership while making architectural decisions complete, comparable, and auditable.

## Architectural risks

1. Scope drift into governance authority
   - Mitigation: ADPM recommendations do not execute; consuming projects decide adoption.

2. Scope drift into upstream analysis
   - Mitigation: evidence references preserve upstream ownership and provenance.

3. Scope drift into renderer/UI
   - Mitigation: ADPM forbids renderer assumptions in the semantic model.

4. Overmodeling
   - Mitigation: only mandatory fields tied to decision completeness are canonical.

5. False precision
   - Mitigation: confidence must include rationale, evidence mode, and reducers.

## Recommended next state

Accept ADPM as BriefForge's canonical semantic decision-support model.

Do not implement runtime behavior yet.

Next valid work after this task should be one of:

1. manual validation of ADPM against representative existing investigation packages;
2. schema/validation design for ADPM as an implementation-planning task;
3. package-builder design only after manual validation proves the model stable.

Renderer work remains downstream and should wait until ADPM semantics prove what presentation pressure remains.
