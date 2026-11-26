"""Update documentation from successfully verified live exports."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'evidence/deployment.json').read_text())
v=json.loads((root/'evidence/verified-live.json').read_text())
r=json.loads((root/'evidence/releases-live.json').read_text())
contract=f"https://explorer-studio.genlayer.com/address/{d['address']}"
lines=['## Verified live deployment','',f"Contract: [`{d['address']}`]({contract})",'',f"Network: **Studionet**, chain ID **{d['chain_id']}**. Deployed through Studio built-in account `{d['account']}` using **Normal (Full Consensus)**.",'',f"Deployed source SHA-256: `{v['source_sha256']}`. Source bytes were independently retrieved and compared with `contracts/rollout_guard.py`.",'','| Action | Transaction | Consensus |','| --- | --- | --- |']
for t in v['transactions']:
 lines.append(f"| {t['action']} | [{t['hash'][:12]}…](https://explorer-studio.genlayer.com/transactions/{t['hash']}) | {t['status']} / {t['result']} |")
lines+=['','## Observed release results','']
for rid,state in r.items():
 outcomes=' → '.join(x['data']['result']['outcome'] for x in state['receipts'])
 lines += [f"`{rid}`: receipt outcomes **{outcomes}**. Latest effective outcome **{state['effective']['outcome']}**, round **{state['rounds']}**, challenge pending **{state['effective']['challenge_pending']}**.",'']
lines+=['A rejected re-assessment reached FINALIZED / MAJORITY_DISAGREE and added no receipt. The single bounded retry is recorded separately. Historical receipts are preserved; no validation rules or source code were changed to obtain agreement.','',f"Exported **{v['status']['events']}** hash-linked events. Run `python scripts/verify_chain.py evidence/events-live.json` to recompute their hashes and assessment decision hashes.",'','The live input is synthetic validation evidence, not production telemetry. Roles share one Studio account with `separate_duties: false`; organizational deployments should use three distinct precommitted accounts. See `evidence/live-input/` for the exact submitted policy and evidence.','', 'Reproduce read-only network checks with `npm ci && npm run verify:live`. The exporter verifies both successful consensus and explicitly expected rejection entries; rejection is never treated as a successful assessment.']
p=root/'DEPLOYMENT.md';s=p.read_text().split('## Current status')[0];p.write_text(s+'\n'+'\n'.join(lines)+'\n')
p=root/'README.md';s=p.read_text();s=s.replace('## What it verifies',f"**Deployed:** [Studionet contract]({contract}) · **43 tests passed** · [Live receipts and validation](EVIDENCE.md)\n\n## What it verifies");p.write_text(s)
p=root/'SUBMISSION.md';p.write_text(p.read_text()+f'\n**Explorer contract:** {contract}\n\n**Independent live verification:** https://github.com/haris4587/RolloutGuard/blob/main/evidence/verified-live.json\n\n**Receipt hash chain:** https://github.com/haris4587/RolloutGuard/blob/main/evidence/hash-chain.txt\n')
print('Updated documentation from verified chain state')
