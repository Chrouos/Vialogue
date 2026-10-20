// Run against an isolated headless Chrome on 127.0.0.1:9347.
const fs=require('node:fs/promises'),path=require('node:path'),{pathToFileURL}=require('node:url');
const root=__dirname,origin='http://127.0.0.1:9347';
async function connect(url){const socket=new WebSocket(url),pending=new Map();let next=0;await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});socket.onmessage=e=>{const v=JSON.parse(e.data);if(pending.has(v.id)){const p=pending.get(v.id);clearTimeout(p.timer);pending.delete(v.id);v.error?p.reject(Error(JSON.stringify(v.error))):p.resolve(v.result);}};socket.onclose=()=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('closed'));}pending.clear();};return {socket,send(method,params={}){return new Promise((resolve,reject)=>{const id=++next,timer=setTimeout(()=>reject(Error('CDP timeout')),15000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));});}};}
async function main(){
  for(let i=0;i<80;i++){try{if((await fetch(origin+'/json/version')).ok)break;}catch{}await new Promise(r=>setTimeout(r,250));}
  const target=await(await fetch(origin+'/json/new?'+encodeURIComponent(pathToFileURL(path.join(root,'preview.html')).href),{method:'PUT'})).json(),cdp=await connect(target.webSocketDebuggerUrl);
  async function evaluate(expression){const r=await cdp.send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
  for(let i=0;i<100;i++){if(await evaluate('typeof images!=="undefined" && images.length===5'))break;await new Promise(r=>setTimeout(r,100));}
  await evaluate('document.getElementById("pause").click()');
  await cdp.send('Emulation.setDeviceMetricsOverride',{width:1280,height:1000,deviceScaleFactor:1,mobile:false});
  const frames=[];
  for(let i=0;i<5;i++){
    await evaluate(`index=${i};draw()`);
    const png=await evaluate('detail.toDataURL("image/png")');
    await fs.writeFile(path.join(root,`browser-frame-${i}.png`),Buffer.from(png.split(',')[1],'base64'));frames.push(i);
  }
  await evaluate('index=0;draw()');
  let shot=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(root,'preview-desktop.png'),Buffer.from(shot.data,'base64'));
  const step=await evaluate('document.getElementById("step").click(); index===1 && paused');if(!step)throw Error('Step failed');
  await cdp.send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
  const overflow=await evaluate('document.documentElement.scrollWidth>innerWidth');if(overflow)throw Error('Mobile overflow');
  shot=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(root,'preview-mobile.png'),Buffer.from(shot.data,'base64'));
  await fs.writeFile(path.join(root,'browser-check.json'),JSON.stringify({frames_captured:frames.length,pause_and_step_passed:step,mobile_overflow:overflow,offline_file:true},null,2));
  cdp.socket.close();const version=await(await fetch(origin+'/json/version')).json(),browser=await connect(version.webSocketDebuggerUrl);await browser.send('Browser.close').catch(()=>{});console.log('Preview: 5 frames captured, pause/step passed, mobile layout passed.');
}
main().catch(e=>{console.error(e);process.exitCode=1;});
