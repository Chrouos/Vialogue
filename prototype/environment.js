(function(r,f){if(typeof module==='object'&&module.exports)module.exports=f();else r.VialogueEnvironment=f();})(globalThis,()=>{
 'use strict';
 const stops=[{m:0,c:0x40577b,s:0,b:.43,l:1},{m:300,c:0xb3bfd3,s:.2,b:.76,l:.25},{m:420,c:0xffffff,s:1,b:1,l:0},{m:990,c:0xffd9a6,s:.9,b:1,l:0},{m:1110,c:0xc58eab,s:.15,b:.62,l:.5},{m:1200,c:0x40577b,s:0,b:.43,l:1},{m:1440,c:0x40577b,s:0,b:.43,l:1}];
 function mixColor(a,b,t){return [16,8,0].reduce((v,n)=>v|(Math.round(((a>>n)&255)*(1-t)+((b>>n)&255)*t)<<n),0);}
 function sampleDay(minute){const m=((minute%1440)+1440)%1440;let i=1;while(stops[i].m<m)i++;const a=stops[i-1],b=stops[i],t=(m-a.m)/(b.m-a.m);return {skyTint:mixColor(a.c,b.c,t),sunlight:a.s+(b.s-a.s)*t,moonlight:a.l+(b.l-a.l)*t,lights:a.l+(b.l-a.l)*t,brightness:a.b+(b.b-a.b)*t,localMinute:m};}
 function shoreY(shore,x){let i=1;while(i<shore.length-1&&shore[i][0]<x)i++;const a=shore[i-1],b=shore[i];return a[1]+(b[1]-a[1])*Math.max(0,Math.min(1,(x-a[0])/(b[0]-a[0])));}
 function createEnvironment(config,rng=Math.random){return {config,rng,time:0,nextBirdAt:12000+rng()*13000,birds:[],waves:[],wavePeriods:[7000+rng()*5000,7000+rng()*5000]};}
 function stepEnvironment(s,{dtMs,localMinute,visible=true,reducedMotion=false}){
  if(visible&&!reducedMotion)s.time+=Math.max(0,Math.min(dtMs,30000));
  const t=s.time,shore=s.config.shore||[[0,300],[1280,530]];
  s.waves=s.wavePeriods.map((period,k)=>{const shifted=t+k*period*.47,cycle=Math.floor(shifted/period),phase=(shifted%period)/period;const advance=phase<.35?phase/.35:1-(phase-.35)/.65;const points=[];for(let x=0;x<=1280;x+=20)points.push({x,y:shoreY(shore,x)-20+advance*42+Math.sin(x/110+k*2)*3});return {id:'shore-'+k,cycle,period,phase,advance,points,clipX:[320,1090],bands:[{offset:0,width:advance*5+1},{offset:4,width:1}],alpha:.25+advance*.45};});
  s.birds=s.birds.filter(b=>t-b.born<18000);
  if(visible&&!reducedMotion&&t>=s.nextBirdAt){const count=1+Math.floor(s.rng()*3);for(let i=0;i<count;i++)s.birds.push({id:'bird-'+t+'-'+i,born:t+i*500,y:70+s.rng()*90,phase:s.rng()*1000});s.nextBirdAt=t+35000+s.rng()*55000;}
  return {...sampleDay(localMinute),time:t,waves:s.waves,birds:reducedMotion?[]:s.birds.map(b=>({...b,x:-80+(t-b.born)/18000*1440,frame:Math.floor((t+b.phase)/220)%3})),cloudOffset:(t/1000*2)%1500,reducedMotion};
 }
 return {sampleDay,shoreY,createEnvironment,stepEnvironment};
});
