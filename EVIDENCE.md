# Evidence format and verification

`fixtures/policy.json` and `fixtures/bundle.json` define the exact schema accepted by the contract. `fixtures/review.mock.json` is a local test response only and is never submitted as an assessment by a caller.

Evidence bundles name the locked feature, environment and release commit. They declare coverage and provide an ordered prefix of stages. Each observed stage includes timestamps, peak exposure in basis points (10000 = 100%), request/error counts, p95 milliseconds, trigger/rollback timestamps (0 = absent), resulting rollback exposure, and separate flag/monitoring/incident narratives. `complete` refers to coverage of the submitted stages, not automatic completion of the full policy.

An operator submits the exact serialized JSON string, its SHA-256 and UTF-8 byte length. `scripts/prepare_calls.py` calculates these values and creates Studio call arguments. It never signs or submits a transaction. The attestor must independently inspect underlying records before calling `attest_evidence`; sample fixtures are synthetic and do not represent an actual production release.

Every event hashes canonical JSON containing version, chain ID, contract, sequence, preceding hash, actor, timestamp, kind, release ID and event data. Assessment data includes policy/release/evidence/attestation/challenge bindings, grounded review, deterministic result and decision hash. `scripts/verify_chain.py` recomputes exported event hashes and decision hashes; altered or reordered records fail verification.

## Validation records

- `evidence/tests.txt`: direct-mode tests with mocked model outputs, including independently invoked validator callbacks.
- `evidence/genvm-check.txt`: GenVM AST checks and SDK semantic validation.
- `evidence/schema.json`: local SDK ABI extraction.
- `evidence/schema-live.json`: ABI accepted by the hosted Studionet RPC, independently of deployment availability.
- Live deployment status, successful transactions and exported receipts are recorded in `DEPLOYMENT.md` when available. An accepted schema is not a deployment.
