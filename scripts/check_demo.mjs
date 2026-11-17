// Dependency-free Chromium DevTools Protocol smoke test. Requires Node with WebSocket.
import {spawn} from "node:child_process";
import {mkdtempSync, writeFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import assert from "node:assert/strict";

const [browser, url = "http://127.0.0.1:8000"] = process.argv.slice(2);
if (!browser) throw new Error("Usage: node scripts/check_demo.mjs /path/to/chromium [url]");
const profile = mkdtempSync(join(tmpdir(), "locrag-browser-"));
const child = spawn(browser, ["--headless", "--no-sandbox", "--disable-gpu", "--remote-debugging-port=0", `--user-data-dir=${profile}`, "about:blank"], {stdio:["ignore","ignore","pipe"]});
let socket;
try {
  const endpoint = await new Promise((resolve,reject) => {
    let logs=""; const timer=setTimeout(()=>reject(new Error("Browser startup timed out")),15000);
    child.stderr.on("data", chunk=>{logs+=chunk; const found=logs.match(/DevTools listening on (ws:\/\/[^\s]+)/);if(found){clearTimeout(timer);resolve(found[1]);}});
    child.on("error",reject); child.on("exit",code=>reject(new Error(`Browser exited ${code}`)));
  });
  const origin = endpoint.replace(/^ws:/,"http:").split("/devtools/")[0];
  const targets=await (await fetch(`${origin}/json/list`)).json();
  socket=new WebSocket(targets.find(t=>t.type==="page").webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{socket.onopen=resolve;socket.onerror=reject;});
  const pending=new Map();let sequence=0;const errors=[];
  socket.onmessage=event=>{const message=JSON.parse(event.data);if(message.method==="Runtime.exceptionThrown")errors.push(message.params.exceptionDetails.text);if(message.id){const p=pending.get(message.id);pending.delete(message.id);if(message.error)p.reject(new Error(message.error.message));else p.resolve(message.result);}};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++sequence;pending.set(id,{resolve,reject});socket.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;};
  await send("Runtime.enable");await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride",{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
  await send("Page.navigate",{url});
  for(let i=0;i<100;i++){if(await evaluate("!!document.getElementById('source-text')?.textContent"))break;await new Promise(r=>setTimeout(r,100));}
  assert.match(await evaluate("document.getElementById('source-text').textContent"),/Winthrop/);
  assert.equal(await evaluate("document.querySelectorAll('.case').length"),5);
  assert.equal(await evaluate("document.querySelectorAll('#rag-translation mark').length > 0"),true);
  writeFileSync("docs/workbench.png",Buffer.from((await send("Page.captureScreenshot",{format:"png"})).data,"base64"));
  await evaluate("document.querySelector('[data-index=\"0\"]').click()");
  assert.match(await evaluate("document.getElementById('route-name').textContent"),/No memory/);
  assert.equal(await evaluate("document.getElementById('rag-translation').textContent === document.getElementById('zero-translation').textContent"),true);
  await evaluate("document.getElementById('mode').value='recorded';document.getElementById('mode').dispatchEvent(new Event('change'))");
  assert.match(await evaluate("document.getElementById('route-reason').textContent"),/below the floor/);
  await evaluate("document.getElementById('search').value='Winthrop';document.getElementById('search').dispatchEvent(new Event('input'))");
  assert.ok(await evaluate("document.querySelectorAll('#browse-results button').length")>0);
  await evaluate("document.querySelector('#browse-results button').click()");
  await evaluate("document.querySelector('[data-view=evidence]').click()");
  assert.equal(await evaluate("document.getElementById('evidence').hidden"),false);
  assert.equal(await evaluate("document.querySelectorAll('#band-chart .chart-row').length"),5);
  await evaluate("document.querySelector('[data-view=languages]').click()");
  assert.match(await evaluate("document.getElementById('language-data').textContent"),/42,461/);
  assert.equal(await evaluate("document.documentElement.scrollWidth <= innerWidth"),true);
  await send("Emulation.setDeviceMetricsOverride",{width:390,height:844,deviceScaleFactor:1,mobile:true});
  await evaluate("document.querySelector('[data-view=workbench]').click();document.querySelector('[data-index=\"197\"]').click()");
  assert.equal(await evaluate("document.documentElement.scrollWidth <= innerWidth"),true);
  assert.match(await evaluate("document.getElementById('judge-note').textContent"),/Zero-shot preferred/);
  writeFileSync("/tmp/locrag-mobile.png",Buffer.from((await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:true})).data,"base64"));
  assert.deepEqual(errors,[]);
  console.log("Browser checks passed: records, differences, fallback replay, search, evidence, languages, responsive layout; no JS exceptions.");
} finally {socket?.close();child.kill();}
