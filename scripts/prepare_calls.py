"""Prepare exact Studio arguments from local records; does not submit transactions."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--policy',required=True);p.add_argument('--bundle',required=True);p.add_argument('--release-id',required=True);p.add_argument('--output',required=True)
a=p.parse_args()
canon=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)
policy=json.loads(Path(a.policy).read_text());raw=Path(a.bundle).read_text();b=json.loads(raw)
h=hashlib.sha256(raw.encode()).hexdigest();pid=hashlib.sha256(canon(policy).encode()).hexdigest()
calls=[{'method':'lock_policy','args':[canon(policy)]},{'method':'open_release','args':[a.release_id,pid,b['release_commit']]},{'method':'submit_evidence','args':[a.release_id,raw,h,len(raw.encode())]},{'method':'attest_evidence','args':[a.release_id,h]},{'method':'assess','args':[a.release_id]},{'method':'challenge','args':[a.release_id,'Recheck cohort scope, monitoring completeness and incident evidence against the locked policy.']},{'method':'assess','args':[a.release_id]}]
Path(a.output).write_text(json.dumps(calls,indent=2)+'\n')
print('Prepared seven calls; open the release before observing stages, then submit and attest evidence.')
