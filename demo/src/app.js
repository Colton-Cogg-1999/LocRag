/* All data is bundled. This explorer never sends source text to a model. */
"use strict";
const data = window.LOCRAG_DATA;
const $ = id => document.getElementById(id);
let selected = 10;
function text(id, value) { $(id).textContent = value; }
function element(tag, content, className) {
  const node = document.createElement(tag); node.textContent = content;
  if (className) node.className = className;
  return node;
}
function showView(name) {
  if (!["workbench", "evidence", "languages"].includes(name)) name = "workbench";
  document.querySelectorAll(".view").forEach(node => { node.hidden = node.id !== name; });
  document.querySelectorAll(".nav").forEach(node => {
    node.classList.toggle("active", node.dataset.view === name);
    if (node.dataset.view === name) node.setAttribute("aria-current", "page");
    else node.removeAttribute("aria-current");
  });
  history.replaceState(null, "", `#${name}`);
}
document.querySelectorAll("[data-view]").forEach(button => button.addEventListener("click", () => {
  showView(button.dataset.view); window.scrollTo({top: 0, behavior: "smooth"});
}));
window.addEventListener("hashchange", () => showView(location.hash.slice(1)));

// Token-level LCS highlights insertions/substitutions, without implying an error.
function highlightChanges(before, after, target) {
  const tokenize = s => s.match(/\s+|[^\s]+/gu) || [];
  const a = tokenize(before), b = tokenize(after);
  const dp = Array.from({length: a.length + 1}, () => new Uint16Array(b.length + 1));
  for (let i = a.length - 1; i >= 0; i--) for (let j = b.length - 1; j >= 0; j--)
    dp[i][j] = a[i] === b[j] ? 1 + dp[i+1][j+1] : Math.max(dp[i+1][j], dp[i][j+1]);
  const same = new Set(); let i=0, j=0;
  while (i<a.length && j<b.length) {
    if (a[i] === b[j]) { same.add(j); i++; j++; }
    else if (dp[i+1][j] >= dp[i][j+1]) i++; else j++;
  }
  target.replaceChildren();
  b.forEach((word, index) => target.append(!same.has(index) && word.trim() ? element("mark", word) : document.createTextNode(word)));
}

