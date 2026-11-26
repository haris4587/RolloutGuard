# Security and limitations

## Account authority

Policies commit operator, attestor and reviewer addresses; no administrator can edit a policy, evidence or receipt. Enabling `separate_duties` requires three distinct nonzero accounts. Only the operator can open and submit. Only the attestor can attest. Only the reviewer can challenge. Only the operator/reviewer can assess, preventing outsiders from consuming the two bounded assessment rounds. Global release IDs are first-come-first-served; use organization-prefixed, unpredictable IDs to avoid collisions.

Attestations bind the contract's submitted bytes and release, with actor, chain ID and contract in the event chain. They are accountable statements, not provider signatures. There is no monitoring-provider API integration, credential custody, external certificate validation, or cryptographic verification of a provider's exports in this version. A compromised attestor can endorse false records. A compromised reviewer can suspend a positive result once. Party identities and separation are policy choices, not a Sybil defense.

## Data validation

Strict key sets, duplicate-key rejection, normalized and raw byte bounds, full commit format, integer-only numeric values, bounded stage count and narrative sizes, chronological checks and scope binding constrain inputs. Floats, booleans in integer positions and out-of-range values are rejected. The source commit is fixed at opening, before any observed stage. Policies are canonical ASCII-escaped JSON, SHA-256 hashed with sorted keys and compact separators. Evidence byte hashes cover original UTF-8 bytes; canonical hashes identify parsed meaning separately.

## Consensus and injection

All evidence, policy prose and challenges are untrusted data in clearly separated prompts. The leader and each validator independently request a structured stage review. Validators check identical stage statuses, valid source quotations, then perform an independent full-context grounding audit. Model errors or invalid reviews become UNKNOWN; validators do not accept a leader execution error. Disagreement can reject a transaction without appending a receipt. A successful UNKNOWN assessment is INCONCLUSIVE; a failed transaction is not an assessment.

Hard violations cannot be overruled by model output. Unattested evidence cannot establish a confirmed violation or compliance. Deterministic violations bypass the LLM path and retain UNKNOWN semantic fields; they do not claim semantic review ran. One initial assessment plus one reviewer-triggered re-assessment bounds model costs. A challenge neither edits evidence nor introduces new privileged facts. Corrected evidence requires a new release and policy opening before its observation period.

## Operational boundaries

Maximum eight stages, 60 KB normalized evidence plus 60 KB raw evidence bound, 10 KB policy, and 2 KB challenge. Storage is append-only and grows with use; there is no pruning. Full evidence is public. Use appropriate fee estimates and wait for successful finalized consensus. Developer networks may reset. This project is not a production security audit, incident-response controller, deployment approval engine, or guarantee of factual telemetry authenticity.

Report reproducible issues through the repository's GitHub issue tracker; do not include secrets.
