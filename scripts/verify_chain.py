"""Verify an exported get_event sequence, including result hashes."""
import hashlib,json,sys
canon=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True)
sha=lambda x:hashlib.sha256(canon(x).encode()).hexdigest()
events=json.load(open(sys.argv[1]));head='0'*64;domain=None
for i,e in enumerate(events,1):
 e=dict(e);h=e.pop('event_hash')
 assert e['sequence']==i and e['previous_hash']==head and sha(e)==h,'broken event chain'
 d=(e['version'],e['chain_id'],e['contract'])
 assert domain is None or domain==d,'mixed contract domain'
 domain=d
 if e['kind']=='ASSESS':assert sha(e['data']['result'])==e['data']['decision_hash'],'bad decision hash'
 head=h
print(f'Verified {len(events)} events; head={head}')
