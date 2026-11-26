# Deployment

Target: GenLayer Studionet, chain ID **61999**, RPC `https://studio.genlayer.com/api`, [Studio](https://studio.genlayer.com/contracts), [Explorer](https://explorer-studio.genlayer.com).

## Procedure

1. Import `contracts/rollout_guard.py` into Studio; retain its pinned runner header.
2. Use Studio's built-in account and select **Normal (Full Consensus)**.
3. Deploy with no constructor arguments. Track the same transaction through finalization, checking successful execution and validator agreement.
4. Prepare policy addresses, release commit and exact observation timestamps. Lock the policy and open a unique release before the rollout starts.
5. After stages complete, submit exact hash-bound evidence, attest from the designated account, then assess. Use the precommitted reviewer to challenge and request the second assessment if needed.
6. Export successful transaction receipts, deployed code, all events, release state and effective result. Verify deployed source equals repository bytes and run `scripts/verify_chain.py` over the event export.

## Current status

Deployment verification is in progress. Consult the final status recorded below before claiming a live deployment; there is no placeholder contract address.
