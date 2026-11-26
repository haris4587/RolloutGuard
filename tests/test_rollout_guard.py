import copy
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=str(ROOT/'contracts/rollout_guard.py')
NOW=1795600000
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
sha=lambda x:hashlib.sha256(canon(x).encode()).hexdigest()
def fixture(n):return json.loads((ROOT/'fixtures'/f'{n}.json').read_text())
def warp(vm,t):
 iso=datetime.fromtimestamp(t,timezone.utc).isoformat();vm.warp(iso)
 from genlayer import gl
 gl.message_raw['datetime']=iso
@pytest.fixture
def setup(direct_vm,direct_deploy,direct_owner):
 p=fixture('policy');a='0x'+direct_owner.hex()
 for k in ['operator','attestor','reviewer']:p[k]=a
 direct_vm.warp(datetime.fromtimestamp(NOW,timezone.utc).isoformat());direct_vm.check_pickling=True
 c=direct_deploy(SOURCE,sdk_version='v0.2.16')
 direct_vm.mock_llm('^ROLLOUTGUARD_REVIEW:',canon(fixture('review.mock')))
 direct_vm.mock_llm('^ROLLOUTGUARD_GROUNDING:','{"grounded":true}')
 return direct_vm,c,p,fixture('bundle')
def opened(s,rid='r1'):
 vm,c,p,b=s;c.lock_policy(canon(p));c.open_release(rid,sha(p),'a'*40)
def submitted(s,rid='r1',attest=True):
 vm,c,p,b=s;warp(vm,NOW+200);raw=canon(b);h=hashlib.sha256(raw.encode()).hexdigest()
 c.submit_evidence(rid,raw,h,len(raw.encode()))
 if attest:c.attest_evidence(rid,h)
def assess(s,attest=True):
 opened(s);submitted(s,attest=attest);return json.loads(s[1].assess('r1'))['data']['result']
def remock(vm,review=None,audit=True):
 vm.clear_mocks()
 vm.mock_llm('^ROLLOUTGUARD_REVIEW:',review if isinstance(review,str) else canon(review if review is not None else fixture('review.mock')))
 vm.mock_llm('^ROLLOUTGUARD_GROUNDING:',canon({'grounded':audit}))
def test_full_lifecycle_and_independent_validator(setup):
 assert assess(setup)['outcome']=='COMPLIANT'
 vm,c,*_=setup;assert vm.run_validator() is True
 prev='0'*64
 for i in range(1,json.loads(c.get_status())['events']+1):
  e=json.loads(c.get_event(i));h=e.pop('event_hash');assert sha(e)==h and e['previous_hash']==prev;prev=h
 assert prev==json.loads(c.get_status())['head']
 assert json.loads(c.effective_result('r1'))['outcome']=='COMPLIANT'
@pytest.mark.parametrize('field,value,reason',[('peak_exposure_bps',1001,'exposure'),('end',NOW+59,'dwell'),('errors',11,'rollback'),('p95_ms',301,'rollback'),('triggered_at',NOW+20,'rollback')])
def test_hard_violations(setup,field,value,reason):
 setup[3]['stages'][0][field]=value
 r=assess(setup);assert r['outcome']=='VIOLATION';assert any(reason in x for x in r['violations'])
def test_unattested_cannot_confirm_violation(setup):
 setup[3]['stages'][0]['peak_exposure_bps']=9999
 assert assess(setup,False)['outcome']=='INCONCLUSIVE'
def test_partial_prefix(setup):
 setup[3]['stages']=setup[3]['stages'][:1]
 remock(setup[0],{'canary':fixture('review.mock')['canary']})
 assert assess(setup)['outcome']=='PARTIAL'
def test_unknown_not_partial(setup):
 setup[3]['complete']=False
 assert assess(setup)['outcome']=='INCONCLUSIVE'
def test_small_sample(setup):
 setup[3]['stages'][0].update(requests=99,errors=0)
 assert assess(setup)['outcome']=='INCONCLUSIVE'
def test_equality_threshold_and_exact_error_math(setup):
 setup[3]['stages'][0]['errors']=10
 assert assess(setup)['outcome']=='COMPLIANT'
def test_rollback_does_not_erase_exposure_violation(setup):
 b=setup[3];b['stages']=b['stages'][:1];s=b['stages'][0]
 s.update(peak_exposure_bps=1001,triggered_at=NOW+20,rollback_at=NOW+30,rollback_exposure_bps=0)
 assert assess(setup)['outcome']=='VIOLATION'
def test_promotion_after_trigger(setup):
 setup[3]['stages'][0].update(triggered_at=NOW+20,rollback_at=NOW+30)
 assert 'promotion_after_trigger:canary' in assess(setup)['violations']
@pytest.mark.parametrize('field,value',[('feature','other'),('environment','staging'),('release_commit','b'*40),('complete',1),('stages',[])])
def test_scope_or_empty(setup,field,value):
 setup[3][field]=value
 if field=='stages':assert assess(setup)['outcome']=='INCONCLUSIVE'
 else:
  with pytest.raises(Exception):assess(setup)
