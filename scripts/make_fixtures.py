import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def save(n,x): (ROOT/'fixtures'/f'{n}.json').write_text(json.dumps(x,indent=2)+'\n')
account='0xcD72fA5B6A496d84B4A10bCFF31D3B7c12346a9e'
p={'feature':'search-v2','environment':'production','operator':account,'attestor':account,'reviewer':account,'separate_duties':False,'rollback_seconds':120,'semantic_requirements':'Only the opted-in EU cohort may receive search-v2. All requests in that cohort must be monitored. Incident evidence must explicitly describe whether a rollback trigger occurred.','stages':[{'id':'canary','max_exposure_bps':1000,'min_duration_seconds':60,'min_requests':100,'max_error_bps':100,'max_p95_ms':300},{'id':'expand','max_exposure_bps':5000,'min_duration_seconds':60,'min_requests':100,'max_error_bps':100,'max_p95_ms':300}]}
b={'feature':p['feature'],'environment':p['environment'],'release_commit':'a'*40,'complete':True,'coverage_note':'Synthetic demonstration only: complete records for the observed stages, not authenticated production telemetry.','stages':[]}
for i,s in enumerate(p['stages']):
 b['stages'].append({'id':s['id'],'start':1795600000+i*60,'end':1795600060+i*60,'peak_exposure_bps':s['max_exposure_bps'],'requests':1000,'errors':2,'p95_ms':200,'triggered_at':0,'rollback_at':0,'rollback_exposure_bps':0,'flag_evidence':f"search-v2 production commit {'a'*40}: only opted-in EU cohort enabled; peak exposure {s['max_exposure_bps']} basis points of all users.",'monitoring_evidence':'All requests in the opted-in EU cohort were monitored: 1000 requests, 2 errors, p95 200 ms. No monitoring gaps.','incident_evidence':'No rollout incident or rollback trigger occurred during this stage. No rollback was performed.'})
m={s['id']:{'status':'SUPPORTED','flag_quote':s['flag_evidence'],'monitor_quote':s['monitoring_evidence'],'incident_quote':s['incident_evidence']} for s in b['stages']}
for n,x in [('policy',p),('bundle',b),('review.mock',m)]:save(n,x)
