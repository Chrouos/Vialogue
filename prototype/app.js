'use strict';
const M=VialogueCore,$=id=>document.getElementById(id),STORE='vialogue.local-playtest.v1';
const PILOT='../design/characters/paper-doll-pilot/sitting-idle-v1/',ART='../assets/characters/traveler/';
let state,storageError=false,writable=false;
const pendingImages={new:false,reply:false},imageTokens={new:0,reply:0};
try{state=JSON.parse(localStorage.getItem(STORE));if(!state||state.version!==1||!state.player||!Array.isArray(state.bottles)||!state.drafts?.replies||!Array.isArray(state.dismissed)||!Number.isFinite(state.createdAt))throw Error('invalid');}
catch{state=M.createState(Date.now());}
if(!Array.isArray(state.readReturns))state.readReturns=[];
state.player.mode='sitting';state.player.x=Number(state.player.x)||640;state.player.y=Number(state.player.y)||610;
let target=null,view={scale:1,x:0,y:0,w:1280,h:720},loaded=false,reader=null,tab='drifting',toastTimer,saveTimer,walkingDirection=1;
const canvas=$('world'),reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
function now(){return Date.now()+(state.clockOffset||0);}
function toast(message){$('toast').textContent=message;$('toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('visible'),4200);}
function save(){clearTimeout(saveTimer);if(!writable)return;try{localStorage.setItem(STORE,JSON.stringify(state));storageError=false;}catch{if(!storageError)toast('裝置儲存空間不足，這次變更暫存於本頁；關閉後可能遺失。');storageError=true;}}
function saveSoon(){clearTimeout(saveTimer);saveTimer=setTimeout(save,250);}
function remaining(ms){const seconds=Math.max(0,Math.ceil(ms/1000));return Math.floor(seconds/60)+':'+String(seconds%60).padStart(2,'0');}
function age(b){const days=Math.floor(Math.max(0,now()-b.createdAt)/M.DAY);return days===0?'出發還不到一天':'漂流了 '+days+' 天';}
function imageSafe(src){return typeof src==='string'&&/^data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+$/.test(src);}
function modal(id){if(gameUI)gameUI.openPaper(id,document.activeElement);else if(!$(id).open)$(id).showModal();}
document.querySelectorAll('[data-close]').forEach(button=>button.onclick=()=>button.closest('dialog').close());
document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('close',save));
$('about-button').onclick=()=>modal('about-dialog');

const samples=[
 ['sample-tide',2,[
  '今天下班的路上，看到一隻貓躺在便利商店門口。\n\n牠睡得那麼安心，我也忽然覺得，今天可以先這樣就好。',
  '我今天也沒有完成很多事，但有好好吃一頓飯。\n\n讀到你的貓，心裡好像也找到了一小塊可以躺下的地方。']],
 ['sample-light',4,[
  '把一個小小的好消息放進來：陽台的植物，今天長出新葉子了。',
  '我不太會種植物，但很會替別人的新葉子開心。希望它長得慢慢的、好好的。',
  '今天打了一通一直想打的電話。好像也是一種，長出新葉子的感覺。',
  '這幾封信陪我喝完一杯茶。原來不認識的人，也能一起替小事開心。']],
 ['sample-rain',1,[
  '最近有點不知道自己走得對不對。\n\n先把這件事放在海裡，今天就不帶著它睡覺了。',
  '我也還在找路。沒有什麼大道理可以給你，但這一刻，我有讀到。']]
];
function makeSample(entry){const [id,days,texts]=entry;return {id,createdAt:now()-days*M.DAY,status:'drifting',sample:true,participants:[],pickedUp:false,letters:texts.map((text,i)=>({text,image:null,at:now()-days*M.DAY+i*M.MINUTE,author:i+1}))};}
function offerSample(manual=false){
 if(!writable)return false;
 if(!loaded){if(manual)toast('海灘還在載入，稍等一下。');return false;}
 for(const entry of samples){const b=makeSample(entry);if(M.receive(state,b,now())){save();renderUI();if(manual)toast('一個示例瓶靠岸了。點瓶子，看看前面的旅人留下什麼。');chime();return true;}}
 if(manual)toast(state.incoming?'先讀完或放回手上的瓶子吧。':state.player.mode!=='sitting'?'先找個位置坐下。':!state.player.waiting?'先開啟「坐下等信」。':'這次的示例瓶都讀過了；可以從我的旅途查看紀錄。');return false;
}
$('demo-arrival').onclick=()=>offerSample(true);
function advance(ms){state.clockOffset=(state.clockOffset||0)+ms;const events=M.tick(state,now());afterTick(events);save();renderUI();if($('journeys-dialog').open)renderJourneys();toast(ms===7*M.DAY?'試玩時間前進了 7 天。未寫完的草稿仍會留下。':'試玩時間前進了 30 分鐘。');}
$('advance-half-hour').onclick=()=>advance(M.HALF_HOUR);$('advance-week').onclick=()=>advance(7*M.DAY);

function newDraft(){return state.drafts.new;}
function replyDraft(){if(!state.incoming)return null;return state.drafts.replies[state.incoming.bottle.id]??={text:'',image:null};}
function syncDraft(prefix,draft){$(prefix+'-text').value=draft.text;$(prefix+'-count').textContent=[...draft.text].length+' / 500';const valid=imageSafe(draft.image);$(prefix+'-image-preview').hidden=!valid;$(prefix+'-remove-image').hidden=!valid;if(valid)$(prefix+'-image-preview').src=draft.image;else $(prefix+'-image-preview').removeAttribute('src');}
function openNewDraft(){syncDraft('new',newDraft());modal('write-dialog');renderUI();}
$('write-button').onclick=openNewDraft;
for(const prefix of ['new','reply']){
 $(prefix+'-text').addEventListener('input',()=>{if(prefix==='reply'&&!touchReader())return;const draft=prefix==='new'?newDraft():replyDraft();if(!draft)return;draft.text=$(prefix+'-text').value;$(prefix+'-count').textContent=[...draft.text].length+' / 500';saveSoon();});
 $(prefix+'-remove-image').onclick=()=>{if(prefix==='reply'&&!touchReader())return;const draft=prefix==='new'?newDraft():replyDraft();if(!draft)return;imageTokens[prefix]++;pendingImages[prefix]=false;draft.image=null;syncDraft(prefix,draft);$(prefix+'-image').value='';save();renderUI();};
 $(prefix+'-image').onchange=async event=>{
  const file=event.target.files[0];if(!file)return;
  const bottleId=prefix==='reply'?state.incoming?.bottle.id:null,token=++imageTokens[prefix];pendingImages[prefix]=true;renderUI();
  try{
   if(!['image/jpeg','image/png','image/webp'].includes(file.type)||file.size>5*1024*1024)throw Error('試玩版支援 5 MB 以內的 JPG、PNG 或 WebP 圖片。');
   const url=URL.createObjectURL(file);let image;
   try{image=await loadImage(url);}finally{URL.revokeObjectURL(url);}
   if(token!==imageTokens[prefix])return;
   const scale=Math.min(1,1280/Math.max(image.width,image.height)),temp=document.createElement('canvas');temp.width=Math.max(1,Math.round(image.width*scale));temp.height=Math.max(1,Math.round(image.height*scale));
   const c=temp.getContext('2d');c.fillStyle='#fff';c.fillRect(0,0,temp.width,temp.height);c.drawImage(image,0,0,temp.width,temp.height);
   const data=temp.toDataURL('image/jpeg',.78);
   if(data.length>2200000)throw Error('這張圖片仍太大，請換一張較小的照片。');
   if(prefix==='reply'&&(state.incoming?.bottle.id!==bottleId||!touchReader()))throw Error('原瓶已繼續漂，這張照片沒有加入信件。');
   const draft=prefix==='new'?newDraft():replyDraft();draft.image=data;syncDraft(prefix,draft);save();
  }catch(error){if(token===imageTokens[prefix])toast(error.message);}finally{if(token===imageTokens[prefix]){pendingImages[prefix]=false;renderUI();event.target.value='';}}
 };
}
$('new-form').onsubmit=event=>{event.preventDefault();try{if(pendingImages.new)throw Error('照片正在放進信裡，稍等一下再送出。');M.sendNew(state,newDraft().text,newDraft().image,now());save();$('write-dialog').close();scene?.animateBottle({kind:'depart',from:state.player});renderUI();toast('信已放進本機的旅途。希望這句話，也能陪到某個人。');}catch(error){toast(error.message);renderUI();}};

function currentBottle(){return reader?.kind==='incoming'?state.incoming?.bottle:state.bottles.find(b=>b.id===reader?.id);}
function unreadReturns(){return state.bottles.filter(b=>b.status==='returned'&&!state.readReturns?.includes(b.id));}
function openReturned(id){
 const b=state.bottles.find(b=>b.id===id&&b.status==='returned');if(!b)return;
 $('journeys-dialog').close();reader={kind:'returned',id,page:0};$('reply-form').hidden=true;renderReader();modal('read-dialog');
 state.readReturns??=[];if(!state.readReturns.includes(id))state.readReturns.push(id);save();renderUI();
}
$('read-returned').onclick=()=>{const b=unreadReturns().at(-1);if(b)openReturned(b.id);};
function touchReader(){if(reader?.kind!=='incoming')return true;if(!M.touchIncoming(state,now())){handleLostBottle();return false;}saveSoon();return true;}
function openIncoming(){if(!M.openIncoming(state,now())){renderUI();toast('瓶子已經繼續漂了。');return;}reader={kind:'incoming',id:state.incoming.bottle.id,page:0};$('reply-form').hidden=true;renderReader();modal('read-dialog');save();}
$('arrival').onclick=openIncoming;
function renderReader(){
 const b=currentBottle();if(!b)return;
 reader.page=Math.max(0,Math.min(reader.page,b.letters.length-1));const l=b.letters[reader.page],returned=reader.kind==='returned';
 $('letter-journey').textContent=(b.sample?'示例旅途 · ':'')+age(b)+' · '+b.letters.length+' 封信';
 $('letter-title').textContent=returned?'這段旅途，帶著所有心情回來了。':'有人把這段心情，交給了海。';
 $('letter-author').textContent='第'+['一','二','三','四','五'][reader.page]+'位旅人';$('letter-text').textContent=l.text;
 $('letter-page').textContent=(reader.page+1)+' / '+b.letters.length;$('previous-letter').disabled=reader.page===0;$('next-letter').disabled=reader.page===b.letters.length-1;
 const hasImage=imageSafe(l.image);$('letter-image-button').hidden=!hasImage;if(hasImage)$('letter-image').src=l.image;else $('letter-image').removeAttribute('src');
 $('reader-actions').hidden=returned||!$('reply-form').hidden;$('lease-note').hidden=returned;$('favorite-button').hidden=!returned;
 $('favorite-button').textContent=b.favorite?'已收藏這段旅途 ♥':'收藏這段旅途';
}
for(const [id,step] of [['previous-letter',-1],['next-letter',1]])$(id).onclick=()=>{if(touchReader()){reader.page+=step;renderReader();}};
$('letter-image-button').onclick=()=>{if(!touchReader())return;$('full-image').src=$('letter-image').src;modal('image-dialog');};
$('reply-button').onclick=()=>{if(!touchReader())return;$('reply-form').hidden=false;syncDraft('reply',replyDraft());renderReader();$('reply-text').focus();};
$('cancel-reply').onclick=()=>{touchReader();$('reply-form').hidden=true;renderReader();};
$('reply-form').onsubmit=event=>{event.preventDefault();try{if(pendingImages.reply)throw Error('照片正在放進信裡，稍等一下再送出。');const draft=replyDraft();if(!draft)throw Error('瓶子已繼續漂了，草稿仍會留下。');const result=M.continueBottle(state,draft.text,draft.image,now());save();$('read-dialog').close();reader=null;scene?.animateBottle({kind:'depart',from:state.player});renderUI();toast(result.status==='returned'?'這個瓶子完成旅途了。你可以在歸來的瓶子讀完整內容。':'你的信與前面的信，一起繼續漂了。');}catch(error){toast(error.message);if(!state.incoming)handleLostBottle();}};
$('release-button').onclick=()=>{if(!touchReader())return;M.releaseIncoming(state,now());save();$('read-dialog').close();reader=null;scene?.animateBottle({kind:'depart',from:state.player});renderUI();toast('讓這些話，繼續往下一個人那裡去。');};
$('favorite-button').onclick=()=>{const b=currentBottle();if(b){b.favorite=!b.favorite;save();renderReader();}};
function handleLostBottle(){if(reader?.kind==='incoming'){$('image-dialog').close();$('read-dialog').close();reader=null;toast('瓶子已經繼續漂了。未送出的文字留在草稿裡。');}renderUI();}

$('journeys-button').onclick=()=>{renderJourneys();modal('journeys-dialog');};
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{tab=button.dataset.tab;renderJourneys();});
function element(tag,text,className){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;}
function recoverReply(id){
 afterTick(M.tick(state,now()));
 const draft=state.drafts.replies[id];if(!draft){renderJourneys();return;}
 $('journeys-dialog').close();
 if(state.incoming?.bottle.id===id){openIncoming();$('reply-button').click();return;}
 $('recovered-text').value=draft.text;
 const valid=imageSafe(draft.image);$('recovered-image').hidden=!valid;
 if(valid)$('recovered-image').src=draft.image;else $('recovered-image').removeAttribute('src');
 $('copy-recovered').disabled=!draft.text;modal('recover-dialog');$('recovered-text').focus();$('recovered-text').select();
}
$('copy-recovered').onclick=async()=>{
 try{await navigator.clipboard.writeText($('recovered-text').value);toast('草稿文字已複製。');}
 catch{$('recovered-text').focus();$('recovered-text').select();toast('已選取文字，可使用複製功能保存。');}
};
function renderJourneys(){
 document.querySelectorAll('[data-tab]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.tab===tab)));
 const list=$('journey-list');list.replaceChildren();
 if(tab==='drafts'){
  const drafts=[['新瓶子的草稿',state.drafts.new,null],...Object.entries(state.drafts.replies).map(([id,d])=>['接續信的私人草稿',d,id])].filter(([,d])=>d.text||d.image);
  for(const [label,d,id] of drafts){
   const card=element('article',undefined,'journey-card');card.append(element('p',label,'meta'),element('p',d.text||'一張還沒寄出的照片。'));
   if(imageSafe(d.image)){const image=element('img');image.src=d.image;image.alt='草稿圖片';image.className='image-preview';card.append(image);}
   const held=id!==null&&state.incoming?.bottle.id===id;
   if(id!==null)card.append(element('p',held?'瓶子還在這裡，可以繼續添信。':'瓶子已繼續漂，這份草稿無法再補入原瓶；文字與照片仍保留在這裡。','meta'));
   const button=element('button',id===null?'繼續寫新信':held?'繼續添信':'取回草稿');
   button.onclick=()=>{if(id===null){$('journeys-dialog').close();openNewDraft();}else recoverReply(id);};card.append(button);list.append(card);
  }
 }else{
  for(const b of [...state.bottles].filter(b=>b.status===tab).reverse()){
   const card=element('article',undefined,'journey-card');card.append(element('p',(b.sample?'示例旅途 · ':'')+(b.status==='returned'?'已返航':age(b))+(b.favorite?' · 已收藏 ♥':''),'meta'));
   const own=b.letters.find((_,i)=>i===b.letters.length-1);card.append(element('p',(own?.text||'').slice(0,100)));
   if(b.status==='returned'){card.append(element('p','帶回 '+b.letters.length+' 封信。'+(b.letters.length===1?'這次沒有遇到添信的人，原信也好好回來了。':''),'meta'));const button=element('button','打開歸來的瓶子');button.onclick=()=>openReturned(b.id);card.append(button);}
   else card.append(element('p','後面的故事，會等返航後一起讀到。','meta'));list.append(card);
  }
 }
 if(!list.children.length)list.append(element('p',tab==='drifting'?'還沒有出發的瓶子。想說的話，一兩句也很好。':tab==='returned'?'海還在慢慢帶路。歸來的瓶子會留在這裡。':'還沒有沒寫完的話。','empty'));
}

$('wait-button').onclick=()=>{
 if(interactions?.mode==='draw'){finishDrawing();return;}
 if(state.incoming){openIncoming();return;}
 if(state.player.mode==='moving'){target=null;state.player.mode='sitting';state.player.waiting=true;}
 else state.player.waiting=!state.player.waiting;
 save();renderUI();
};
function renderUI(){
 if(gameUI)gameUI.render({drawing:interactions?.mode==='draw',quality});
 const active=state.incoming,cool=M.cooldownLeft(state,now());$('cooldown').textContent=cool>0?'新瓶 '+remaining(cool):'';
 $('new-submit').disabled=cool>0||pendingImages.new;$('reply-form').querySelector('[type=submit]').disabled=pendingImages.reply;
 $('new-send-note').textContent=pendingImages.new?'照片正在放進信裡……':cool>0?'再過 '+remaining(cool)+' 可以寄新瓶子，現在可先寫草稿。':'這封信會先存在本機試玩旅途中。';
 $('wait-button').setAttribute('aria-pressed',String(state.player.waiting&&state.player.mode==='sitting'));
 $('wait-label').textContent=active?'手上有瓶子':state.player.mode==='moving'?'在這裡坐下':state.player.waiting?'等信中':'坐下等信';
 $('presence').textContent=active?(active.openedAt===null?'有一段陌生人的心情，漂到這裡了。':'慢慢讀，想寫的話也可以慢慢寫。'):state.player.mode==='moving'?'找個喜歡的位置，慢慢走過去。':state.player.waiting?'坐在這裡，等一封沒有約定的信。':'先聽聽海，也很好。';
 $('arrival').hidden=!active||active.openedAt!==null;if(active&&active.openedAt===null)$('arrival-time').textContent='還會停留 '+remaining(active.arrivedAt+3*M.MINUTE-now());
 if(active?.openedAt!==null&&active)$('lease-note').textContent=($('reply-form').hidden?'閱讀中':'寫信中')+' · 閒置 '+remaining(active.lastActivity+M.HALF_HOUR-now())+' 後瓶子會繼續漂；操作會補回 30 分鐘。';
 const unread=unreadReturns();$('return-dot').hidden=unread.length===0;$('return-notice').hidden=unread.length===0;
 $('return-message').textContent=unread.length===1?'有一個瓶子返航了，完整的信都在這裡。':'有 '+unread.length+' 個瓶子返航了，故事等你打開。';
}
function afterTick(events){if(events.includes('bottle-left'))handleLostBottle();if(events.includes('returned'))toast('有瓶子帶著原來的心情，回到你的旅途裡了。');if(events.length)save();}
setInterval(()=>{if(!writable)return;afterTick(M.tick(state,now()));renderUI();},1000);
setInterval(()=>{if(!document.hidden&&Math.random()<.22)offerSample(false);},18000);
addEventListener('pagehide',save);document.addEventListener('visibilitychange',()=>{if(!writable)return;afterTick(M.tick(state,now()));renderUI();});

function loadImage(src){return new Promise((resolve,reject)=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>reject(Error('圖片載入失敗，請重新開啟頁面。'));image.src=src;});}
let scene=null,gameUI=null,environment=null,interactions=null,nav=null,lastTime=0,quality='high',sceneMinute=null,sceneSpeed=1,sceneElapsed=0;
const E=globalThis.VialogueEnvironment,I=globalThis.VialogueInteractions,pack=globalThis.VialogueScenePack;
const npcs=pack?.config.actors||[],geometry={drawRegions:pack?.config.drawRegions||[],wetRegions:[]};
const shore=pack?.config.shore||[[0,300],[1280,530]];geometry.wetRegions=[shore.map(([x,y])=>[x,y-12]).concat([...shore].reverse().map(([x,y])=>[x,y+(pack?.config.wetWidth||54)]))];
function finishDrawing(){if(!interactions)return;const result=I.endDrawing(interactions);if(result){state.player.waiting=result.restoreWaiting;save();renderUI();}}
function openEmotes(actorId='me'){if(document.querySelector('dialog[open]'))return;const a=actorId==='me'?state.player:npcs.find(a=>a.id===actorId)||state.player;gameUI.openEmotes({anchor:scene.worldToScreen(a),actorId});}
function gameCommand(command){
 if(command.type==='finish-draw'){finishDrawing();return;}
 if(command.type==='open-emotes'){openEmotes();return;}
 if(command.type==='emote'){const okay=I.emitEmote(interactions,{actorId:'me',kind:command.kind,nowMs:performance.now(),source:'player',actors:npcs,player:state.player});if(!okay)toast('讓這個表情停留一下，再發下一個。');return;}
 if(command.type==='draw'){if(interactions.mode==='draw'){finishDrawing();return;}if(!I.beginDrawing(interactions,{player:state.player,incoming:state.incoming})){toast('先讀讀手上的瓶子，或讓它繼續漂，再來畫沙。');return;}target=null;state.player.mode='sitting';state.player.waiting=false;gameUI.closeEmotes();save();renderUI();return;}
 if(command.type==='quality'){quality=quality==='high'?'low':'high';scene.setQuality(quality);renderUI();}
}
function sceneIntent(intent){
 if(intent.type==='context-lost'){target=null;save();$('scene-error-note').textContent='海灘畫面暫時中斷，草稿已保存。可以等待畫面恢復，或重新開啟。';modal('scene-error-dialog');return;}
 if(intent.type==='context-restored'){$('scene-error-dialog').close();return;}
 if(document.querySelector('dialog[open]'))return;
 if(intent.type==='self-menu'){openEmotes(intent.actorId);return;}
 if(intent.type==='move'){moveTo(intent.point.x,intent.point.y);return;}
 if(intent.type==='draw-start'){I.beginStroke(interactions,{point:intent.point,player:state.player,geometry,nowMs:performance.now()});return;}
 if(intent.type==='draw-move'){I.appendStroke(interactions,{point:intent.point,player:state.player,geometry});return;}
 if(intent.type==='draw-end')I.endStroke(interactions);
}
function loop(t){
 const dt=Math.max(0,Math.min(t-lastTime,50));lastTime=t;
 if(!document.hidden&&loaded){
  if(target){let budget=58*dt/1000;while(target&&budget>0){const p=target.path[0],dx=p.x-state.player.x,dy=p.y-state.player.y,d=Math.hypot(dx,dy);if(d<=budget){state.player.x=p.x;state.player.y=p.y;budget-=d;target.path.shift();if(!target.path.length){target=null;state.player.mode='sitting';save();renderUI();}}else{state.player.x+=dx/d*budget;state.player.y+=dy/d*budget;budget=0;}}}
  sceneElapsed+=dt*sceneSpeed;const date=new Date(),minute=sceneMinute===null?date.getHours()*60+date.getMinutes()+date.getSeconds()/60:(sceneMinute+sceneElapsed/60000)%1440;
  const frame=E.stepEnvironment(environment,{dtMs:dt,localMinute:minute,visible:true,reducedMotion:reduced}),fx=I.stepInteractions(interactions,{nowMs:t,environment:frame,actors:npcs});
  scene.render({player:{...state.player,id:'me',head:'hb',outfit:'tshirt-jeans',walking:!!target,facing:walkingDirection},actors:npcs,incoming:state.incoming,environment:frame,...fx,nowMs:t,drawing:interactions.mode==='draw',blocked:!!document.querySelector('dialog[open]')});view=scene.view;gameUI.avoidPlayer(scene.worldToScreen(state.player));
  const point=scene.worldToScreen({x:state.player.x+40,y:state.player.y-75});$('arrival').style.left=Math.min(view.w-190,Math.max(12,point.x))+'px';$('arrival').style.top=Math.max(100,Math.min(view.h-205,point.y))+'px';
 }
 requestAnimationFrame(loop);
}
function moveTo(x,y){
 if(document.querySelector('dialog[open]')||interactions?.mode==='draw')return;
 if(state.incoming){toast('先讀讀手上的瓶子，或讓它繼續漂吧。');return;}
 const destination={x,y},path=nav.findPath(state.player,destination);if(!path){toast('找一塊能走到的沙地坐下吧。');return;}
 walkingDirection=x<state.player.x?-1:1;target={x,y,path};state.player.mode='moving';gameUI.closeEmotes();renderUI();
}
canvas.addEventListener('keydown',event=>{if(document.querySelector('dialog[open]')||interactions?.mode==='draw')return;if(event.key===' '){event.preventDefault();$('wait-button').click();return;}const delta={ArrowLeft:[-30,0],ArrowRight:[30,0],ArrowUp:[0,-20],ArrowDown:[0,20]}[event.key];if(delta){event.preventDefault();moveTo(state.player.x+delta[0],state.player.y+delta[1]);}});
for(const button of document.querySelectorAll('[data-scene-minute]'))button.onclick=()=>{sceneMinute=Number(button.dataset.sceneMinute);sceneElapsed=0;};
$('scene-live').onclick=()=>{sceneMinute=null;sceneElapsed=0;sceneSpeed=1;};$('scene-fast').onclick=()=>{sceneMinute=sceneMinute??720;sceneSpeed=600;};
$('scene-error-dialog').addEventListener('cancel',event=>event.preventDefault());
$('retry-scene').onclick=()=>{save();location.reload();};
document.addEventListener('visibilitychange',()=>{if(!scene)return;if(document.hidden){I.endStroke(interactions);scene.pause();}else{I.skipHidden(interactions,performance.now());scene.resume();lastTime=performance.now();}});

