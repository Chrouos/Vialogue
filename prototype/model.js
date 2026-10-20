/* Shared local-prototype rules. No browser APIs and no fabricated replies. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.VialogueCore=api;})(globalThis,()=>{
 'use strict';
 const MINUTE=60000,DAY=86400000,HALF_HOUR=30*MINUTE;
 function createState(now){return {version:1,createdAt:now,sentAt:null,clockOffset:0,player:{x:640,y:610,mode:'sitting',waiting:true},incoming:null,bottles:[],dismissed:[],drafts:{new:{text:'',image:null},replies:{}},settings:{sound:false}};}
 function cooldownLeft(s,now){return s.sentAt===null?0:Math.max(0,s.sentAt+HALF_HOUR-now);}
 function validateLetter(text,image){
   if(typeof text!=='string'||!text.trim()||[...text].length>500)throw Error('請寫下 1～500 字，再交給海。');
   if(image!==null&&image!==undefined&&!(typeof image==='string'&&/^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$/.test(image)&&image.length<2400000))throw Error('圖片格式無法保存，請重新選擇。');
 }
 function letter(text,image,at,author){validateLetter(text,image);return {text:text.trim(),image:image||null,at,author};}
 function finish(b,now){b.status='returned';b.returnedAt=now;return b;}
 function addRecord(s,b){const old=s.bottles.findIndex(v=>v.id===b.id);const copy=JSON.parse(JSON.stringify(b));if(old<0)s.bottles.push(copy);else s.bottles[old]=copy;}
 function sendNew(s,text,image,now){
   if(cooldownLeft(s,now)>0)throw Error('新瓶子還在冷卻，內容會先留在草稿。');
   const first=letter(text,image,now,1),b={id:'local-'+now.toString(36)+'-'+Math.random().toString(36).slice(2,8),createdAt:now,status:'drifting',letters:[first],participants:['me'],sample:false,pickedUp:false,favorite:false};
   s.sentAt=now;s.bottles.push(b);s.drafts.new={text:'',image:null};return b;
 }
 function receive(s,b,now){
   tick(s,now);
   if(s.incoming||s.player.mode!=='sitting'||!s.player.waiting||b.status!=='drifting'||now-b.createdAt>=7*DAY||b.letters.length>=5||b.participants.includes('me')||s.dismissed.includes(b.id))return false;
   s.incoming={bottle:JSON.parse(JSON.stringify(b)),arrivedAt:now,openedAt:null,lastActivity:null};s.incoming.bottle.pickedUp=true;s.player.waiting=false;return true;
 }
 function openIncoming(s,now){tick(s,now);if(!s.incoming)return false;s.incoming.openedAt??=now;s.incoming.lastActivity=now;return true;}
 function touchIncoming(s,now){tick(s,now);if(!s.incoming||s.incoming.openedAt===null)return false;s.incoming.lastActivity=now;return true;}
 function releaseIncoming(s,now){
   const active=s.incoming;if(!active)return null;const b=active.bottle;
   if(active.openedAt!==null&&!s.dismissed.includes(b.id))s.dismissed.push(b.id);
   if(b.letters.length>=5||now-b.createdAt>=7*DAY)finish(b,now);
   if(b.participants.includes('me'))addRecord(s,b);
   s.incoming=null;s.player.waiting=s.player.mode==='sitting';return b;
 }
 function continueBottle(s,text,image,now){
   tick(s,now);if(!s.incoming||s.incoming.openedAt===null)throw Error('瓶子已經繼續漂了，未送出的文字仍在草稿。');
   const b=s.incoming.bottle;if(b.participants.includes('me'))throw Error('這趟旅程已經留下過信了。');
   const next=letter(text,image,now,b.letters.length+1);b.letters.push(next);b.participants.push('me');s.incoming.lastActivity=now;
   delete s.drafts.replies[b.id];const result=releaseIncoming(s,now);addRecord(s,result);return result;
 }
 function tick(s,now){
   const events=[];
   if(s.incoming){const a=s.incoming,expired=a.openedAt===null?now-a.arrivedAt>=3*MINUTE:now-a.lastActivity>=HALF_HOUR;
     if(expired){releaseIncoming(s,now);events.push('bottle-left');}}
   for(const b of s.bottles){if(b.status==='drifting'&&(!s.incoming||s.incoming.bottle.id!==b.id)&&(now-b.createdAt>=7*DAY||b.letters.length>=5)){finish(b,now);events.push('returned');}}
   return events;
 }
 return {MINUTE,DAY,HALF_HOUR,createState,cooldownLeft,validateLetter,sendNew,receive,openIncoming,touchIncoming,releaseIncoming,continueBottle,tick};
});
