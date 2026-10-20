(function(r,f){if(typeof module==='object'&&module.exports)module.exports=f(require('./vendor/map-runtime.js'));else r.VialogueNavigation=f(r.VialogueMapRuntime);})(globalThis,R=>{
 'use strict';
 function createNavigation(bundle){
  const world=R.createMapRuntime(bundle);
  const isValid=p=>Number.isFinite(p?.x)&&Number.isFinite(p?.y)&&R.isValid(world,p.x,p.y);
  return {world,isValid,segmentClear:(a,b)=>R.segmentClear(world,a.x,a.y,b.x,b.y),
   findPath(a,b){if(!isValid(a)||!isValid(b))return null;const result=R.findPath(world,a.x,a.y,b.x,b.y);return result;},
   restore:p=>isValid(p)?{x:p.x,y:p.y}:{x:640,y:610}};
 }
 return {createNavigation};
});
