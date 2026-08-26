#!/usr/bin/env python3
"""Freeze the canonical TASK-076 governed contract-byte manifest."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"artifacts/contracts/task076/final-contract-byte-manifest.json"
ROLES={
 "core-object-kind-location-registry.json":("registry","briefforge:core-object-kind-location-registry:1.0.0"),
 "core-object-kind-location-registry.schema.json":("schema","briefforge:core-object-kind-location-registry:1.0.0:schema"),
 "derivation-evidence-envelope.schema.json":("schema","briefforge:paired-semantic-derivation-evidence:2.0.0"),
 "task071-derivation-evidence-envelope.json":("normative-non-authority-fixture","briefforge:paired-semantic-derivation-evidence:2.0.0"),
 "task071-derived-populations.json":("normative-non-authority-population-proof","briefforge:task076-derived-populations-fixture:1.0.0"),
 "capability-v2-record.schema.json":("schema","briefforge:renderer-capability-declaration:2.0.0:record-schema"),
 "capability-v2-record.json":("normative-non-authority-bcrp-record-bytes","briefforge:renderer-capability-declaration:2.0.0"),
 "capability-v2-extension.json":("normative-non-authority-extension-bytes","briefforge:renderer-capability-declaration:2.0.0"),
 "plan-v2-record.schema.json":("schema","briefforge:renderer-compatibility-plan:2.0.0:record-schema"),
 "plan-v2-record.json":("normative-non-authority-bcrp-record-bytes","briefforge:renderer-compatibility-plan:2.0.0"),
 "plan-v2-extension.json":("normative-non-authority-extension-bytes","briefforge:renderer-compatibility-plan:2.0.0"),
 "planning-completeness-evidence.json":("normative-non-authority-coverage-proof","briefforge:planning-completeness-evidence:1.0.0"),
 "valid-fixtures.json":("valid-fixture-index","briefforge:task076-valid-fixture-index:2.0.0"),
 "invalid-fixtures.json":("executable-invalid-fixture-corpus","briefforge:task076-executable-invalid-fixtures:2.0.0"),
 "expected-findings.json":("expected-finding-set","briefforge:task076-expected-findings:1.0.0"),
 "validation-rules.json":("validation-rules","briefforge:task076-contract-validation-rules:2.0.0"),
}
SPECS={
 "artifacts/specifications/briefforge-core-object-kind-location-registry-v1.md":("normative-human-contract","briefforge:core-object-kind-location-registry:1.0.0"),
 "artifacts/specifications/briefforge-paired-derivation-evidence-envelope-v2.md":("normative-human-contract","briefforge:paired-semantic-derivation-evidence:2.0.0"),
 "artifacts/specifications/briefforge-capability-v2-contract.md":("normative-human-contract","briefforge:renderer-capability-declaration:2.0.0"),
 "artifacts/specifications/briefforge-plan-v2-contract.md":("normative-human-contract","briefforge:renderer-compatibility-plan:2.0.0"),
 "tools/build_task076_contracts.py":("deterministic-non-production-fixture-builder","briefforge:task076-contract-builder:1.0.0"),
 "tools/validate_task076_contracts.py":("read-only-contract-validator","briefforge:task076-contract-validator:1.0.0"),
 "tools/freeze_task076_contract_manifest.py":("byte-freeze-tool","briefforge:task076-byte-freeze:1.0.0"),
}

def main():
 entries=[]
 for name,(role,profile) in sorted(ROLES.items()):
  path="artifacts/contracts/task076/"+name; data=(ROOT/path).read_bytes()
  entries.append({"path":path,"length":len(data),"sha256":hashlib.sha256(data).hexdigest(),"profile":profile,"role":role})
 for path,(role,profile) in sorted(SPECS.items()):
  data=(ROOT/path).read_bytes(); entries.append({"path":path,"length":len(data),"sha256":hashlib.sha256(data).hexdigest(),"profile":profile,"role":role})
 entries.sort(key=lambda x:x["path"])
 entries_digest=hashlib.sha256(json.dumps(entries,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
 doc={"contract":"briefforge:task076-final-contract-byte-manifest:1.0.0","task":"TASK-076","freeze_generation":8,"canonicalization":"UTF-8 JSON sort_keys=true separators=(',',':') ensure_ascii=false no trailing newline","governed_entry_count":len(entries),"entries_digest_sha256":entries_digest,"review_invalidation":"any governed byte modification invalidates every prior review; increment freeze_generation, regenerate, and repeat all reviews","entries":entries}
 OUT.write_bytes(json.dumps(doc,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode())
 print(json.dumps({"status":"PASS","path":str(OUT.relative_to(ROOT)),"entries":len(entries),"entries_digest":entries_digest,"manifest_length":OUT.stat().st_size,"manifest_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()},sort_keys=True))
if __name__=="__main__": main()
