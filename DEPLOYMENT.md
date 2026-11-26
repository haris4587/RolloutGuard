# Deployment

Target: GenLayer Studionet, chain ID **61999**, RPC `https://studio.genlayer.com/api`, [Studio](https://studio.genlayer.com/contracts), [Explorer](https://explorer-studio.genlayer.com).

## Procedure

1. Import `contracts/rollout_guard.py` into Studio; retain its pinned runner header.
2. Use Studio's built-in account and select **Normal (Full Consensus)**.
3. Deploy with no constructor arguments. Track the same transaction through finalization, checking successful execution and validator agreement.
4. Prepare policy addresses, release commit and exact observation timestamps. Lock the policy and open a unique release before the rollout starts.
5. After stages complete, submit exact hash-bound evidence, attest from the designated account, then assess. Use the precommitted reviewer to challenge and request the second assessment if needed.
6. Export successful transaction receipts, deployed code, all events, release state and effective result. Verify deployed source equals repository bytes and run `scripts/verify_chain.py` over the event export.


## Verified live deployment

Contract: [`0xE7c1189ad8d66463767AA08098c028FC634E06B4`](https://explorer-studio.genlayer.com/address/0xE7c1189ad8d66463767AA08098c028FC634E06B4)

Network: **Studionet**, chain ID **61999**. Deployed through Studio built-in account `0xcD72fA5B6A496d84B4A10bCFF31D3B7c12346a9e` using **Normal (Full Consensus)**.

Deployed source SHA-256: `3798015127bfa9fdd1b66669b135b2d25a80fd1296fb3990627914d6226d1635`. Source bytes were independently retrieved and compared with `contracts/rollout_guard.py`.

| Action | Transaction | Consensus |
| --- | --- | --- |
| deploy | [0x23cc02c983…](https://explorer-studio.genlayer.com/transactions/0x23cc02c983597327ae1dbe292104902017832d9ff2d3677b3fc6ca02faf14307) | FINALIZED / MAJORITY_AGREE |
| lock_policy | [0xf20fc7eacd…](https://explorer-studio.genlayer.com/transactions/0xf20fc7eacd6d31bef7954ec27d0045685afd227b153f087838811c8131f802b1) | FINALIZED / MAJORITY_AGREE |
| open_release | [0xd8e079ce3c…](https://explorer-studio.genlayer.com/transactions/0xd8e079ce3c7abd61239d93a2ef7ba7d18204f17cb90eba6a5ec28e59d15fdeae) | FINALIZED / MAJORITY_AGREE |
| submit_evidence | [0xf435e382cc…](https://explorer-studio.genlayer.com/transactions/0xf435e382cc041518b9abf3e052fd0e936e0e6c028c07432b66bc8c9bd5517e04) | FINALIZED / MAJORITY_AGREE |
| attest_evidence | [0x557e4384a4…](https://explorer-studio.genlayer.com/transactions/0x557e4384a499038102e743a581d8880c8db1ff483eec3a9d987b5fa07b556f3d) | FINALIZED / MAJORITY_AGREE |
| assess-1 | [0xd815d3d80a…](https://explorer-studio.genlayer.com/transactions/0xd815d3d80a2b7e3fe012d69feb6f3c239c2f256a2ffbe7ec5d07cba60eed954e) | FINALIZED / MAJORITY_AGREE |
| challenge | [0x75a1d8cea2…](https://explorer-studio.genlayer.com/transactions/0x75a1d8cea27b15d10bccb37527fa0a6869485e1652bbcd545cf78bad8e73e664) | FINALIZED / MAJORITY_AGREE |
| assess-2-rejected | [0x40f3938d96…](https://explorer-studio.genlayer.com/transactions/0x40f3938d96c2bef2551b186a0dc8db33157e772bdccda531be4df006ac8c2481) | FINALIZED / MAJORITY_DISAGREE |
| assess-2-retry | [0x992d6c8d06…](https://explorer-studio.genlayer.com/transactions/0x992d6c8d06c2df7e42eb8af952380798fc0e57ff68c648ab4d1504eeaf872080) | FINALIZED / MAJORITY_AGREE |

## Observed release results

`rolloutguard-release-1`: receipt outcomes **COMPLIANT → COMPLIANT**. Latest effective outcome **COMPLIANT**, round **2**, challenge pending **False**.

A rejected re-assessment reached FINALIZED / MAJORITY_DISAGREE and added no receipt. The single bounded retry is recorded separately. Historical receipts are preserved; no validation rules or source code were changed to obtain agreement.

Exported **7** hash-linked events. Run `python scripts/verify_chain.py evidence/events-live.json` to recompute their hashes and assessment decision hashes.

The live input is synthetic validation evidence, not production telemetry. Roles share one Studio account with `separate_duties: false`; organizational deployments should use three distinct precommitted accounts. See `evidence/live-input/` for the exact submitted policy and evidence.

Reproduce read-only network checks with `npm ci && npm run verify:live`. The exporter verifies both successful consensus and explicitly expected rejection entries; rejection is never treated as a successful assessment.
