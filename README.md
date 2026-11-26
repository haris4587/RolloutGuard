# RolloutGuard

A standalone GenLayer Intelligent Contract for assessing staged feature releases against immutable rollout policies. It records assessments; it never changes feature flags, controls deployments, or executes rollbacks.

**Deployed:** [Studionet contract](https://explorer-studio.genlayer.com/address/0xE7c1189ad8d66463767AA08098c028FC634E06B4) · **43 tests passed** · [Live receipts and validation](EVIDENCE.md)

## What it verifies

Teams lock a feature, environment, accountable accounts, ordered stages, exposure caps, minimum dwell times, minimum request counts, error-rate limits, p95 latency limits, rollback deadline, and semantic requirements. The operator opens a release against a full Git commit SHA, submits a bounded evidence bundle, and a precommitted attestor signs its exact SHA-256 through an on-chain transaction.

Deterministic code checks exposure, chronology, stage order, dwell time, integer error rates, rollback timing, zero exposure after rollback, and prohibition of promotion after a trigger. Independent leader and validator LLM executions check cohort meaning, denominator scope, monitoring coverage, incidents, and contradictions against the locked requirements. Validators independently reproduce status fields and perform a separate full-context grounding audit; matching quotations alone is insufficient.

## Outcomes

| Outcome | Conditions |
| --- | --- |
| COMPLIANT | Attested, complete coverage for every stage, sufficient samples, no deterministic violation, every semantic finding SUPPORTED, no rollback trigger |
| PARTIAL | Same evidentiary standard, but only an ordered prefix completed or a trigger ended the release with timely zero-exposure rollback |
| VIOLATION | Attested evidence establishes a hard violation or a semantic contradiction; missing coverage cannot erase a known violation |
| INCONCLUSIVE | No attestation, empty evidence, unknown semantic findings, insufficient sample, incomplete coverage, or a pending challenge to a non-violation |

A performance threshold breach invokes the locked rollback obligation. A timely rollback may produce PARTIAL; it cannot erase an exposure or dwell violation. Equality with a cap is allowed. Error rates use exact cross-products, without floating-point rounding.

## Lifecycle

1. `lock_policy(policy_json)` — operator only; content-addressed and immutable.
2. `open_release(release_id, policy_hash, release_commit)` — operator only, unique ID, full lowercase Git SHA. Open before the first observed stage.
3. `submit_evidence(release_id, bundle_json, sha256, byte_length)` — operator only, once; exact UTF-8 hash and length checked. Every stage must fall between opening and submission.
4. `attest_evidence(release_id, sha256)` — designated attestor only, once, before assessment; binds the exact submitted bytes.
5. `assess(release_id)` — operator or reviewer; deterministic checks plus real GenLayer nondeterministic consensus where needed.
6. `challenge(release_id, reason)` — designated reviewer, once after round 1; preserves receipts and suspends positive outcomes.
7. `assess(release_id)` — at most one re-assessment of the same immutable evidence, incorporating the challenge as an allegation.

Views: `get_policy`, `get_release`, `get_receipt`, `effective_result`, `get_event`, `get_status`. Always consult `effective_result` before consuming a receipt: challenges do not rewrite historical receipts.

## Run locally

Python 3.12 recommended:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -q
genvm-lint check contracts/rollout_guard.py
genvm-lint schema contracts/rollout_guard.py -o evidence/schema.json
```

Tests use the actual pinned GenLayer Python SDK through `genlayer-test` direct mode, including serialization and explicit independent-validator execution. LLM outputs are mocked in local tests; those tests do not establish real network consensus. Live verification is documented separately in [EVIDENCE.md](EVIDENCE.md).

```sh
npm ci
npm run schema
```

The schema command is read-only and asks Studionet to validate the contract ABI. Deployment instructions and status are in [DEPLOYMENT.md](DEPLOYMENT.md).

## Evidence and trust

Evidence is inline, immutable and hash-bound; the contract performs no arbitrary URL fetches. This avoids SSRF, redirects, mutable URLs and hidden credential handling. The release SHA is an asserted provenance anchor, not proof that code ran. The attestor's transaction authenticates its account's endorsement, not the monitoring provider or objective completeness. Use distinct trusted accounts with `separate_duties: true` for organizational separation; fixture accounts intentionally share roles for reproducibility.

The contract cannot discover hidden users, omitted incidents, forged telemetry, or collusion between an operator and attestor. Independent AI reasoning does not create missing facts. All assessments apply only to submitted attested records. Do not publish credentials, personal traffic data, or private production logs on-chain. See [SECURITY.md](SECURITY.md) and [EVIDENCE.md](EVIDENCE.md).

## Design references

Original rollout-specific state and decision logic built with official GenLayer primitives:

- [Equivalence Principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- [Direct and integration testing](https://docs.genlayer.com/developers/intelligent-contracts/testing)
- [Networks](https://docs.genlayer.com/developers/networks)
- [Deployment](https://docs.genlayer.com/developers/intelligent-contracts/deploying)

MIT licensed. [Submission text](SUBMISSION.md).
