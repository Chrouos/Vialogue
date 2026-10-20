const {test}=require('node:test');
const assert=require('node:assert/strict');
const M=require('./model.js');
const NOW=1800000000000;
function bottle(count=2,age=2*M.DAY){return {id:'sample-a',createdAt:NOW-age,status:'drifting',sample:true,letters:Array.from({length:count},(_,i)=>({text:'letter '+i,image:null,at:NOW-age+i,author:i+1})),participants:[]};}
test('new bottles enforce 30 minutes across reloads; drafts and continuations remain available',()=>{
 const s=M.createState(NOW);M.sendNew(s,'今天有一件開心的事。',null,NOW);const copy=JSON.parse(JSON.stringify(s));
 assert.throws(()=>M.sendNew(copy,'another',null,NOW+1),/冷卻/);assert.equal(M.cooldownLeft(copy,NOW+M.HALF_HOUR),0);
 M.receive(copy,bottle(),NOW+1);M.openIncoming(copy,NOW+2);M.continueBottle(copy,'也替你開心。',null,NOW+3);assert.equal(copy.bottles.length,2);
});
test('delivery requires seated waiting, no duplicate contributions or read bottles',()=>{
 const s=M.createState(NOW);s.player.mode='moving';assert.equal(M.receive(s,bottle(),NOW),false);
 s.player.mode='sitting';s.player.waiting=false;assert.equal(M.receive(s,bottle(),NOW),false);
 s.player.waiting=true;assert.equal(M.receive(s,bottle(),NOW),true);assert.equal(M.receive(s,bottle(),NOW),false);
 M.openIncoming(s,NOW);M.releaseIncoming(s,NOW);assert.equal(M.receive(s,bottle(),NOW),false);
 const own=M.sendNew(s,'own',null,NOW);assert.equal(M.receive(s,own,NOW),false);
});
test('unopened bottle leaves at three minutes and can be offered again',()=>{
 const s=M.createState(NOW);M.receive(s,bottle(),NOW);M.tick(s,NOW+3*M.MINUTE);
 assert.equal(s.incoming,null);assert.equal(s.player.waiting,true);assert.equal(M.receive(s,bottle(),NOW+3*M.MINUTE),true);
});
test('real activity extends idle lease; reload and passive ticks do not',()=>{
 const s=M.createState(NOW);M.receive(s,bottle(),NOW);M.openIncoming(s,NOW);
 M.touchIncoming(s,NOW+29*M.MINUTE);const reloaded=JSON.parse(JSON.stringify(s));M.tick(reloaded,NOW+31*M.MINUTE);assert.ok(reloaded.incoming);
 M.tick(reloaded,NOW+59*M.MINUTE);assert.equal(reloaded.incoming,null);assert.ok(reloaded.dismissed.includes('sample-a'));
});
test('seventh day at sea returns even a bottle nobody read, with no fake new letters',()=>{
 const s=M.createState(NOW);M.sendNew(s,'只有自己的信也會回來。',null,NOW);M.tick(s,NOW+7*M.DAY);
 assert.equal(s.bottles[0].status,'returned');assert.equal(s.bottles[0].letters.length,1);
});
test('held bottle can cross day seven while active; release then returns the complete contribution',()=>{
 const s=M.createState(NOW);const b=bottle(2,7*M.DAY-5*M.MINUTE);M.receive(s,b,NOW);M.openIncoming(s,NOW);
 M.touchIncoming(s,NOW+6*M.MINUTE);M.tick(s,NOW+6*M.MINUTE);assert.ok(s.incoming);
 M.continueBottle(s,'謝謝這次相遇。',null,NOW+7*M.MINUTE);assert.equal(s.bottles[0].status,'returned');assert.equal(s.bottles[0].letters.length,3);
});
test('fifth letter immediately returns and never becomes eligible again',()=>{
 const s=M.createState(NOW);M.receive(s,bottle(4),NOW);M.openIncoming(s,NOW);M.continueBottle(s,'第五封',null,NOW);
 assert.equal(s.bottles[0].status,'returned');assert.equal(s.bottles[0].letters.length,5);assert.equal(M.receive(s,s.bottles[0],NOW),false);
});
test('expired lease cannot be revived by a late click; draft survives',()=>{
 const s=M.createState(NOW);M.receive(s,bottle(),NOW);M.openIncoming(s,NOW);s.drafts.replies['sample-a']={text:'尚未寫完',image:null};
 assert.equal(M.touchIncoming(s,NOW+M.HALF_HOUR),false);assert.equal(s.incoming,null);assert.equal(s.drafts.replies['sample-a'].text,'尚未寫完');
});
test('invalid text and image data are rejected without consuming cooldown',()=>{
 const s=M.createState(NOW);for(const text of ['', 'a'.repeat(501)])assert.throws(()=>M.sendNew(s,text,null,NOW));
 assert.throws(()=>M.sendNew(s,'test','javascript:alert(1)',NOW));assert.equal(s.sentAt,null);
});
