/* Local-only integration check against isolated Chrome on 127.0.0.1:9347. */
const fs=require('node:fs/promises'),path=require('node:path'),assert=require('node:assert/strict'),{pathToFileURL}=require('node:url');
const root=__dirname,qa=path.join(root,'qa'),origin='http://127.0.0.1:9347';
let activeConnection;
async function connect(url){
 const socket=new WebSocket(url),pending=new Map(),errors=[];let next=0;
 await new Promise((r,j)=>{socket.onopen=r;socket.onerror=j;});
 socket.onmessage=event=>{const v=JSON.parse(event.data);if(v.method==='Runtime.exceptionThrown')errors.push(v.params.exceptionDetails);if(pending.has(v.id)){const p=pending.get(v.id);clearTimeout(p.timer);pending.delete(v.id);v.error?p.reject(Error(JSON.stringify(v.error))):p.resolve(v.result);}};
 socket.onclose=()=>{for(const p of pending.values()){clearTimeout(p.timer);p.reject(Error('closed'));}pending.clear();};
 return {socket,errors,send(method,params={}){return new Promise((resolve,reject)=>{const id=++next,timer=setTimeout(()=>{pending.delete(id);reject(Error('CDP timeout: '+method));},20000);pending.set(id,{resolve,reject,timer});socket.send(JSON.stringify({id,method,params}));});}};
}
async function main(){
 await fs.mkdir(qa,{recursive:true});
 for(let i=0;i<80;i++){try{if((await fetch(origin+'/json/version')).ok)break;}catch{}await new Promise(r=>setTimeout(r,250));}
 for(const old of await(await fetch(origin+'/json/list')).json())if(old.type==='page'&&old.url.includes('/prototype/index.html'))await fetch(origin+'/json/close/'+old.id);
 const target=await(await fetch(origin+'/json/new?'+encodeURIComponent(pathToFileURL(path.join(root,'index.html')).href),{method:'PUT'})).json(),cdp=await connect(target.webSocketDebuggerUrl);activeConnection=cdp;
 async function evaluate(expression){const r=await cdp.send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
 async function wait(expression){for(let i=0;i<100;i++){if(await evaluate(expression))return;await new Promise(r=>setTimeout(r,70));}throw Error('Timed out: '+expression);}
 async function screenshot(name){const shot=await cdp.send('Page.captureScreenshot',{format:'png'});await fs.writeFile(path.join(qa,name),Buffer.from(shot.data,'base64'));}
 function check(value,message){assert.ok(value,message);checks.push(message);console.log('PASS: '+message);}
 const checks=[];
 await cdp.send('Runtime.enable');await cdp.send('Emulation.setDeviceMetricsOverride',{width:1440,height:960,deviceScaleFactor:1,mobile:false});
 await wait('typeof loaded!=="undefined" && loaded');
 await evaluate('localStorage.clear();state=M.createState(Date.now());target=null;renderUI();document.querySelectorAll("dialog[open]").forEach(d=>d.close())');
 await screenshot('beach-desktop.png');
 const point=await evaluate('({x:720*view.scale+view.x,y:580*view.scale+view.y})');
 await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',x:point.x,y:point.y,button:'left',clickCount:1});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',x:point.x,y:point.y,button:'left',clickCount:1});
 await wait('!target && Math.abs(state.player.x-720)<1');check(await evaluate('state.player.mode==="sitting"'),'click-to-move arrives and sits');
 await evaluate('$("write-button").click();$("new-text").value="今天真的走到海邊了。把這個小小的完成，送給下一個人。";$("new-text").dispatchEvent(new Event("input",{bubbles:true}))');
 const doc=await cdp.send('DOM.getDocument'),input=await cdp.send('DOM.querySelector',{nodeId:doc.root.nodeId,selector:'#new-image'});
 await evaluate('window.__originalLoadImage=loadImage;loadImage=async src=>{const image=await window.__originalLoadImage(src);await new Promise(r=>setTimeout(r,700));return image;}');
 await cdp.send('DOM.setFileInputFiles',{nodeId:input.nodeId,files:[path.join(root,'../design/characters/paper-doll-pilot/sitting-idle-v1/master-review.png')]});
 await wait('pendingImages.new');await evaluate('$("new-form").requestSubmit()');check(await evaluate('state.bottles.length===0 && $("new-submit").disabled'),'sending is blocked while a selected image is processing');
 await wait('!!state.drafts.new.image');await screenshot('writing-desktop.png');
 await evaluate('$("new-form").requestSubmit()');check(await evaluate('state.bottles.length===1 && !!state.bottles[0].letters[0].image && M.cooldownLeft(state,now())>0'),'new letter with image saved and cooldown starts');
 const secondTarget=await(await fetch(origin+'/json/new?'+encodeURIComponent(pathToFileURL(path.join(root,'index.html')).href),{method:'PUT'})).json(),second=await connect(secondTarget.webSocketDebuggerUrl);
 let protectedTab=false;for(let i=0;i<80;i++){const r=await second.send('Runtime.evaluate',{expression:'typeof writable!=="undefined" && !writable && document.getElementById("session-dialog").open',returnByValue:true});if(r.result.value){protectedTab=true;break;}await new Promise(r=>setTimeout(r,70));}
 check(protectedTab,'second tab cannot overwrite the active local journey');await fetch(origin+'/json/close/'+secondTarget.id);second.socket.close();await cdp.send('Page.bringToFront');
 check(await evaluate('JSON.parse(localStorage.getItem(STORE)).bottles.length===1 && M.cooldownLeft(JSON.parse(localStorage.getItem(STORE)),now())>0'),'closing a stale second tab preserves sent letter and cooldown');
 await evaluate('$("write-button").click();$("new-text").value="冷卻時，也可以慢慢寫。";$("new-text").dispatchEvent(new Event("input",{bubbles:true}));save()');
 check(await evaluate('$("new-submit").disabled && state.drafts.new.text.length>0'),'cooldown still permits private drafts');await evaluate('$("write-dialog").close();$("demo-arrival").click();$("arrival").click()');
 check(await evaluate('state.incoming.bottle.letters.length===2 && reader.page===0'),'sample bottle opens at the first accumulated letter');
 await evaluate('$("next-letter").click()');check(await evaluate('reader.page===1 && $("letter-author").textContent.includes("二")'),'letters turn in chronological order');
 await evaluate('$("reply-button").click();$("reply-text").value="我也想在這裡，留一句：今天辛苦了。";$("reply-text").dispatchEvent(new Event("input",{bubbles:true}));save()');
 const heldAt=await evaluate('state.incoming.lastActivity');await cdp.send('Page.reload',{ignoreCache:true});await wait('typeof loaded!=="undefined" && loaded');
 await evaluate('document.querySelectorAll("dialog[open]").forEach(d=>d.close())');
 check(await evaluate(`state.incoming.lastActivity===${heldAt} && state.drafts.replies['sample-tide'].text.length>0 && state.drafts.new.text.length>0 && M.cooldownLeft(state,now())>0`),'reload preserves held deadline, both drafts, and cooldown');
 await evaluate('$("journeys-button").click();document.querySelector("[data-tab=drafts]").click()');
 check(await evaluate('document.querySelectorAll("#journey-list button").length===2'),'both saved drafts offer a recovery action');
 await evaluate('document.querySelector("#journey-list button").click()');
 check(await evaluate('$("write-dialog").open && !$("journeys-dialog").open && $("new-text").value==="冷卻時，也可以慢慢寫。" && $("new-submit").disabled'),'new draft resumes without bypassing cooldown');
 await evaluate('$("write-dialog").close();$("journeys-button").click();document.querySelectorAll("#journey-list button")[1].click()');
 check(await evaluate('$("read-dialog").open && !$("reply-form").hidden && $("reply-text").value==="我也想在這裡，留一句：今天辛苦了。" && state.incoming.bottle.id==="sample-tide"'),'held reply draft resumes in its original bottle');
 await screenshot('reading-desktop.png');
 await evaluate('$("reply-form").requestSubmit()');check(await evaluate('!state.incoming && state.bottles.length===2 && state.bottles[1].letters.length===3 && state.bottles[1].status==="drifting"'),'continuation preserves prior letters and bypasses new-bottle cooldown');
 await evaluate('$("demo-arrival").click();$("arrival").click();$("reply-button").click();$("reply-text").value="第五封：願大家的葉子，都慢慢長出來。";$("reply-text").dispatchEvent(new Event("input",{bubbles:true}));$("reply-form").requestSubmit()');
 check(await evaluate('state.bottles.some(b=>b.id==="sample-light" && b.status==="returned" && b.letters.length===5)'),'fifth letter returns the complete bottle');
 check(await evaluate('!!$("return-notice") && !$("return-notice").hidden'),'fifth letter offers a persistent return reading entry');
 await cdp.send('Page.reload',{ignoreCache:true});await wait('typeof loaded!=="undefined" && loaded');
 check(await evaluate('!$("return-notice").hidden'),'unread return entry survives reload');
 await evaluate('$("read-returned").click()');
 check(await evaluate('$("read-dialog").open && reader.id==="sample-light" && reader.page===0 && $("letter-page").textContent==="1 / 5" && $("return-notice").hidden'),'return entry opens the full journey and acknowledges its notice');
 await evaluate('$("favorite-button").click()');
 check(await evaluate('state.bottles.find(b=>b.id==="sample-light").favorite'),'returned journey can be collected');await screenshot('returned-desktop.png');
 await evaluate('$("read-dialog").close();$("demo-arrival").click()');check(await evaluate('!!state.incoming && state.incoming.openedAt===null'),'another eligible sample can arrive');
 await evaluate('$("advance-half-hour").click()');check(await evaluate('state.incoming===null && state.player.waiting'),'unopened sample leaves after elapsed time and resumes waiting');
 await evaluate('$("demo-arrival").click();$("arrival").click();$("reply-button").click();$("reply-text").value="還沒寫完，也想留下這句話。";$("reply-text").dispatchEvent(new Event("input",{bubbles:true}));replyDraft().image=state.bottles[0].letters[0].image;$("advance-half-hour").click();$("journeys-button").click();document.querySelector("[data-tab=drafts]").click();document.querySelectorAll("#journey-list button")[1].click()');
 check(await evaluate('$("recover-dialog").open && $("recovered-text").value==="還沒寫完，也想留下這句話。" && $("recovered-text").readOnly && !state.incoming && state.drafts.new.text==="冷卻時，也可以慢慢寫。" && state.drafts.replies["sample-rain"].text==="還沒寫完，也想留下這句話。"'),'expired reply text is recoverable without rejoining or overwriting either draft');
 check(await evaluate('!$("recovered-image").hidden && $("recovered-image").src===state.drafts.replies["sample-rain"].image'),'expired reply also retains its attached photo');
 await screenshot('recovered-desktop.png');
 await cdp.send('Browser.grantPermissions',{permissions:['clipboardReadWrite','clipboardSanitizedWrite']});
 await evaluate('$("copy-recovered").click()');await wait('navigator.clipboard.readText().then(text=>text==="還沒寫完，也想留下這句話。")');
 check(await evaluate('navigator.clipboard.readText().then(text=>text==="還沒寫完，也想留下這句話。")'),'recovered text can be copied to the clipboard');
 await evaluate('$("recover-dialog").close()');
 await evaluate('$("advance-week").click()');check(await evaluate('state.bottles.filter(b=>!b.sample).every(b=>b.status==="returned" && b.letters.length===1)'),'unread own bottle returns without invented replies');
 await cdp.send('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await new Promise(r=>setTimeout(r,150));await screenshot('beach-mobile.png');
 check(await evaluate('document.documentElement.scrollWidth<=innerWidth'),'mobile beach fits viewport');
 check(await evaluate('!$("return-notice").hidden && $("return-notice").getBoundingClientRect().right<=innerWidth'),'timed return notice fits mobile viewport');
 check(await evaluate('$("return-notice").getBoundingClientRect().bottom<=scene.worldToScreen(state.player).y-100'),'mobile return notice does not cover the beach introduction');
 await evaluate('$("write-button").click()');await screenshot('writing-mobile.png');
 check(await evaluate('$("write-dialog").scrollWidth<=$("write-dialog").clientWidth+1'),'mobile writing dialog has no horizontal overflow');
 await evaluate('$("write-dialog").close();$("journeys-button").click();document.querySelector("[data-tab=drafts]").click();document.querySelectorAll("#journey-list button")[1].click()');
 check(await evaluate('$("recover-dialog").scrollWidth<=$("recover-dialog").clientWidth+1'),'recovered text and photo fit mobile viewport');await screenshot('recovered-mobile.png');await evaluate('$("recover-dialog").close()');
 await evaluate('$("write-dialog").close()');const soundPoint=await evaluate('(()=>{const r=$("sound-button").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()');
 await cdp.send('Input.dispatchMouseEvent',{type:'mousePressed',...soundPoint,button:'left',clickCount:1});await cdp.send('Input.dispatchMouseEvent',{type:'mouseReleased',...soundPoint,button:'left',clickCount:1});
 await wait('soundOn');check(await evaluate('audio.state==="running"'),'white noise starts only after sound button gesture');await evaluate('$("sound-button").click()');
 assert.deepEqual(cdp.errors,[],'No uncaught browser exceptions');checks.push('no uncaught browser exceptions');
 await fs.writeFile(path.join(qa,'browser-check.json'),JSON.stringify({passed:true,checks,viewport_desktop:[1440,960],viewport_mobile:[390,844],local_file:true},null,2));console.log(JSON.stringify({passed:true,checks:checks.length}));
 cdp.socket.close();const version=await(await fetch(origin+'/json/version')).json(),browser=await connect(version.webSocketDebuggerUrl);await browser.send('Browser.close').catch(()=>{});
}
main().catch(async error=>{console.error(error);process.exitCode=1;activeConnection?.socket.close();try{const version=await(await fetch(origin+'/json/version')).json(),browser=await connect(version.webSocketDebuggerUrl);await browser.send('Browser.close').catch(()=>{});}catch{}});