let audio=null,noise=null,wave=null,soundOn=false;
async function toggleSound(){
 try{
  if(soundOn){await audio.suspend();soundOn=false;}else{
   const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw Error('這個瀏覽器暫時無法播放海浪聲。');
   if(!audio){audio=new Audio();const buffer=audio.createBuffer(1,audio.sampleRate*3,audio.sampleRate),data=buffer.getChannelData(0);for(let i=0;i<data.length;i++)data[i]=Math.random()*2-1;noise=audio.createBufferSource();noise.buffer=buffer;noise.loop=true;const filter=audio.createBiquadFilter();filter.type='lowpass';filter.frequency.value=540;wave=audio.createGain();wave.gain.value=.09;const lfo=audio.createOscillator(),gain=audio.createGain();lfo.frequency.value=.13;gain.gain.value=.04;lfo.connect(gain).connect(wave.gain);noise.connect(filter).connect(wave).connect(audio.destination);noise.start();lfo.start();}
   await audio.resume();soundOn=true;
  }
  $('sound-button').textContent=soundOn?'聲音 開':'聲音 關';$('sound-button').setAttribute('aria-pressed',String(soundOn));
 }catch(error){toast(error.message);}
}
function chime(){if(!soundOn||!audio)return;const oscillator=audio.createOscillator(),gain=audio.createGain(),t=audio.currentTime;oscillator.type='sine';oscillator.frequency.setValueAtTime(660,t);oscillator.frequency.exponentialRampToValueAtTime(880,t+.2);gain.gain.setValueAtTime(0,t);gain.gain.linearRampToValueAtTime(.045,t+.025);gain.gain.exponentialRampToValueAtTime(.001,t+.7);oscillator.connect(gain).connect(audio.destination);oscillator.start(t);oscillator.stop(t+.75);}
$('sound-button').onclick=toggleSound;

