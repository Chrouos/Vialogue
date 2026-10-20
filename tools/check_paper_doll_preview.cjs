// Optional UI QA against an isolated headless Chromium on localhost:9347.
const fs=require('node:fs/promises'),path=require('node:path'),{pathToFileURL}=require('node:url');
const root=path.resolve(__dirname,'..'),assets=path.join(root,'assets/characters/traveler'),qa=path.join(assets,'qa');
const origin='http://127.0.0.1:9347';
async function connect(url){
  const socket=new WebSocket(url),pending=new Map();let next=0;
  await new Promise((resolve,reject)=>{socket.addEventListener('open',resolve,{once:true});socket.addEventListener('error',reject,{once:true});});
  socket.addEventListener('message',event=>{const value=JSON.parse(event.data);if(value.id&&pending.has(value.id)){const item=pending.get(value.id);clearTimeout(item.timer);pending.delete(value.id);value.error?item.reject(new Error(JSON.stringify(value.error))):item.resolve(value.result);}});
  socket.addEventListener('close',()=>{for(const item of pending.values()){clearTimeout(item.timer);item.reject(new Error('CDP connection closed'));}pending.clear();});
  return {socket,send(method,params={}){return new Promise((resolve,reject)=>{const id=++next;const timer=setTimeout(()=>{pending.delete(id);reject(new Error('CDP timeout: '+method));},15000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));});}};
}
async function main(){
  await fs.mkdir(path.join(qa,'ui-frames'),{recursive:true});
  let ready=false;
  for(let attempt=0;attempt<80;attempt++){
    try{const response=await fetch(origin+'/json/version');if(response.ok){ready=true;break;}}catch{}
    await new Promise(resolve=>setTimeout(resolve,250));
  }
  if(!ready)throw new Error('Headless browser did not start within20seconds');
  const url=pathToFileURL(path.join(assets,'preview.html')).href;
  const response=await fetch(origin+'/json/new?'+encodeURIComponent(url),{method:'PUT'});if(!response.ok)throw new Error('Headless browser unavailable');
  const target=await response.json(),cdp=await connect(target.webSocketDebuggerUrl);
  async function evaluate(expression){const r=await cdp.send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
  for(let i=0;i<40;i++){if(await evaluate('document.readyState==="complete" && typeof draw==="function"'))break;await new Promise(resolve=>setTimeout(resolve,100));}
  await cdp.send('Emulation.setDeviceMetricsOverride',{width:1100,height:800,deviceScaleFactor:1,mobile:false});
  const errors=await evaluate('(async()=>{await draw();return document.getElementById("error").textContent;})()');if(errors)throw new Error(errors);
  const screenshot=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(qa,'preview-desktop.png'),Buffer.from(screenshot.data,'base64'));
  let count=0;
  const catalog=JSON.parse(await fs.readFile(path.join(assets,'catalog.json'),'utf8'));
  const heads=catalog.slots.find(s=>s.id==='head').variants,outfits=catalog.slots.find(s=>s.id==='outfit').variants;
  for(const head of heads)for(const item of outfits){
    const hair=head.id,outfit=item.id;
    const data=await evaluate(`(async()=>{const h=document.getElementById('slot-head'),o=document.getElementById('slot-outfit');h.value=${JSON.stringify(hair)};o.value=${JSON.stringify(outfit)};h.dispatchEvent(new Event('change'));o.dispatchEvent(new Event('change'));await draw();return canvas.toDataURL('image/png');})()`);
    await fs.writeFile(path.join(qa,'ui-frames',`${hair}-${outfit}.png`),Buffer.from(data.split(',')[1],'base64'));count++;
  }
  const axisChecks=await evaluate(`(async()=>{let count=0;const head=slots.find(s=>s.id==='head');for(const variant of head.variants){if(!variant.selection)continue;for(const axis of head.selectors){const input=document.getElementById('axis-head-'+axis.key);input.value=variant.selection[axis.key];input.dispatchEvent(new Event('change'));}await draw();if(selection.get('head')!==variant.id)throw new Error('Independent selectors mismatch: '+variant.id);if(document.getElementById('error').textContent)throw new Error(document.getElementById('error').textContent);count++;}return count;})()`);
  await cdp.send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const mobile=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(qa,'preview-mobile.png'),Buffer.from(mobile.data,'base64'));
  const overflow=await evaluate('document.documentElement.scrollWidth > window.innerWidth');if(overflow)throw new Error('Mobile layout overflows horizontally');
  await fs.writeFile(path.join(qa,'browser-check.json'),JSON.stringify({browser:'isolated headless Chrome',offline_file_preview:true,dropdown_combinations:count,independent_style_color_selections:axisChecks,mobile_horizontal_overflow:false},null,2));
  console.log('Browser dropdowns rendered all '+count+' combinations; no mobile horizontal overflow.');
  cdp.socket.close();
  const version=await (await fetch(origin+'/json/version')).json(),browser=await connect(version.webSocketDebuggerUrl);
  await browser.send('Browser.close').catch(()=>{});
}
main().catch(error=>{console.error(error);process.exit(1);});
