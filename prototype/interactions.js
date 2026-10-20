(function(r,f){if(typeof module==='object'&&module.exports)module.exports=f();else r.VialogueInteractions=f();})(globalThis,()=>{
 'use strict';
 const kinds=['wave','happy','surprise','company'];
 function inside(p,poly){let yes=false;for(let i=0,j=poly.length-1;i<poly.length;j=i++){const a=poly[i],b=poly[j];if((a[1]>p.y)!==(b[1]>p.y)&&p.x<(b[0]-a[0])*(p.y-a[1])/(b[1]-a[1])+a[0])yes=!yes;}return yes;}
 function createInteractions(config={},rng=Math.random){return {config,rng,mode:'explore',emotes:[],pendingReplies:[],lastEmotes:{},strokes:[],activeStrokeId:null,waitingBeforeDraw:null,nextSampleAt:20000+rng()*30000,sequence:0};}
 function emitEmote(s,{actorId,kind,nowMs,source,actors=[],player}){
  if(!kinds.includes(kind))return false;const cooldown=source==='player'?3000:20000;if(nowMs-(s.lastEmotes[actorId]??-Infinity)<cooldown)return false;
  s.lastEmotes[actorId]=nowMs;s.emotes=s.emotes.filter(e=>e.actorId!==actorId);s.emotes.push({actorId,kind,startedAt:nowMs,source});
  if(source==='player'&&player&&s.rng()<.5){const near=actors.filter(a=>Math.hypot(a.x-player.x,a.y-player.y)<=220&&nowMs-(s.lastEmotes[a.id]??-Infinity)>=20000);if(near.length)s.pendingReplies.push({actorId:near[Math.floor(s.rng()*near.length)].id,kind,at:nowMs+1500+s.rng()*2500});}
  return true;
 }
 function beginDrawing(s,{player,incoming}){if(incoming||s.mode==='draw')return false;s.mode='draw';s.waitingBeforeDraw=!!player.waiting;return true;}
 function endDrawing(s){if(s.mode!=='draw')return null;endStroke(s);s.mode='explore';const restoreWaiting=s.waitingBeforeDraw;s.waitingBeforeDraw=null;return {restoreWaiting};}
 function allowed(point,player,geometry){return Number.isFinite(point?.x)&&Number.isFinite(point?.y)&&Math.hypot(point.x-player.x,point.y-player.y)<=120&&(geometry.drawRegions||[]).some(p=>inside(point,p));}
 function wet(point,geometry){return (geometry.wetRegions||[]).some(p=>inside(point,p));}
 function beginStroke(s,{point,player,geometry,nowMs}){s.lastNow=nowMs;if(s.mode!=='draw'||!allowed(point,player,geometry))return null;endStroke(s);if(s.strokes.filter(v=>v.forceFadeAt===undefined).length>=24){const old=s.strokes.find(v=>v.forceFadeAt===undefined);old.forceFadeAt=nowMs;}const id='stroke-'+s.sequence++;s.strokes.push({id,createdAt:nowMs,segments:[],last:{...point},geometry,pointCount:1});s.activeStrokeId=id;return id;}
 function simplifySegments(line,player,geometry){const out=[];for(let i=0;i<line.segments.length;i++){const a=line.segments[i],b=line.segments[i+1];let merge=!!b&&a.points[1].x===b.points[0].x&&a.points[1].y===b.points[0].y&&a.wet===b.wet&&a.strength===b.strength&&a.waveHits.join('|')===b.waveHits.join('|');if(merge){const p=a.points[0],q=b.points[1],d=Math.hypot(q.x-p.x,q.y-p.y);merge=d<=8;for(let k=0;merge&&k<=Math.ceil(d/2);k++){const t=k/Math.max(1,Math.ceil(d/2));merge=allowed({x:p.x+(q.x-p.x)*t,y:p.y+(q.y-p.y)*t},player,geometry);}}if(merge){out.push({...a,points:[a.points[0],b.points[1]]});i++;}else out.push(a);}line.segments=out;}
 function appendStroke(s,{point,player,geometry}){let line=s.strokes.find(v=>v.id===s.activeStrokeId);if(!line)return;if(!allowed(point,player,geometry)){line.last=null;return;}if(!line.last){line.last={...point};return;}if(Math.hypot(point.x-line.last.x,point.y-line.last.y)<2)return;
  const origin={...line.last},length=Math.hypot(point.x-origin.x,point.y-origin.y),steps=Math.min(40,Math.ceil(length/3));let previous=origin;
  for(let i=1;i<=steps;i++){const next={x:origin.x+(point.x-origin.x)*i/steps,y:origin.y+(point.y-origin.y)*i/steps},mid={x:(previous.x+next.x)/2,y:(previous.y+next.y)/2};if(allowed(mid,player,geometry)){
   if(line.segments.length>=255){simplifySegments(line,player,geometry);if(line.segments.length>=255){beginStroke(s,{point:previous,player,geometry,nowMs:s.lastNow??line.createdAt});line=s.strokes.at(-1);}}
   line.segments.push({points:[previous,next],strength:1,waveHits:[],wet:wet(mid,geometry)});
  }previous=next;}line.last={...point};line.pointCount=line.segments.length+1;
 }
 function endStroke(s){const line=s.strokes.find(v=>v.id===s.activeStrokeId);if(line)line.last=null;s.activeStrokeId=null;}
 function distanceToSegment(p,a,b){const dx=b.x-a.x,dy=b.y-a.y,k=Math.max(0,Math.min(1,((p.x-a.x)*dx+(p.y-a.y)*dy)/(dx*dx+dy*dy||1)));return Math.hypot(p.x-a.x-k*dx,p.y-a.y-k*dy);}
 function covered(segment,wave){const a=segment.points[0],b=segment.points[1],mid={x:(a.x+b.x)/2,y:(a.y+b.y)/2};return (wave.bands||[{offset:0,width:wave.width||2}]).some(band=>wave.points.some((p,i)=>i>0&&(!wave.clipX||(wave.points[i-1].x>=wave.clipX[0]&&wave.points[i-1].x<=wave.clipX[1]))&&distanceToSegment(mid,{x:wave.points[i-1].x,y:wave.points[i-1].y+band.offset},{x:p.x,y:p.y+band.offset})<=band.width/2+1));}
 function stepInteractions(s,{nowMs,environment={waves:[]},actors=[]}){
  s.lastNow=nowMs;s.emotes=s.emotes.filter(e=>nowMs-e.startedAt<3600);const due=s.pendingReplies.filter(e=>e.at<=nowMs);s.pendingReplies=s.pendingReplies.filter(e=>e.at>nowMs);for(const e of due)emitEmote(s,{actorId:e.actorId,kind:e.kind,nowMs,source:'reply'});
  if(nowMs>=s.nextSampleAt&&actors.length){const a=actors[Math.floor(s.rng()*actors.length)];emitEmote(s,{actorId:a.id,kind:kinds[Math.floor(s.rng()*4)],nowMs,source:'sample'});s.nextSampleAt=nowMs+20000+s.rng()*30000;}
  s.strokes=s.strokes.filter(l=>nowMs-l.createdAt<120000&&(l.forceFadeAt===undefined||nowMs-l.forceFadeAt<1000));
  const strokes=[];for(const line of s.strokes){const ageAlpha=Math.min(1,Math.max(0,(120000-(nowMs-line.createdAt))/30000)),forced=line.forceFadeAt===undefined?1:Math.max(0,1-(nowMs-line.forceFadeAt)/1000);const segments=[];for(const seg of line.segments){if(seg.wet)for(const wave of environment.waves||[]){const key=wave.id+':'+wave.cycle;if(!seg.waveHits.includes(key)&&covered(seg,wave)){seg.waveHits.push(key);seg.strength=Math.max(0,seg.strength-.5);}}const alpha=seg.strength*ageAlpha*forced;if(alpha>0)segments.push({...seg,alpha});}if(segments.length)strokes.push({id:line.id,segments});}
  return {emotes:s.emotes,strokes};
 }
 function skipHidden(s,nowMs){s.pendingReplies=[];s.nextSampleAt=nowMs+20000+s.rng()*30000;endStroke(s);}
 return {kinds,inside,createInteractions,emitEmote,beginDrawing,endDrawing,beginStroke,appendStroke,endStroke,stepInteractions,skipHidden};
});
