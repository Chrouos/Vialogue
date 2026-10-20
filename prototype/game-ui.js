(function(r){
 'use strict';
 function createGameUI({root,onCommand,pack}){
  const $=id=>root.querySelector('#'+id);let menuActor='me';const triggers=new Map();
  function icon(button,texture,label){const img=document.createElement('img');img.src=pack.textures[texture].src;img.alt='';img.className='tool-art';button.prepend(img);button.setAttribute('aria-label',label);button.title=label;const old=button.querySelector('.nav-icon');if(old)old.remove();}
  for(const [id,tex,label] of [['write-button','letter','寫信'],['wait-button','bottle','等信'],['journeys-button','journal','信冊'],['emote-button','happy','表情'],['draw-button','pencil','畫沙']])icon($(id),tex,label);
  const arrival=$('arrival'),svg=arrival.querySelector('svg');if(svg)svg.remove();const bottle=document.createElement('img');bottle.src=pack.textures.bottle.src;bottle.alt='';arrival.prepend(bottle);
  const choices=[['wave','揮手'],['happy','開心'],['surprise','驚訝'],['company','陪伴']];
  for(const [kind,label]of choices){const b=document.createElement('button'),img=document.createElement('img');b.type='button';b.dataset.emote=kind;b.setAttribute('role','menuitem');b.setAttribute('aria-label',label);img.src=pack.textures[kind].src;img.alt='';const span=document.createElement('span');span.textContent=label;b.append(img,span);b.onclick=()=>{onCommand({type:'emote',kind,targetId:menuActor});closeEmotes();};$('emote-menu').append(b);}
  function closeEmotes(){$('emote-menu').hidden=true;$('emote-button').setAttribute('aria-expanded','false');}
  function openEmotes({anchor,actorId='me'}){menuActor=actorId;const menu=$('emote-menu');menu.hidden=false;menu.style.left=Math.max(12,Math.min(innerWidth-250,anchor.x-120))+'px';menu.style.top=Math.max(85,Math.min(innerHeight-210,anchor.y-210))+'px';$('emote-button').setAttribute('aria-expanded','true');menu.querySelector('button').focus();}
  $('emote-button').onclick=()=>onCommand({type:'open-emotes'});$('draw-button').onclick=()=>onCommand({type:'draw'});$('finish-drawing').onclick=()=>onCommand({type:'finish-draw'});
  $('quality-button').onclick=()=>onCommand({type:'quality'});
  function key(event){if(event.target.closest('textarea,input,dialog'))return;if(event.key.toLowerCase()==='e'){event.preventDefault();onCommand({type:'open-emotes'});}if(event.key==='Escape'){closeEmotes();onCommand({type:'finish-draw'});}if(!$('emote-menu').hidden&&['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)){event.preventDefault();const buttons=[...$('emote-menu').querySelectorAll('button')],i=buttons.indexOf(document.activeElement),step=['ArrowLeft','ArrowUp'].includes(event.key)?-1:1;buttons[(i+step+4)%4].focus();}}
  document.addEventListener('keydown',key);
  for(const d of root.querySelectorAll('dialog')){d.classList.add('game-paper');d.addEventListener('close',()=>{const trigger=triggers.get(d.id);if(trigger?.isConnected)trigger.focus({preventScroll:true});});}
  function openPaper(id,trigger=document.activeElement){onCommand({type:'finish-draw'});closeEmotes();const d=$(id);if(!d.open){triggers.set(id,trigger);d.showModal();d.scrollTop=0;}}
  const intro=$('scene-intro');if(intro)setTimeout(()=>intro.classList.add('intro-finished'),4500);
  return {avoidPlayer(foot){const bottom=root.querySelector('.bottom');bottom.classList.toggle('compact-tools',foot.y>innerHeight-105);bottom.classList.toggle('side-tools',foot.y>innerHeight-60);},openEmotes,closeEmotes,openPaper,closePaper:id=>$(id).close(),openJournal:trigger=>openPaper('journeys-dialog',trigger),render(status){$('world').style.touchAction=status.drawing?'none':'manipulation';$('draw-button').setAttribute('aria-pressed',String(status.drawing));$('draw-hint').hidden=!status.drawing;$('quality-button').textContent=status.quality==='low'?'畫質 省電':'畫質 一般';},destroy(){document.removeEventListener('keydown',key);}};
 }
 r.VialogueGameUI={createGameUI};
})(globalThis);