async function init(){
 try{
  nav=VialogueNavigation.createNavigation(pack.map);Object.assign(state.player,nav.restore(state.player));environment=E.createEnvironment(pack.config);interactions=I.createInteractions(pack.config);
  gameUI=VialogueGameUI.createGameUI({root:document,onCommand:gameCommand,pack});scene=await VialogueScene.createScene({canvas,pack,onIntent:sceneIntent,reducedMotion:reduced,quality});
  loaded=true;$('loading').hidden=true;afterTick(M.tick(state,now()));renderUI();requestAnimationFrame(loop);
  try{if(!localStorage.getItem(STORE+'.visited')){modal('about-dialog');localStorage.setItem(STORE+'.visited','yes');}}catch{}
 }catch(error){loaded=false;$('loading').hidden=true;$('scene-error-note').textContent='海灘暫時無法載入。'+error.message;modal('scene-error-dialog');}
}
$('session-dialog').addEventListener('cancel',event=>event.preventDefault());
$('retry-session').onclick=()=>location.reload();
async function begin(){
 if(!navigator.locks){$('loading').hidden=true;$('session-note').textContent='這個瀏覽器缺少本機資料保護功能，請使用新版 Chrome 或 Edge 開啟試玩。';modal('session-dialog');return;}
 try{await navigator.locks.request(STORE,{ifAvailable:true},async lock=>{
  if(!lock){$('loading').hidden=true;modal('session-dialog');return;}
  writable=true;await init();await new Promise(()=>{});
 });}catch{writable=false;$('loading').hidden=true;$('session-note').textContent='暫時無法保護這台裝置上的試玩紀錄，請重新開啟再試一次。';modal('session-dialog');}
}
begin();