@pytest.mark.parametrize('mutation',['skip','future','reverse','boolean','negative','extra','duplicates'])
def test_malformed_evidence(setup,mutation):
 b=setup[3];s=b['stages'][0]
 if mutation=='skip':b['stages'].reverse()
 if mutation=='future':s['end']=NOW+1000
 if mutation=='reverse':s['start']=s['end']+1
 if mutation=='boolean':s['peak_exposure_bps']=True
 if mutation=='negative':s['requests']=-1
 if mutation=='extra':s['injected']=True
 if mutation=='duplicates':b['stages'][1]['id']='canary'
 with pytest.raises(Exception):assess(setup)
def test_wrong_hash_and_length(setup):
 opened(setup);warp(setup[0],NOW+200);raw=canon(setup[3])
 for h,n in [('f'*64,len(raw)),(hashlib.sha256(raw.encode()).hexdigest(),1)]:
  with pytest.raises(Exception):setup[1].submit_evidence('r1',raw,h,n)
def test_sealed_and_round_bounds(setup):
 assess(setup);c=setup[1]
 with pytest.raises(Exception):submitted(setup)
 with pytest.raises(Exception):c.assess('r1')
 first=c.get_receipt('r1',1);c.challenge('r1','Check cohort scope against the full narratives.')
 assert json.loads(c.effective_result('r1'))['outcome']=='INCONCLUSIVE'
 with pytest.raises(Exception):c.challenge('r1','again')
 c.assess('r1');assert c.get_receipt('r1',1)==first
 with pytest.raises(Exception):c.assess('r1')
def test_challenge_preserves_known_violation(setup):
 setup[3]['stages'][0]['peak_exposure_bps']=9999;assess(setup);setup[1].challenge('r1','Disagree')
 assert json.loads(setup[1].effective_result('r1'))['outcome']=='VIOLATION'
def test_invalid_model_is_inconclusive(setup):
 remock(setup[0],'{"bad":true}')
 assert assess(setup)['outcome']=='INCONCLUSIVE'
def test_contradiction(setup):
 m=fixture('review.mock');m['canary']['status']='CONTRADICTED';remock(setup[0],m)
 assert assess(setup)['outcome']=='VIOLATION'
def test_ungrounded_quote(setup):
 m=fixture('review.mock');m['canary']['flag_quote']='invented source content';remock(setup[0],m)
 assert assess(setup)['outcome']=='INCONCLUSIVE'
def test_validator_rejects_disagreement(setup):
 assess(setup);m=fixture('review.mock');m['canary']['status']='CONTRADICTED';remock(setup[0],m)
 assert setup[0].run_validator() is False
def test_validator_rejects_irrelevant_quote_audit(setup):
 assess(setup);remock(setup[0],audit=False)
 assert setup[0].run_validator() is False
def test_distinct_duties(setup):
 setup[2]['separate_duties']=True
 with pytest.raises(Exception):opened(setup)
def test_unauthorized_registration(setup):
 setup[2]['operator']='0x'+'1'*40
 with pytest.raises(Exception):opened(setup)
def test_unauthorized_attestation_and_challenge(setup):
 setup[2]['attestor']='0x'+'1'*40;setup[2]['reviewer']='0x'+'2'*40
 opened(setup);submitted(setup,attest=False)
 with pytest.raises(Exception):setup[1].attest_evidence('r1',hashlib.sha256(canon(setup[3]).encode()).hexdigest())
 setup[1].assess('r1')
 with pytest.raises(Exception):setup[1].challenge('r1','unauthorized')
def test_duplicate_json_key(setup):
 with pytest.raises(Exception):setup[1].lock_policy('{"feature":"a","feature":"b"}')
def test_policy_immutable(setup):
 opened(setup)
 with pytest.raises(Exception):opened(setup)
 assert json.loads(setup[1].get_policy(sha(setup[2])))==setup[2]

def test_timely_rollback_is_partial(setup):
 b=setup[3];b['stages']=b['stages'][:1];b['stages'][0].update(errors=11,triggered_at=NOW+20,rollback_at=NOW+50)
 remock(setup[0],{'canary':fixture('review.mock')['canary']})
 assert assess(setup)['outcome']=='PARTIAL'
@pytest.mark.parametrize('updates',[{'rollback_at':NOW+10},{'rollback_exposure_bps':1},{'rollback_at':0}])
def test_bad_rollback(setup,updates):
 setup[3]['stages'][0].update(triggered_at=NOW+20,rollback_at=NOW+40)
 setup[3]['stages'][0].update(updates)
 assert assess(setup)['outcome']=='VIOLATION'
def test_outsider_cannot_exhaust_assessment(setup):
 opened(setup);submitted(setup)
 setup[0].sender=bytes.fromhex('12'*20)
 with pytest.raises(Exception):setup[1].assess('r1')