data.curated.forEach((c, i) => {
  const button = element("button", "", "case");
  button.append(element("small", `${String(i+1).padStart(2,"0")} / ${c.tag}`), element("strong", c.label));
  button.dataset.index = c.index;
  button.addEventListener("click", () => { selected = c.index; $("mode").value = c.index === 0 ? "replay" : "recorded"; render(); });
  $("case-list").append(button);
});
function render() {
  const r = data.rows[selected];
  $("mode").querySelector('[value="replay"]').disabled = r.set !== "real";
  if (r.set !== "real") $("mode").value = "recorded";
  const replay = $("mode").value === "replay";
  const declined = replay && r.route === "none";
  const originalExamples = r.set === "risk" ? r.sem_top : r.sem_top.filter(h => h.sim >= 80);
  if (!originalExamples.length) originalExamples.push(r.sem_top[0]);
  const used = declined ? [] : originalExamples;
  const title = data.curated.find(c => c.index === selected)?.label || "Recorded segment";
  text("case-title", title);
  text("source-text", r.src);
  text("source-tag", `${r.set.toUpperCase()} · ENGLISH`);
  text("fuzzy-score", `${r.fuzzy_best.toFixed(1)}%`);
  $("fuzzy-meter").style.width = `${Math.max(0, Math.min(100, r.fuzzy_best))}%`;
  text("fuzzy-source", r.fuzzy_best_src);
  text("fuzzy-caption", r.fuzzy_best >= 75 ? "Meets the configured 75% fuzzy threshold." : "Below the configured 75% fuzzy threshold.");
  const top = r.sem_top[0];
  text("semantic-score", (top.sim / 100).toFixed(3));
  $("semantic-meter").style.width = `${Math.max(0, Math.min(100, top.sim))}%`;
  text("semantic-source", top.src); text("semantic-target", top.tgt);
  text("route-name", declined ? "No memory examples → zero-shot translation" : "Semantic examples → translation model");
  text("route-reason", declined ? "The semantic match is below 0.80. Replay reuses the saved zero-shot output; no new inference or judgment is performed."
    : r.set === "risk" ? "Stress test: semantic examples were forced into the prompt, regardless of the fuzzy route."
    : top.sim < 80 ? "The original experiment supplied its top semantic hit even below the floor. The selective router would decline it."
    : "The semantic candidate passes the 0.80 floor. Its similarity does not verify its meaning.");
  text("record-note", replay ? "POLICY REPLAY · Uses the original recorded route labels (75% / 0.80), not a fresh model run. Only real segments are supported."
    : "RECORDED EXPERIMENT · The original treatment always supplied semantic context, including below-threshold matches. Outputs and judgments are preserved.");
  text("example-count", `${used.length} example${used.length === 1 ? "" : "s"} used`);
  text("zero-translation", r.zero_shot);
  highlightChanges(r.zero_shot, declined ? r.zero_shot : r.rag, $("rag-translation"));
  text("treatment-title", declined ? "Selective fallback" : "With retrieved examples");
  text("change-label", declined ? "SAVED BASELINE REUSED" : "WORDING CHANGES HIGHLIGHTED");
  text("reference-text", r.ref || "No independent reference was supplied for this constructed probe.");
  $("used-examples").replaceChildren(...originalExamples.map(h => {
    const entry = element("div", "", "example-entry");
    entry.append(element("p", h.src), element("p", h.tgt), element("small", `Cosine similarity ${(h.sim/100).toFixed(3)}`)); return entry;
  }));
  const verdict = value => ({rag:"RAG preferred", zero_shot:"Zero-shot preferred", tie:"Tie", error:"Judge error"}[value] || value);
  text("judge-note", `${verdict(r.loc_pairwise)}. ${r.loc_reason}${declined ? " This judgment applies to the original treatment, not the replay above." : ""}`);
  text("generic-note", `${verdict(r.pairwise)}. ${r.judge_reason}`);
  text("provenance", `results/router/rows.jsonl · line ${r.row_number} · ${r.id}`);
  document.querySelectorAll(".case").forEach(node => {
    const active = Number(node.dataset.index) === selected;
    node.classList.toggle("active", active); node.setAttribute("aria-pressed", String(active));
  });
}
$("mode").addEventListener("change", render);
function browse() {
  const query = $("search").value.toLocaleLowerCase();
  const set = $("set-filter").value;
  const matches = data.rows.map((r,i) => [r,i]).filter(([r]) => (set === "all" || r.set === set) && `${r.src} ${r.rag}`.toLocaleLowerCase().includes(query));
  const container = $("browse-results"); container.hidden = false;
  container.replaceChildren(element("p", `${matches.length} matching records${matches.length > 60 ? " · Showing the first 60; refine your search" : ""}`));
  matches.slice(0,60).forEach(([r,i]) => {
    const button = element("button", `${r.row_number}. ${r.src}`);
    button.addEventListener("click", () => { selected=i; $("mode").value="recorded"; render(); container.hidden=true; });
    container.append(button);
  });
}
$("search").addEventListener("input", browse); $("set-filter").addEventListener("change", browse);
$("browse").addEventListener("click", () => { if (!$("browse-results").hidden) $("browse-results").hidden=true; else browse(); });
$("download").addEventListener("click", () => {
  const row=data.rows[selected];
  const blob=new Blob([JSON.stringify({original_record:row,display_mode:$("mode").value,source_sha256:data.evidence.provenance["results/router/rows.jsonl"]},null,2)],{type:"application/json"});
  const url=URL.createObjectURL(blob); const a=element("a", ""); a.href=url; a.download=`locrag-${row.id}.json`; a.click(); setTimeout(()=>URL.revokeObjectURL(url),1000);
});
const c=data.evidence.coverage, s=data.evidence.routed_subset;
[[`${c.reusable_passing_n}/${c.real_n}`,"Passing candidates judged reusable","85/300 passed the similarity floor; 65 of those were judged useful."],
 [`${s.localization.rag} : ${s.localization.zero_shot}`,"Localization preference","Among the 85 passing segments; 22 additional ties."],
 [`${s.accuracy.zero_shot} → ${s.accuracy.rag}`,"Rated accurate","Among the same 85 segments. Accuracy equivalence is unproven."]].forEach(([value,label,note]) => {
  const node=element("article","","metric");node.append(element("strong",value),element("p",label),element("small",note));$("metrics").append(node);
});
for(const [band,row] of Object.entries(data.evidence.mt_by_band)) {
  if(band === "ALL") continue;
  const line=element("div","","chart-row"), bars=element("div","","bars");line.append(element("span",`${band}% fuzzy`));
  [["zero_shot","zero-key"],["fuzzy_cat75","fuzzy-key"],["semantic","semantic-key"]].forEach(([key,color]) => {
    const bar=element("div",row.chrf[key].toFixed(1),`bar ${color}`);bar.style.width=`${row.chrf[key]}%`;bar.setAttribute("aria-label",`${band} ${key}: ${row.chrf[key]} chrF++`);bars.append(bar);
  });line.append(bars);$("band-chart").append(line);
}
data.evidence.limitations.forEach(value => $("limits").append(element("p",value,"limitation")));
if(data.multilingual) {
  const m=data.multilingual, stats=element("div","","data-stats");
  [[m.shared_english_sources.toLocaleString(),"shared English sources"],[m.split_sizes.tm.toLocaleString(),"memory entries / language"],[m.split_sizes.test,"test segments / language"]].forEach(([v,label]) => {
    const n=element("div","");n.append(element("strong",String(v)),element("span",label));stats.append(n);
  });$("language-data").append(stats,element("p",`Data audit complete. Fuzzy prefilter missed the exhaustive best match on ${m.fuzzy_prefilter_audit.missed_best}/${m.fuzzy_prefilter_audit.n} segments, with ${m.fuzzy_prefilter_audit.threshold_crossings} crossings of the 75% threshold. Translation and human-review results are pending.`));
}
render();showView(location.hash.slice(1));
