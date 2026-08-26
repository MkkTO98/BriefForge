# Controlled Renderer Invocation and Artifact-Evidence Contract

Version: `1.0.0`
Policy: `briefforge-controlled-renderer-invocation-policy:1.0.0`
Status: Accepted for TASK-052

## Input closure

Exactly one invocation transaction consumes detached exact-type values for:

- a complete TASK-050 Release closure plus its exact evidence snapshot;
- the complete TASK-049 lifecycle Release/event/policy catalog;
- one verified TASK-051 compatibility Plan closure and its original declaration and planning authorization;
- one exact TASK-052 invocation authorization;
- the exact fixed `minimal-html-renderer` contract and implementation version.

The implementation must rerun the authoritative Release, lifecycle and Plan verifiers immediately before projection or renderer execution. Possession of records or previous verification results grants no invocation authority.

## Fixed projection

The projection must be derived only from the independently reverified BCRP Brief, Material, Candidate and exact Plan mappings. It must preserve explicit identity, purpose, statement text/posture, authority/provenance links, obligations and encounter order. It must consume every Plan mapping once and only the selected expression named by that mapping.

It must not construct or accept `ReadyPresentationPackage`, infer new semantics, inspect TASK-039 artifacts, follow external references, query data or use renderer fallback not selected by the Plan.

## Renderer identity

The only admitted renderer is:

- planning identity: `renderer:minimal-html`;
- implementation adapter: `minimal-html-renderer`;
- media type: `text/html`;
- fixed output filename: `publication.html`;
- external asset policy: `none`.

The capability declaration remains a trusted renderer-owned claim, not proof. Invocation binds the SHA-256 digest of the exact renderer source, loaded local/external function closure, fixed worker source and projection-loader code. Each execution launches the fixed worker in a fresh subprocess with a minimal explicit environment and fixed interpreter flags, then rechecks the implementation digest before calling the renderer. Artifact conformance remains unassessed.

## Authorization

`RendererInvocationAuthorization` is exact, immutable and one-act. It binds policy, authority, authorization identity/time, Release fingerprint, lifecycle-scope fingerprint, Plan fingerprint, capability fingerprint, renderer identity/adapter/version/source digest, projection fingerprint, a separate absolute authorization-ledger directory, absolute empty output directory, output filename/count/size/media type, environment, external-asset policy and invocation mode.

Before either execution, invocation atomically creates and fsyncs one fingerprint-named consumption marker in the separately authorized ledger. The marker is permanent authority-consumption state and is not a publication artifact. Its retained integrity is an explicit operating trust assumption: deleting, replacing or tampering with the authorized ledger is out-of-bound authority-state corruption. Output-file or output-directory deletion/recreation does not restore authorization.

The admitted invocation mode is `one-artifact-with-determinism-replay`: one controlled transaction, exactly two isolated executions, byte equality required, exactly one artifact admitted and persisted.

## Execution boundary

- fixed internal Python worker only; no caller-supplied callable, module path, executable path, shell or command;
- fixed UTF-8/LF output and minimal environment contract (`TZ=UTC`, `LC_ALL=C`, `LANG=C`, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONHASHSEED=0`, `PYTHONUTF8=1`);
- fixed interpreter controls (`-B -s -S -X utf8`) whose effective flags and exact child environment are verified before either execution's bytes are accepted;
- independent temporary child-process execution directories; parent CWD, environment and signal state are not mutated;
- regular-file output only; no symlink, traversal, device, socket or auxiliary renderer files;
- exactly one declared artifact and maximum bytes enforced;
- no network/database/external service or dependency install;
- no retry or alternate renderer;
- any execution exception, bounded timeout, nonzero/partial result, nondeterminism or inventory violation blocks the transaction.

This is a controlled fixed-renderer boundary, not a hostile-code sandbox. It detects undeclared relative filesystem output in each execution directory and prohibits renderer network/database/external-service behavior by fixed implementation identity and review; it does not claim kernel-level confinement of arbitrary code. Invocation authorization creation, ledger retention and output-parent integrity remain trusted-process/local-writer assumptions. Hashes and admission commitments prove consistency and detect tampering; they are not human authentication, digital signatures, external sandbox attestation or WORM storage.

## Success evidence

Success persists exactly:

1. `publication.html` — exact captured bytes;
2. `invocation-evidence.json` — canonical nine-record BCRP closure containing one `GeneratedArtifactAuditRecord` with the required specialized invocation extension.

The extension cross-binds all authoritative inputs, the projection, both execution digests/lengths, admitted output inventory, artifact digest/length/media type and successful controlled-invocation outcome. It declares:

- artifact existence: verified;
- audit links: verified;
- semantic conformance: unassessed;
- Manifest authority: absent;
- distribution authority: absent;
- successful publication: not asserted.

Both staged regular files are independently reread and fully verified before publication. The populated staging-directory inode and the original authorized output-directory inode are captured. Linux `renameat2(RENAME_EXCHANGE)` is the single commit point; immediately after it, both resulting names are reopened relative to the pinned parent descriptor and must have the expected inode identities. The complete pair therefore becomes visible atomically. Detached immutable verified output must not expose mutable authority.

## Failure semantics

All detected problems are retained as deterministic findings. Any detected pre-commit failure returns no verified artifact, no bundle, no persisted success evidence and no partial-success status; staging is discarded and the authorized output directory remains without usable artifact/evidence files. Any detected post-exchange identity failure is rolled back only after both directory identities are reverified.

The atomic exchange is the transaction commit, not the subsequent Python return. A process or host failure before the exchange leaves no publication pair at the authorized path (though hidden staging residue may require operational cleanup). A failure after the exchange may lose the in-process return but leaves the already verified, complete pair committed; independent persisted verification determines its validity. No crash state exposes only one of the two files at the authorized path.

## Verification boundary

Persisted verification requires exactly nine BCRP records: TASK-050 six-record Release closure, TASK-051 capability and Plan, and one artifact audit. It reopens the exact authorized filenames without following the final directory or file symlink, reruns upstream verifiers, reproduces the projection and checks canonical extension shape, every cross-binding, artifact bytes/digest/length/media type and evidence bytes. It never creates or accepts conformance or Manifest records.
