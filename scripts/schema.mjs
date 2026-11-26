import fs from 'node:fs';
import {createClient} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';
const c=createClient({chain:studionet});
const schema=await c.getContractSchemaForCode(fs.readFileSync('contracts/rollout_guard.py','utf8'));
fs.writeFileSync('evidence/schema-live.json',JSON.stringify(schema,null,2)+'\n');
console.log('Live Studionet schema accepted');
