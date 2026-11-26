// Read-only exporter. No private keys, signatures or transaction submissions.
import fs from 'node:fs';
import crypto from 'node:crypto';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
import {TransactionHashVariant} from 'genlayer-js/types';
const d=JSON.parse(fs.readFileSync('evidence/deployment.json'));
const c=createClient({chain:studionet});
let last=0;
async function paced(fn){
 for(let attempt=0;attempt<3;attempt++){
  const wait=Math.max(0,last+3500-Date.now());if(wait)await new Promise(r=>setTimeout(r,wait));last=Date.now();
  try{return await fn();}catch(e){if(attempt===2||!String(e).includes('Rate limit'))throw e;last=Date.now()+30000;}
 }
}
const json=x=>JSON.stringify(x,(_,v)=>typeof v==='bigint'?String(v):v,2)+'\n';
const remote=await paced(()=>c.getContractCode(d.address));
const bytes=remote.startsWith('0x')?Buffer.from(remote.slice(2),'hex'):Buffer.from(remote);
if(!bytes.equals(fs.readFileSync('contracts/rollout_guard.py')))throw Error('Deployed source mismatch');
function projection(r){
 const node=n=>({mode:n.mode,vote:n.vote,execution_result:n.execution_result,nondet_disagree:n.nondet_disagree,model:n.node_config?.primary_model?.model,eq_outputs:n.eq_outputs,result:n.result?.payload?.readable??(typeof n.result==='object'?n.result?.status:undefined)});
 return {export_format:'rolloutguard-rpc-projection-v1',omitted:'Repeated binary calldata, state, logs and consensus history; verifier checks original RPC response before export.',hash:r.hash,from_address:r.from_address,to_address:r.to_address,statusName:r.statusName,result_name:r.result_name,txExecutionResultName:r.txExecutionResultName,leader_only:r.leader_only,execution_mode:r.execution_mode,created_at:r.created_at,fees:r.fees,consensus_data:{votes:r.consensus_data?.votes,leader_receipt:r.consensus_data?.leader_receipt?.map(node),validators:r.consensus_data?.validators?.map(node)}};
}
const txs=[];
for(const t of d.transactions){
 const r=await paced(()=>c.getTransaction({hash:t.hash}));
 fs.writeFileSync(`evidence/tx-${t.action}.json`,json(projection(r)));
 const expected=t.expected_consensus??'MAJORITY_AGREE';
 if((r.statusName??r.status_name)!=='FINALIZED'||r.result_name!==expected||r.leader_only!==false||!r.consensus_data?.leader_receipt?.some(x=>x.execution_result==='SUCCESS'))throw Error('Unexpected finality/execution/consensus: '+t.action);
 if(expected!=='MAJORITY_AGREE'&&expected!=='MAJORITY_DISAGREE')throw Error('Unsupported expected result');
 txs.push({action:t.action,hash:t.hash,status:'FINALIZED',result:r.result_name,leader_only:r.leader_only,votes:r.consensus_data.votes});
}
const read=async(fn,args=[])=>JSON.parse(await paced(()=>c.readContract({address:d.address,functionName:fn,args,transactionHashVariant:TransactionHashVariant.LATEST_FINAL})));
const status=await read('get_status');const events=[];
for(let i=1;i<=status.events;i++)events.push(await read('get_event',[i]));
const releases={};
for(const id of d.release_ids){
 const state=await read('get_release',[id]);const receipts=[];
 for(let n=1;n<=state.rounds;n++)receipts.push(await read('get_receipt',[id,n]));
 releases[id]={...state,receipts,effective:await read('effective_result',[id])};
}
const end=await read('get_status');if(end.events!==status.events||end.head!==status.head)throw Error('State changed during export; rerun once writes finalize');
fs.writeFileSync('evidence/events-live.json',json(events));fs.writeFileSync('evidence/releases-live.json',json(releases));
const result={source_matches:true,source_sha256:crypto.createHash('sha256').update(bytes).digest('hex'),status,transactions:txs,outcomes:Object.fromEntries(Object.entries(releases).map(([id,r])=>[id,r.effective]))};
fs.writeFileSync('evidence/verified-live.json',json(result));console.log(json(result));
