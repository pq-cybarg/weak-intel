#!/usr/bin/env python3
"""Emit docs/*.html — phosphor-on-void dual-use bubble map."""
from __future__ import annotations

import glob
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav import navbar  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")
REP = os.path.join(ROOT, "report")
os.makedirs(DOCS, exist_ok=True)
os.makedirs(REP, exist_ok=True)

COLORS = {
    "actor": "#b54a3c",
    "malware": "#c17a4a",
    "people": "#d9c48a",
    "crypto": "#6a9bb0",
    "protectors": "#6d9a6f",
    "intel": "#7ea8be",
    "targets": "#e0c07a",
    "blue": "#8fbf9a",
    "quantum": "#c9a0dc",
    "clear": "#a89f8d",
    "capability": "#8a6a4a",
    "other": "#6e6a63",
}

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&family=Syne:wght@700;800&display=swap" rel="stylesheet">'
)

CSS = """
:root{--void:#0b0e14;--ink:#e8e2d4;--dim:#8a8378;--line:#2a241c;--phos:#e0c07a;--copper:#c17a4a;--ice:#6a9bb0;--ember:#b54a3c;--ok:#6d9a6f;}
*{box-sizing:border-box}
html,body{margin:0;background:var(--void);color:var(--ink);font:15px/1.55 'IBM Plex Sans',sans-serif;}
a{color:var(--ice)}
h1,h2,.display{font-family:Syne,sans-serif;letter-spacing:-.02em}
.wrap{max-width:1100px;margin:0 auto;padding:28px 20px 80px}
.kicker{font:600 11px/1 'IBM Plex Mono',monospace;color:var(--phos);text-transform:uppercase;letter-spacing:.16em}
.lede{font-size:1.25rem;color:#d7d0c2;max-width:42rem}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:22px 0}
.rgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(168px,1fr));gap:10px;margin:22px 0}
.rcard{border:1px solid var(--line);padding:12px 14px;background:#12161f}
.rcard b{display:block;font:600 14px/1.3 'IBM Plex Sans',sans-serif;color:var(--phos);letter-spacing:0}
.rcard span{display:block;margin-top:6px;color:var(--dim);font:11px/1.4 'IBM Plex Mono',monospace}
.stat{border:1px solid var(--line);padding:14px 16px;background:#12161f}
.stat b{display:block;font:700 1.6rem/1 Syne,sans-serif;color:var(--phos)}
.stat span{color:var(--dim);font:11px/1.4 'IBM Plex Mono',monospace}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{text-align:left;padding:7px 8px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--phos);font:600 11px/1 'IBM Plex Mono',monospace;text-transform:uppercase;letter-spacing:.08em}
.tag{display:inline-block;padding:1px 7px;border:1px solid var(--line);font:11px 'IBM Plex Mono',monospace;margin-right:4px}
.dual{color:var(--ember)}
.ok{color:var(--ok)}
.foot{margin-top:48px;color:var(--dim);font-size:12px;border-top:1px solid var(--line);padding-top:16px}
.map-body{overflow:hidden;height:100vh;display:flex;flex-direction:column}
.map-body header{flex:0 0 auto}
#stage{flex:1 1 auto;min-height:0;position:relative;overflow:hidden;background:radial-gradient(1200px 600px at 50% 20%, #161b26 0%, #0b0e14 70%)}
#stage svg{display:block;width:100%;height:100%;cursor:grab}
#hud{position:absolute;top:10px;left:12px;z-index:8;max-width:310px;max-height:calc(100% - 20px);overflow:auto;background:#0b0e14ee;border:1px solid var(--line);padding:12px 14px}
#hud h1{font:700 16px Syne,sans-serif;margin:0 0 4px;color:var(--phos)}
#hud .sub{color:var(--dim);font:11px/1.4 'IBM Plex Mono',monospace;margin-bottom:8px}
#q{width:100%;padding:7px 9px;background:#12161f;color:var(--ink);border:1px solid var(--line);font:13px 'IBM Plex Sans',sans-serif}
#qres{max-height:280px;overflow:auto;margin:4px 0 8px;border:1px solid var(--line);display:none;background:#12161f}
#qres.on{display:block}
#qres .ri{padding:6px 9px;cursor:pointer;border-bottom:1px solid var(--line);font-size:12.5px}
#qres .ri:hover,#qres .ri.sel{background:#6a9bb022}
#qres .ri b{color:var(--ice)}
#qres .rm{color:var(--dim);font-size:11px}
#qres .rs{float:right;color:var(--phos);font-size:10.5px;margin-left:6px}
#qres .rnone{padding:7px 9px;color:var(--dim);font-size:12px}
#tip{position:fixed;z-index:20;pointer-events:none;display:none;max-width:300px;background:#12161ff2;color:#e8e2d4;font-size:12px;line-height:1.45;padding:8px 10px;border:1px solid var(--line)}
#tip b{color:var(--phos)}
#panel .k{font:700 11px 'IBM Plex Mono',monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--phos);margin:11px 0 3px}
#panel .pr{color:var(--dim);font-size:12px;margin-bottom:8px}
#panel ul{margin:4px 0;padding-left:18px}#panel li{font-size:12.5px;margin:2px 0}
#panel a{color:var(--ice)}
.pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:10px;color:#0b0e14;margin:0 4px 4px 0}
line.hl,path.hl{stroke:#e0c07a!important;opacity:.95!important}
#stage svg{overflow:hidden}
.tog{display:block;font-size:12.5px;margin:5px 0;cursor:pointer;user-select:none;color:#d7d0c2}
.tog input{margin-right:6px;vertical-align:-1px}
#legend{display:flex;flex-wrap:wrap;gap:4px 10px;margin-top:8px}
.lg{font:11px 'IBM Plex Mono',monospace;color:#c9c2b3;cursor:pointer}.lg i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
.lg.off{opacity:.3}.lg.solo{outline:1px solid var(--ice)}
#panel{position:absolute;right:12px;top:10px;z-index:8;width:300px;max-height:calc(100% - 24px);overflow:auto;background:#0b0e14f2;border:1px solid var(--line);padding:14px 16px;display:none}
#panel h2{font:700 16px Syne,sans-serif;margin:0 0 4px}
#close{position:absolute;top:8px;right:10px;cursor:pointer;color:var(--dim);font-size:18px}
#btns{position:absolute;bottom:10px;right:14px;z-index:8;display:flex;gap:6px}
#btns button{font:12px 'IBM Plex Sans',sans-serif;cursor:pointer;background:#12161f;color:var(--ice);border:1px solid var(--line);padding:6px 10px}
.note{position:absolute;bottom:10px;left:14px;z-index:8;font:11px 'IBM Plex Mono',monospace;color:var(--dim);background:#0b0e14c8;padding:4px 8px}
#flk{display:none;margin:6px 0;border:1px solid var(--line);padding:8px 10px}
#flk.on{display:block}
#flk .row{display:flex;align-items:center;gap:8px;margin:3px 0;font:11px 'IBM Plex Mono',monospace}
#flk .row label{flex:0 0 118px;color:var(--dim)}
#flk .row input[type=range]{flex:1;min-width:0}
#flk .row .v{flex:0 0 40px;text-align:right}
text.lab{font:9px 'IBM Plex Mono',monospace;fill:#e8e2d4;pointer-events:none;paint-order:stroke;stroke:#0b0e14;stroke-width:3px}
.sect text{font:800 13px Syne,sans-serif;fill:#e0c07a;fill-opacity:.85;letter-spacing:.1em;pointer-events:none;paint-order:stroke;stroke:#0b0e14;stroke-width:4px}
"""


def load_graph():
    with open(os.path.join(DATA, "graph.json"), encoding="utf-8") as f:
        return json.load(f)


def page(title, body, active, body_class=""):
    bc = f' class="{body_class}"' if body_class else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — Weak.Intel</title>
{FONTS}<style>{CSS}</style></head><body{bc}>
{navbar(active)}
{body}
</body></html>"""


def write(name, title, body, active):
    html_out = page(title, body, active)
    path = os.path.join(DOCS, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_out)
    shutil.copy(path, os.path.join(REP, name.upper() if name != "index.html" else "INDEX.html"))


def build_index(g):
    an = g["analysis"]
    body = f"""
<div class="wrap">
  <div class="kicker">Weak.Intel · a dual-use landscape</div>
  <h1 class="display" style="font-size:clamp(2rem,5vw,3.4rem);margin:.3em 0 .4em">One stack.<br>Two faces.</h1>
  <p class="lede">The cyber landscape is not two armies. It is a single substrate —
  cryptographic primitives, vendor products, identity planes, lawful-intercept doors —
  that APTs, criminals, agencies, and blue teams all stand on. Recurring compromise
  happens where that substrate concentrates. A CRQC is the forcing event that
  reprices every recorded RSA/ECC ciphertext (harvest-now-decrypt-later) and every
  classical signature (trust-now-forge-later).</p>
  <div class="grid">
    <div class="stat"><b>{an['n_entities']}</b><span>entities</span></div>
    <div class="stat"><b>{an['n_edges']}</b><span>edges</span></div>
    <div class="stat"><b>{len(an['dual_use_nodes'])}</b><span>dual-use nodes</span></div>
    <div class="stat"><b>{an['core_scc_size']}</b><span>attack-layer SCC (emergent)</span></div>
  </div>
  <h2>The story we can already tell</h2>
  <ol>
    <li><b>The dual-use door.</b> CALEA lawful intercept was built for US law enforcement;
        Salt Typhoon used the same door. Dual_EC sat in a NIST standard for years.
        Crypto AG sold the world's ciphers while its owners read them. A shared channel
        cannot be proven exclusive — that is a theorem (S2), not a vibe.</li>
    <li><b>Leak and boomerang.</b> EternalBlue left a hoard and came back as WannaCry
        and NotPetya. TLA+ <code>Inv_NoCascade</code> is written to be violated.</li>
    <li><b>Weaponize the guard.</b> DoubleAgent and BYOVD turn EDR into the attack surface.
        “EDR is running” is not a safety invariant if the process is injectable (B2).</li>
    <li><b>CRQC as the unwind.</b> HNDL means the confidentiality loss is already booked.
        TNFL means identity credentials issued on ECDSA become impersonable at Q-Day.
        Silent-Q-Day is graded speculation: the first CRQC owner has a reason not to announce.</li>
    <li><b>Launder and vanish.</b> Crypto mixers are the settlement rail of the same
        substrate: Lazarus washed stolen funds through Tornado Cash, yet the mixer is
        also a genuine privacy tool — so <code>Tornado_Cash</code>, <code>Samourai_Wallet</code>,
        and <code>Financial_Privacy</code> surface as dual-use nodes on their own, not by
        assertion. The accountability split is honest: OFAC's Tornado Cash designation
        was judicially vacated (the immutable code <em>got away</em>) while its developer
        Roman Storm did not — the protocol outlived the sanction, the person did not.</li>
    <li><b>The marketplace tier.</b> eCrime is not just crews and malware; it is a wholesale
        economy. Initial Access Brokers sell the foothold; darknet markets (Silk Road,
        AlphaBay, and their continuous rebirths) move stolen data and access. Takedowns
        kill instances, not the model — which is why the class node persists while the
        instances land in <em>did-not-get-away</em>.</li>
    <li><b>What still works.</b> Segmentation, immutable backups, memory-safe rewrites,
        AES-256, ML-KEM, PPL on security services. They work because they leave the
        shared public-key substrate or shrink the blast radius — not because they paint over it.</li>
  </ol>
  <p><a href="bubblemap.html">Open the bubble map</a> · <a href="methodology.html">How this is graded</a></p>
  <div class="foot">Public records only. Opinion and analysis, not allegations of criminal conduct.
  See methodology. Analog of earnings-bubble for the operator landscape.</div>
</div>"""
    write("index.html", "Home", body, "Home")


def build_dashboard(g):
    an = g["analysis"]
    ents = g["entities"]

    def rows(items, key=None):
        out = []
        for it in items:
            nid = it["id"] if isinstance(it, dict) else it
            rec = ents.get(nid, {})
            extra = ""
            if isinstance(it, dict) and "target_in" in it:
                extra = f"<td>{it['target_in']}</td>"
            out.append(
                f"<tr><td>{html.escape(nid)}</td><td>{html.escape(rec.get('type',''))}</td>"
                f"<td>{html.escape(rec.get('bucket',''))}</td>{extra}</tr>"
            )
        return "\n".join(out)

    body = f"""
<div class="wrap">
  <div class="kicker">Dashboard</div>
  <h1>Mesh statistics</h1>
  <div class="grid">
    <div class="stat"><b>{an['n_entities']}</b><span>entities</span></div>
    <div class="stat"><b>{an['n_edges']}</b><span>edges</span></div>
    <div class="stat"><b>{len(an['dual_use_nodes'])}</b><span>dual-use</span></div>
    <div class="stat"><b>{len(an['crqc_fragile'])}</b><span>CRQC-fragile</span></div>
  </div>
  <h2>Recurring targets</h2>
  <table><thead><tr><th>Node</th><th>Type</th><th>Bucket</th><th>Target in</th></tr></thead>
  <tbody>{rows(an['recurring_targets'])}</tbody></table>
  <h2 class="dual">Dual-use nodes</h2>
  <p>Protector and target, or an explicit dual-use door.</p>
  <p>{' · '.join('<span class="tag dual">'+html.escape(n)+'</span>' for n in an['dual_use_nodes'])}</p>
  <h2>CRQC fragile vs remainder</h2>
  <p>Dies under Shor: {' · '.join('<span class="tag">'+html.escape(n)+'</span>' for n in an['crqc_fragile']) or '—'}</p>
  <p class="ok">Survives (model): {' · '.join('<span class="tag ok">'+html.escape(n)+'</span>' for n in an['crqc_survives']) or '—'}</p>
  <h2>Emergent cores (Tarjan SCC by edge layer)</h2>
  <p>Headline core is the SCC over <b>attack</b> edges only (targets / exploits / route / harvests / dual-use).
  Overlay and capability cycles are listed separately. Empty attack core is a valid result, not a fallback.</p>
  <p><b>Attack core ({an.get('core_scc_size',0)}):</b> {html.escape(', '.join(an.get('core_scc') or []) or '(none)')}</p>
  <p><b>Robust (fact|strong) ({an.get('core_scc_robust_size',0)}):</b> {html.escape(', '.join(an.get('core_scc_robust') or []) or '(none)')}</p>
  <p><b>Capability-layer cycles:</b> {len(an.get('sccs_capability') or [])} &nbsp;
     <b>Overlay-layer cycles:</b> {len(an.get('sccs_overlay') or [])} &nbsp;
     extra in all-edges SCC (not core): {html.escape(', '.join((an.get('nodes_only_in_all_edges_scc') or [])[:20]) or 'none')}</p>
  <p>WCC sizes {an.get('wcc_sizes')} · isolates {an.get('n_isolates')} ·
     attack chokepoints (articulation): {html.escape(', '.join(an.get('chokepoints') or []) or 'none')}</p>
  <h2>Got away with / did not</h2>
  <p>Delayed exposure: {' · '.join(html.escape(n) for n in an['got_away']) or '—'}</p>
  <p>Public disruption/leak/indictment: {' · '.join(html.escape(n) for n in an['did_not_get_away']) or '—'}</p>
  <div class="foot">Sinks are public-record outcomes, not verdicts of guilt.</div>

  <h2>Reading the emergent layers</h2>
  <p><b>The mixer dual-use is data-driven.</b> Nothing in the pipeline hand-labels a laundering
  rail. <code>Tornado_Cash</code> and <code>Samourai_Wallet</code> appear in the dual-use set
  above only because the graph records them both <em>protecting</em> <code>Financial_Privacy</code>
  and being <em>targeted</em> by OFAC/DOJ/FinCEN — the same test that flags CALEA and EternalBlue.
  Lazarus using Tornado Cash to wash stolen funds is a <code>uses</code> edge, not a moral tag.</p>
  <p><b>Protocol vs person.</b> The accountability sinks separate the code from its authors:
  <code>Tornado_Cash</code> lands in <em>got-away</em> (OFAC's designation was vacated in 2024;
  the immutable contracts persist on-chain) while <code>Roman_Storm</code> lands in
  <em>did-not-get-away</em> (convicted 2025). A sanction against autonomous code is not the
  same as a conviction of a developer, and the graph refuses to conflate them.</p>
  <p><b>The marketplace tier is a class, not a headline.</b> <code>Darknet_Market</code> is a
  capability node that <code>Silk_Road</code>, <code>AlphaBay</code>, and <code>Nexus</code>
  instantiate; <code>IABs</code> feed it wholesale access. The instances sit in
  <em>did-not-get-away</em> (Ulbricht, Operation Bayonet) but the class keeps a live degree —
  the graph's way of showing that takedowns remove instances, not the model.</p>
</div>"""
    write("dashboard.html", "Dashboard", body, "Dashboard")


def build_methodology():
    body = """
<div class="wrap">
  <div class="kicker">Methodology</div>
  <h1>Proven, evidenced, speculative</h1>
  <p>Copied in spirit from earnings-bubble: the interesting claims are the ones you can run.</p>
  <h2>Layers</h2>
  <ul>
    <li><b>Proven</b> — Z3 SAT/UNSAT, TLA+ invariant violation, Alloy instance, graph SCC. No named person is “proven guilty.” What is proven is structure: dual-use doors, leak cascades, CRQC vs RSA.</li>
    <li><b>Evidenced</b> — public advisories, indictments, declassified reporting, MITRE, CISA KEV. Attribution is probabilistic (a cluster, not a roster).</li>
    <li><b>Speculative</b> — Silent Q-Day concealment, specific current harvest scale, intent. Graded and kept out of the solvers.</li>
  </ul>
  <h2>Honesty rules</h2>
  <ul>
    <li>No intent inferred from adjacency.</li>
    <li>Collective nouns describe cited actions, not minds.</li>
    <li>“Got away with” means delayed public exposure or non-accountability in the record.</li>
    <li>Criminal vs clear-world is an edge with a grade.</li>
    <li>Commercial spyware (covert implant) is not the same as device forensics (physical custody).</li>
  </ul>
  <h2>Reproduce</h2>
  <pre style="background:#12161f;padding:12px;border:1px solid var(--line)">bash run_all.sh</pre>
  <div class="foot">Independent research. Corrections via issues. Not legal advice, not classified disclosure.</div>
</div>"""
    write("methodology.html", "Methodology", body, "Methodology")


def build_atlas(g):
    rows = []
    for fn in g.get("blocks") or []:
        stub = fn.replace(".json", "")
        rows.append(
            f'<tr><td><a href="r-{html.escape(stub)}.html">{html.escape(stub)}</a></td>'
            f"<td><code>{html.escape(fn)}</code></td></tr>"
        )
    body = f"""
<div class="wrap">
  <div class="kicker">Atlas</div>
  <h1>Research blocks</h1>
  <p>Each block is an on-site page (entities, edges, sources) plus structured <code>.json</code>.</p>
  <p><a href="research.html">Open the research index</a></p>
  <table><thead><tr><th>Page</th><th>Data</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
</div>"""
    write("atlas.html", "Atlas", body, "Atlas")


EXTRA_GLOBE = [
    ["IonQ", 39.00, -76.94, "quantum", "Trapped-ion builder, College Park / DC area."],
    ["IBM Quantum", 41.18, -73.80, "quantum", "Yorktown Heights superconducting program."],
    ["Google Quantum", 34.42, -119.70, "quantum", "Santa Barbara / Goleta superconducting (Willow)."],
    ["PsiQuantum", 37.44, -122.14, "quantum", "Photonic million-qubit bet; Omega at GlobalFoundries NY."],
    ["GlobalFoundries Malta", 42.97, -73.79, "supply", "300mm silicon photonics for PsiQuantum Omega."],
    ["ASML Veldhoven", 51.42, 5.40, "supply", "Sole EUV lithography maker."],
    ["TSMC Taiwan", 25.00, 121.50, "choke", "~95% leading-edge logic."],
    ["Infineon Munich", 48.14, 11.58, "pqc", "SLC27 PQC secure controller."],
    ["Bluefors Helsinki", 60.17, 24.94, "supply", "Dilution refrigerators for superconducting machines."],
    ["USTC Hefei", 31.82, 117.23, "quantum", "Zuchongzhi / Jiuzhang / Origin Quantum cluster."],
    ["Microsoft Redmond", 47.64, -122.13, "vendor", "OS/identity/mail dual-use node; Pluton; SymCrypt PQC."],
    ["Citizen Lab Toronto", 43.66, -79.40, "blue", "Academic forensics of mercenary spyware."],
    ["NSO Herzliya", 32.16, 34.84, "threat", "Pegasus commercial spyware (Unit 8200 alumni reporting)."],
    ["CrowdStrike Austin", 30.27, -97.74, "blue", "EDR vendor; Fancy Bear naming."],
    ["Huntress Ellicott City", 39.27, -76.80, "blue", "SMB/MSP managed EDR + 24/7 SOC (Maryland)."],
    ["Snyk Boston", 42.36, -71.06, "blue", "Developer SCA/SAST/container platform (Boston / Tel Aviv)."],
    ["xLight Palo Alto", 37.44, -122.14, "supply", "FEL EUV light source; CHIPS equity LOI; Albany 2028 prototype."],
    ["Substrate San Francisco", 37.77, -122.42, "supply", "X-ray lithography + planned US foundry; In-Q-Tel / Founders Fund."],
    ["Anduril Costa Mesa", 33.64, -117.92, "intel", "Lattice C2 + autonomous systems."],
    ["Shield AI San Diego", 32.72, -117.16, "intel", "Hivemind autonomy / V-BAT."],
    ["Palantir Denver", 39.74, -104.99, "intel", "Gotham / Maven. IQT-seeded public history."],
    ["In-Q-Tel Arlington", 38.88, -77.11, "intel", "CIA-chartered nonprofit VC."],
    ["SACLA Harima", 34.944, 134.427, "quantum", "RIKEN SPring-8 Angstrom Compact FEL."],
    ["European XFEL Schenefeld", 53.589, 9.829, "quantum", "3.4 km superconducting hard XFEL (DESY to Schenefeld)."],
    ["LCLS SLAC", 37.417, -122.204, "quantum", "US hard XFEL, Menlo Park."],
    ["Xarion Vienna", 48.21, 16.37, "intel", "IQT: laser-ultrasound sensing, not an XFEL."],
]


def build_globe(g):
    pts = []
    seen = set()
    for rec in g["entities"].values():
        if rec.get("lat") is None:
            continue
        kind = rec.get("bucket") or "intel"
        pts.append([rec["id"], rec["lat"], rec["lon"], kind, (rec.get("notes") or "")[:280], rec.get("files") or []])
        seen.add(rec["id"].lower())
    for name, lat, lon, kind, note in EXTRA_GLOBE:
        if name.lower() in seen:
            continue
        pts.append([name, lat, lon, kind, note, []])
    arcs = [
        [39.11, -76.77, -23.80, 133.74, "intel", "NSA Fort Meade <-> Pine Gap"],
        [51.90, -2.12, 39.11, -76.77, "intel", "GCHQ <-> NSA (Five Eyes)"],
        [51.42, 5.40, 25.00, 121.50, "supply", "ASML EUV -> TSMC"],
        [42.97, -73.79, 37.44, -122.14, "quantum", "GlobalFoundries Omega -> PsiQuantum"],
        [48.14, 11.58, 47.64, -122.13, "pqc", "Infineon SE -> Microsoft/Windows TPM plane"],
        [32.16, 34.84, 43.66, -79.40, "threat", "NSO Pegasus <-> Citizen Lab exposure"],
        [40.43, -111.93, 39.11, -76.77, "intel", "Utah Data Center <-> Fort Meade"],
        [53.576, 9.879, 53.589, 9.829, "quantum", "DESY linac -> European XFEL Schenefeld"],
        [34.944, 134.427, 37.417, -122.204, "quantum", "SACLA <-> LCLS (hard XFEL pair)"],
    ]
    colors = {
        "intel": "#7ea8be", "quantum": "#c9a0dc", "supply": "#6d9a6f", "pqc": "#c17a4a",
        "threat": "#b54a3c", "blue": "#8fbf9a", "choke": "#e0c07a", "vendor": "#6a9bb0",
        "actor": "#b54a3c", "malware": "#c17a4a", "people": "#d9c48a", "crypto": "#6a9bb0",
        "protectors": "#6d9a6f", "targets": "#e0c07a", "clear": "#a89f8d",
        "capability": "#8a6a4a", "other": "#6e6a63",
    }
    legend = [
        ("intel", "intel / facilities"), ("quantum", "quantum builders"),
        ("supply", "fab / cryo / lithography"), ("pqc", "PQC silicon"),
        ("threat", "spyware / threat"), ("blue", "protectors"),
        ("choke", "compute chokepoint"),
    ]
    body = GLOBE_HTML.replace("__POINTS__", json.dumps(pts)).replace("__ARCS__", json.dumps(arcs)).replace(
        "__COLORS__", json.dumps(colors)).replace("__LEGEND__", json.dumps(legend))
    html_out = page("Globe", body, "Globe", body_class="map-body")
    path = os.path.join(DOCS, "globe.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_out)
    shutil.copy(path, os.path.join(REP, "GLOBE.html"))


GLOBE_HTML = r"""
<div id="stage">
<div id="hud">
  <h1>Geographic spine</h1>
  <div class="sub">drag to rotate · scroll to zoom · click a pin for a profile. Basemap from world-atlas (needs internet).</div>
  <div id="gleg"></div>
</div>
<div id="tip"></div>
<div class="note">land = countries-110m · gold/ice pins = public-record sites · dashed arcs = documented dependencies</div>
<svg id="g"></svg>
</div>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3"></script>
<script>
const POINTS=__POINTS__, ARCS=__ARCS__, COLORS=__COLORS__, LEGEND=__LEGEND__;
const stage=document.getElementById('stage');
const svg=d3.select('#g');
const tip=document.getElementById('tip');
LEGEND.forEach(([k,t])=>{
  const s=document.createElement('div'); s.className='sub';
  s.innerHTML='<span style="display:inline-block;width:9px;height:9px;border-radius:50%;background:'+(COLORS[k]||'#e0c07a')+';margin-right:7px"></span>'+t;
  document.getElementById('gleg').appendChild(s);
});
let W,H,R,proj,path,countries=null,spin=true;
function size(){W=stage.clientWidth; H=stage.clientHeight; R=Math.min(W,H)/2-28;
 svg.attr('width',W).attr('height',H);
 proj=d3.geoOrthographic().scale(R).translate([W/2,H/2]).clipAngle(90).rotate([-20,-18]);
 path=d3.geoPath(proj);}
size();
const ocean=svg.append('circle').attr('fill','#15202c').attr('stroke','#2a241c');
const gGrat=svg.append('path').attr('fill','none').attr('stroke','#2c3a48').attr('stroke-width',.4);
const gLand=svg.append('g');
const gArc=svg.append('g');
const gPt=svg.append('g');
const grat=d3.geoGraticule10();
function visible(lon,lat){const c=proj.invert([W/2,H/2]); if(!c) return false; return d3.geoDistance([lon,lat],c)<Math.PI/2;}
function render(){
 ocean.attr('cx',W/2).attr('cy',H/2).attr('r',R);
 gGrat.attr('d',path(grat));
 if(countries){
  gLand.selectAll('path').data(countries.features).join('path')
   .attr('d',path).attr('fill','#3d4a3a').attr('stroke','#1c241c').attr('stroke-width',.4);
 }
 gArc.selectAll('path').data(ARCS).join('path')
  .attr('d',d=>path({type:'LineString',coordinates:[[d[3],d[2]],[d[1],d[0]]]}))
  .attr('fill','none').attr('stroke',d=>COLORS[d[4]]||'#c17a4a').attr('stroke-width',1.4).attr('opacity',.55)
  .attr('stroke-dasharray','4,3');
 gPt.selectAll('circle').data(POINTS).join('circle')
  .attr('transform',d=>{const p=proj([d[2],d[1]]); return p?'translate('+p[0]+','+p[1]+')':'translate(-99,-99)';})
  .attr('r',d=>d[3]==='choke'?7:5.5)
  .attr('fill',d=>COLORS[d[3]]||'#e0c07a')
  .attr('stroke','#0b0e14').attr('stroke-width',1.2)
  .attr('opacity',d=>visible(d[2],d[1])?1:0)
  .style('pointer-events',d=>visible(d[2],d[1])?'all':'none')
  .style('cursor','pointer')
  .on('mousemove',(e,d)=>{tip.style.display='block'; tip.style.left=(e.clientX+14)+'px'; tip.style.top=(e.clientY+12)+'px';
    tip.innerHTML='<b>'+d[0]+'</b><br>'+(d[3]||'')+'<br><span style="color:#c9c2b3">'+(d[4]||'')+'</span>';})
  .on('mouseout',()=>tip.style.display='none')
  .on('click',(e,d)=>{e.stopPropagation(); tip.style.display='none'; openPop(d,e);});
}
d3.json('https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json').then(world=>{
 countries=topojson.feature(world, world.objects.countries); render();
}).catch(()=>{render();});
function openPop(d,e){
 const r=stage.getBoundingClientRect();
 document.querySelectorAll('.pop').forEach(x=>x.remove());
 const div=document.createElement('div'); div.className='pop';
 div.style.cssText='position:absolute;left:'+Math.max(8,Math.min(e.clientX-r.left, W-300))+'px;top:'+Math.max(8,Math.min(e.clientY-r.top-20,H-140))+'px;width:280px;background:#12161ff2;border:1px solid #2a241c;padding:12px;z-index:30';
 const files=(d[5]||[]).map(f=>{const s=String(f).replace('.json',''); return '<a href="r-'+s+'.html">'+s+'</a>';}).join(' · ');
 div.innerHTML='<div style="display:flex;justify-content:space-between;color:#e0c07a;font:700 14px Syne,sans-serif"><span>'+d[0]+'</span><span class="pc" style="cursor:pointer">×</span></div>'
  +'<div style="color:#8a8378;font:11px IBM Plex Mono,monospace;margin:4px 0 8px">'+(d[3]||'')+'</div>'
  +'<div style="color:#d7d0c2;font-size:13px">'+(d[4]||'')+'</div>'
  +(files?'<div style="margin-top:8px">'+files+'</div>':'');
 stage.appendChild(div); div.querySelector('.pc').onclick=()=>div.remove();
}
let v0,r0;
svg.call(d3.drag()
 .on('start',e=>{v0=[e.x,e.y]; r0=proj.rotate(); spin=false;})
 .on('drag',e=>{const k=75/proj.scale(); proj.rotate([r0[0]+(e.x-v0[0])*k, r0[1]-(e.y-v0[1])*k]); render();}));
svg.on('wheel',e=>{e.preventDefault(); const s=proj.scale(); proj.scale(Math.max(R*0.6, Math.min(R*3, s*(e.deltaY>0?0.94:1.06)))); render();});
d3.timer(()=>{if(!spin)return; const r=proj.rotate(); proj.rotate([r[0]+0.12,r[1]]); render();});
addEventListener('resize',()=>{size(); render();});
</script>
"""


CONTAINS = {
    "WISeKey": ["SEALSQ"],
    "Honeywell": ["Quantinuum"],
    "IonQ": ["Oxford_Ionics"],
    "UnitedHealth": ["Change_Healthcare"],
    "Thales": ["Luna_HSM"],
    "Entrust": ["nShield_HSM"],
    "Microsoft": ["Microsoft_Pluton"],
    "NSO_Group": ["Pegasus"],
    "ASML": ["Zeiss_SMT"],
}

BLABEL = {
    "actor": "APTs / crime",
    "malware": "malware",
    "people": "researchers",
    "crypto": "crypto",
    "protectors": "vendors",
    "intel": "intel / facilities",
    "targets": "targets",
    "blue": "blue team",
    "quantum": "quantum",
    "clear": "clear-world",
    "capability": "capability",
    "other": "other",
}


def build_bubblemap(g):
    ents = g["entities"]
    nodes = []
    for rec in ents.values():
        nodes.append({
            "id": rec["id"],
            "label": rec["id"].replace("_", " "),
            "bucket": rec.get("bucket") or "other",
            "deg": rec.get("deg") or 1,
            "dual": rec.get("dual_use"),
            "scc": rec.get("scc_core"),
            "fragile": rec.get("crqc_fragile"),
            "robust": rec.get("scc_robust"),
            "isolate": rec.get("isolate"),
            "wcc": rec.get("wcc_id"),
            "wcc_size": rec.get("wcc_size"),
            "chokepoint": rec.get("chokepoint"),
            "type": rec.get("type"),
            "notes": (rec.get("notes") or "")[:400],
            "files": rec.get("files") or [],
        })
    overlay_kinds = {
        "affiliates", "hosted_at", "standardizes", "authored", "attributed_to",
        "has_capability", "got_away", "did_not_get_away",
    }
    links = [{
        "source": e["from"], "target": e["to"],
        "kind": e["kind"], "instrument": e.get("instrument") or "",
        "grade": e.get("grade"), "dual": e["kind"] == "dual_use",
        "overlay": e.get("layer") == "overlay" or e["kind"] in overlay_kinds,
        "elayer": e.get("layer") or "",
        "note": (e.get("notes") or "")[:200],
        "file": e.get("source_file") or "",
    } for e in g["edges"]]
    ids = {n["id"] for n in nodes}
    contains = {p: [c for c in ch if c in ids] for p, ch in CONTAINS.items() if p in ids}
    contains = {p: ch for p, ch in contains.items() if ch}
    legend = "".join(
        f'<span class=lg data-b="{b}"><i style="background:{COLORS.get(b,"#6e6a63")}"></i>{html.escape(BLABEL[b])}</span>'
        for b in BLABEL if any(n["bucket"] == b for n in nodes)
    )
    body = (MAP_HTML
            .replace("__NODES__", json.dumps(nodes))
            .replace("__LINKS__", json.dumps(links))
            .replace("__COLORS__", json.dumps(COLORS))
            .replace("__CONTAINS__", json.dumps(contains))
            .replace("__LEGEND__", legend)
            .replace("__N__", str(len(nodes)))
            .replace("__E__", str(len(links))))
    html_out = page("Bubble Map", body, "Bubble Map", body_class="map-body")
    path = os.path.join(DOCS, "bubblemap.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_out)
    shutil.copy(path, os.path.join(REP, "BUBBLEMAP.html"))


MAP_HTML = r"""
<div id="stage">
<div id="hud">
  <h1>Bubble Map</h1>
  <div class="sub">drag · scroll to zoom · click a node · group by sector</div>
  <input id="q" placeholder="Find a node…" autocomplete="off">
  <div id="qres"></div>
  <label class="tog">highlight reach
    <select id="hops" style="margin-left:6px;background:#12161f;color:#e8e2d4;border:1px solid #2a241c">
      <option value="1" selected>1-hop (narrow)</option>
      <option value="2">2-hop</option>
      <option value="cc">weak component</option>
    </select>
  </label>
  <label class="tog"><input type="checkbox" id="tIso"> hide isolates (WCC size 1)</label>
  <div class="tog" style="display:block">
    <div style="margin-bottom:4px">connections filter <span id="degCount" class="sub" style="float:right"></span></div>
    <div class="row" style="display:flex;gap:6px;align-items:center"><label style="width:30px">min</label><input type="range" id="degMin" min="0" max="25" step="1" value="0" style="flex:1;min-width:0"><span class="v" id="degMinV" style="width:28px;text-align:right">0</span></div>
    <div class="row" style="display:flex;gap:6px;align-items:center"><label style="width:30px">max</label><input type="range" id="degMax" min="1" step="1" style="flex:1;min-width:0"><span class="v" id="degMaxV" style="width:28px;text-align:right"></span></div>
  </div>
  <label class="tog"><input type="checkbox" id="tOverlay" checked> overlay / attribution / affiliation edges</label>
  <label class="tog"><input type="checkbox" id="tCore"> dim all but the attack-layer SCC (emergent; may be empty)</label>
  <label class="tog"><input type="checkbox" id="tCluster" checked> group by sector (flocking)</label>
  <label class="tog"><input type="checkbox" id="tAgg" checked> nest known groups</label>
  <label class="tog"><input type="checkbox" id="tLab"> all labels (default: hubs only)</label>
  <label class="tog"><input type="checkbox" id="tFlk"> tune flocking (live sliders)</label>
  <div id="flk"></div>
  <div id="legend">__LEGEND__</div>
  <div class="sub" style="margin-top:8px">Click a legend colour to isolate a sector.</div>
</div>
<div id="panel"><span id="close">&times;</span><div id="pbody"></div></div>
<div id="tip"></div>
<div id="btns"><button id="bFit">Fit to view</button><button id="bReset">Reset focus</button></div>
<div class="note">__N__ entities · __E__ edges · gold ring = attack-layer SCC (emergent) · dashed = overlay · click narrows highlight by hop radius</div>
<svg id="g"></svg>
</div>
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
const NODES=__NODES__, LINKS=__LINKS__, COLORS=__COLORS__, CONTAINS=__CONTAINS__;
const NLABEL={}; NODES.forEach(n=>NLABEL[n.id]=n.label||n.id);
const W=()=>document.getElementById('stage').clientWidth, H=()=>document.getElementById('stage').clientHeight;
const svg=d3.select('#g').attr('width','100%').attr('height','100%');
const root=svg.append('g');
const id2n=new Map(NODES.map(n=>[n.id,n]));
const lerp=x=>typeof x==='object'?x.id:x;
const tip=document.getElementById('tip');
const PARENTS={}, GROUPS={};
Object.keys(CONTAINS).forEach(p=>{ if(!id2n.has(p)) return;
  CONTAINS[p].forEach(c=>{ if(!id2n.has(c)) return;
    (PARENTS[c]=PARENTS[c]||[]).push(p); (GROUPS[p]=GROUPS[p]||[]).push(c); }); });
NODES.forEach(n=>{ n.parent=(PARENTS[n.id]&&PARENTS[n.id][0])||null; });
let aggregate=true, clustered=true, allLab=false, fitted=false, curK=1, soloB=null, egoOn=null, pendingFocus=null;
const BUCKETS=[...new Set(NODES.map(n=>n.bucket))];
const FLK={velDecay:.55,alphaDecay:.035,charge:-90,chargeMax:260,linkStr:.14,linkDist:52,
           cohesion:.55,collidePad:10,collideStr:.9,collideIter:2,spreadX:.42,spreadY:.42};
function bAnchor(b,axis){const i=BUCKETS.indexOf(b),NB=BUCKETS.length||1,a=(i/NB)*2*Math.PI-Math.PI/2;
 return axis==='x'?W()/2+Math.cos(a)*Math.min(W(),1400)*FLK.spreadX:H()/2+Math.sin(a)*Math.min(H(),900)*FLK.spreadY;}
const ancX=d=>{if(aggregate&&d.parent){const p=id2n.get(d.parent);if(p&&p.x!=null)return p.x;}return clustered?bAnchor(d.bucket,'x'):W()/2;};
const ancY=d=>{if(aggregate&&d.parent){const p=id2n.get(d.parent);if(p&&p.y!=null)return p.y;}return clustered?bAnchor(d.bucket,'y'):H()/2;};
const cohStr=d=>(aggregate&&d.parent&&id2n.has(d.parent))?Math.max(FLK.cohesion,0.92):(clustered?FLK.cohesion:.05);
const rad=d=>4+Math.sqrt(d.deg||1)*2.2;
const LABMIN=5;
const labThr=k=>Math.max(2,Math.round(LABMIN/Math.max(k,1)));
let degMin=0, degMax=Infinity;
function nodeHidden(d){
 if(!d) return false;
 if(document.getElementById('tIso').checked && d.isolate) return true;
 const g=d.deg||1;
 return g<degMin || g>degMax;
}
function labVisible(d){return !nodeHidden(d)&&(allLab||d.scc||d.dual||d.deg>=labThr(curK));}
const labPad=d=>labVisible(d)?Math.min((d.label||'').length*1.8,28):0;
(function(){const AFF={};BUCKETS.forEach(a=>AFF[a]={});
 LINKS.forEach(l=>{const s=id2n.get(lerp(l.source)),t=id2n.get(lerp(l.target));
  if(s&&t&&s.bucket!==t.bucket){AFF[s.bucket][t.bucket]=(AFF[s.bucket][t.bucket]||0)+1;AFF[t.bucket][s.bucket]=(AFF[t.bucket][s.bucket]||0)+1;}});
 const rem=new Set(BUCKETS),ord=[],tot=b=>Object.values(AFF[b]||{}).reduce((x,y)=>x+y,0);
 let cur=[...BUCKETS].sort((a,b)=>tot(b)-tot(a))[0]; if(cur){ord.push(cur);rem.delete(cur);}
 while(rem.size){let best=null,bs=-1;rem.forEach(r=>{const s=(AFF[cur]&&AFF[cur][r])||0;if(s>bs){bs=s;best=r;}});
  if(!best) best=[...rem][0]; ord.push(best); rem.delete(best); cur=best;}
 BUCKETS.length=0; ord.forEach(b=>BUCKETS.push(b));
})();
(function(){const GA=2.399963229, byB={};
 NODES.forEach(n=>{(byB[n.bucket]=byB[n.bucket]||[]).push(n);});
 Object.keys(byB).forEach(b=>{const arr=byB[b],ax=bAnchor(b,'x'),ay=bAnchor(b,'y');
  arr.forEach((n,j)=>{const a=j*GA,r=10+Math.sqrt(j)*7; n.x=ax+Math.cos(a)*r; n.y=ay+Math.sin(a)*r;});});
})();
const strokeOf=d=>d.dual?'#b54a3c':(d.kind==='protects'?'#6d9a6f':'#3a342c');
const baseW=d=>d.dual?1.9:(d.overlay?0.9:1.2);
const link=root.append('g').selectAll('path').data(LINKS).join('path').attr('fill','none')
 .attr('stroke',strokeOf).attr('stroke-width',baseW)
 .attr('stroke-dasharray',d=>d.overlay?'4,3':null).attr('opacity',.75);
const linkHit=root.append('g').selectAll('path').data(LINKS).join('path').attr('fill','none')
 .attr('stroke','transparent').attr('stroke-width',9).style('cursor','help')
 .on('mouseover',(e,d)=>{link.filter(x=>x===d).classed('hl',true);
   tip.style.display='block';
   tip.innerHTML='<b>'+lerp(d.source)+' → '+lerp(d.target)+'</b><br>'+(d.kind||'')+' · '+(d.instrument||'—')
    +(d.grade?' · '+d.grade:'')+(d.overlay?' · overlay':'')
    +(d.note?'<br><span style="color:#c9c2b3">'+(d.note||'')+'</span>':'');})
 .on('mousemove',e=>{tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+12)+'px';})
 .on('mouseout',()=>{link.classed('hl',false);tip.style.display='none';});
const nodeG=root.append('g');
const groupG=root.insert('g',()=>nodeG.node()).attr('class','grp');
const node=nodeG.selectAll('g').data(NODES).join('g').style('cursor','pointer');
node.append('circle').attr('class','core').attr('r',rad)
 .attr('fill',d=>COLORS[d.bucket]||'#6e6a63')
 .attr('stroke',d=>d.dual?'#b54a3c':(d.scc?'#e0c07a':'#0b0e14'))
 .attr('stroke-width',d=>d.dual||d.scc?2.4:1);
node.filter(d=>d.dual).append('circle').attr('class','halo').attr('r',d=>rad(d)+3)
 .attr('fill','none').attr('stroke','#6a9bb0').attr('stroke-dasharray','3,3');
const labels=root.append('g').selectAll('text').data(NODES).join('text')
 .attr('class','lab').text(d=>d.label).attr('dx',8).attr('dy',3).style('display','none');
const sectorG=root.append('g').attr('class','sect');
function drawSectors(){sectorG.raise();sectorG.selectAll('text').data(clustered?BUCKETS:[],b=>b).join('text')
 .attr('x',b=>bAnchor(b,'x')).attr('y',b=>bAnchor(b,'y')-52).attr('text-anchor','middle')
 .text(b=>(b||'').toUpperCase());}
function applyLabels(){if(egoOn||soloB)return; labels.style('display',d=>labVisible(d)?null:'none');}
function drawGroups(){
 const pairs=[];
 if(aggregate){Object.keys(GROUPS).forEach(p=>{const P=id2n.get(p); if(!P||P.x==null)return;
   GROUPS[p].forEach(c=>{const C=id2n.get(c); if(C&&C.x!=null) pairs.push({k:p+'>'+c,P:P,C:C,col:COLORS[P.bucket]||'#8a8378'});});});}
 groupG.selectAll('line.gglow').data(pairs,d=>d.k).join('line').attr('class','gglow')
  .attr('x1',d=>d.P.x).attr('y1',d=>d.P.y).attr('x2',d=>d.C.x).attr('y2',d=>d.C.y)
  .attr('stroke',d=>d.col).attr('stroke-width',7).attr('stroke-opacity',.16);
 groupG.selectAll('line.gline').data(pairs,d=>d.k).join('line').attr('class','gline')
  .attr('x1',d=>d.P.x).attr('y1',d=>d.P.y).attr('x2',d=>d.C.x).attr('y2',d=>d.C.y)
  .attr('stroke',d=>d.col).attr('stroke-width',2).attr('stroke-dasharray','2,5').attr('stroke-opacity',.9);
}
const sim=d3.forceSimulation(NODES)
 .velocityDecay(FLK.velDecay).alphaDecay(FLK.alphaDecay)
 .force('link',d3.forceLink(LINKS).id(d=>d.id).distance(d=>d.overlay?FLK.linkDist+16:FLK.linkDist).strength(FLK.linkStr))
 .force('charge',d3.forceManyBody().strength(FLK.charge).distanceMax(FLK.chargeMax))
 .force('x',d3.forceX(ancX).strength(cohStr)).force('y',d3.forceY(ancY).strength(cohStr))
 .force('collide',d3.forceCollide().radius(d=>rad(d)+FLK.collidePad+labPad(d)).strength(FLK.collideStr).iterations(FLK.collideIter))
 .on('tick',tick);
drawSectors(); applyLabels();
function applyFlk(reheat){
 sim.velocityDecay(FLK.velDecay).alphaDecay(FLK.alphaDecay);
 sim.force('link').strength(FLK.linkStr).distance(d=>d.overlay?FLK.linkDist+16:FLK.linkDist);
 sim.force('charge').strength(FLK.charge).distanceMax(FLK.chargeMax);
 sim.force('x').x(ancX).strength(cohStr); sim.force('y').y(ancY).strength(cohStr);
 sim.force('collide').radius(d=>rad(d)+FLK.collidePad+labPad(d)).strength(FLK.collideStr).iterations(FLK.collideIter);
 drawSectors(); if(reheat!==false){fitted=false; sim.alpha(.6).restart();}
}
function tick(){
 const px=s=>s.attr('d',d=>{const sx=d.source.x,sy=d.source.y,tx=d.target.x,ty=d.target.y,dx=tx-sx,dy=ty-sy,L=Math.hypot(dx,dy)||1,off=Math.min(L*0.16,70),cx=(sx+tx)/2-dy/L*off,cy=(sy+ty)/2+dx/L*off;return 'M'+sx+','+sy+'Q'+cx+','+cy+' '+tx+','+ty;});
 px(link); px(linkHit);
 node.attr('transform',d=>'translate('+d.x+','+d.y+')');
 labels.attr('x',d=>d.x).attr('y',d=>d.y);
 drawGroups();
 if(sim.alpha()<0.06){
   if(pendingFocus){const t=pendingFocus; pendingFocus=null; fitted=true; focusNode(t);}
   else if(!fitted){fitted=true; fit(); applyLabels(); sim.stop();}
 }
}
function rescale(k){curK=k; const s=k<1?Math.min(1/k,3.2):1;
 node.select('circle.core').attr('r',d=>rad(d)*s).attr('stroke-width',d=>(d.dual||d.scc?2.4:1)*s);
 node.select('circle.halo').attr('r',d=>(rad(d)+3)*s);
 link.attr('stroke-width',d=>baseW(d)*s);
 labels.style('font-size',(9*Math.min(s,2.2))+'px').attr('dx',d=>rad(d)*s+2);
 applyLabels();}
let panned=false;
const zoomB=d3.zoom().scaleExtent([.3,6])
 .on('start',()=>{panned=false;})
 .on('zoom',e=>{if(e.sourceEvent&&/move/.test(e.sourceEvent.type||''))panned=true;root.attr('transform',e.transform);rescale(e.transform.k);});
svg.call(zoomB);
function fit(){let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
 NODES.forEach(n=>{if(n.x<x0)x0=n.x;if(n.y<y0)y0=n.y;if(n.x>x1)x1=n.x;if(n.y>y1)y1=n.y;});
 const pad=70, k=Math.min((W()-2*pad)/Math.max(x1-x0,1),(H()-2*pad)/Math.max(y1-y0,1),2.4);
 const tx=W()/2-k*(x0+x1)/2, ty=H()/2-k*(y0+y1)/2;
 svg.transition().duration(450).call(zoomB.transform, d3.zoomIdentity.translate(tx,ty).scale(k));}
node.call(d3.drag().container(function(){return root.node();})
 .on('start',(e,d)=>{if(!e.active)sim.alphaTarget(.12).restart(); d.fx=d.x;d.fy=d.y;})
 .on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y;})
 .on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);}));
node.on('mouseenter',function(e,d){d3.select(this).select('circle.core').attr('r',rad(d)*(curK<1?Math.min(1/curK,3.2):1)+3); d3.select(this).raise();})
 .on('mouseleave',function(e,d){d3.select(this).select('circle.core').attr('r',rad(d)*(curK<1?Math.min(1/curK,3.2):1));});
node.on('click',(e,d)=>{e.stopPropagation(); showPanel(d); egoFocus(d);});
svg.on('click',()=>{if(panned)return; clearEgo(); soloB=null;
 document.querySelectorAll('.lg').forEach(x=>x.classList.remove('off','solo'));
 document.getElementById('panel').style.display='none';});
svg.on('dblclick.zoom',null).on('dblclick',()=>{clearEgo();soloB=null;});
const ADJ=new Map(NODES.map(n=>[n.id,new Set([n.id])]));
LINKS.forEach(l=>{const s=lerp(l.source),t=lerp(l.target); ADJ.get(s)&&ADJ.get(s).add(t); ADJ.get(t)&&ADJ.get(t).add(s);});
function keepSet(d){
 const mode=document.getElementById('hops').value;
 if(mode==='cc') return new Set(NODES.filter(n=>n.wcc===d.wcc).map(n=>n.id));
 const hops=+mode; const keep=new Set([d.id]); let frontier=[d.id];
 for(let h=0;h<hops;h++){const nxt=[]; frontier.forEach(id=>{(ADJ.get(id)||[]).forEach(nb=>{if(!keep.has(nb)){keep.add(nb);nxt.push(nb);}});}); frontier=nxt;}
 return keep;
}
function edgeInKeep(l, keep){
 return keep.has(lerp(l.source)) && keep.has(lerp(l.target));
}
function egoFocus(d){egoOn=d.id; const keep=keepSet(d); const S=(curK<1?Math.min(1/curK,3.2):1);
 const dist1=ADJ.get(d.id)||new Set();
 node.style('opacity',n=>keep.has(n.id)?1:.05)
  .style('pointer-events',n=>keep.has(n.id)?null:'none');
 labels.style('display',n=>keep.has(n.id)?null:'none');
 const direct=l=>lerp(l.source)===d.id||lerp(l.target)===d.id;
 const ov=document.getElementById('tOverlay').checked;
 const vis=l=>edgeInKeep(l, keep) && (ov || !l.overlay);
 link.classed('hl',false)
  .style('display',l=>vis(l)?null:'none')
  .style('opacity',l=>direct(l)?1:.45)
  .attr('stroke-width',l=>(direct(l)?baseW(l)*2.6:baseW(l))*S);
 linkHit.style('display',l=>vis(l)?null:'none').style('pointer-events',l=>vis(l)?null:'none');
 groupG.style('opacity',.12);
 node.select('circle.core').attr('stroke',n=>n.id===d.id?'#e0c07a':(dist1.has(n.id)?'#6a9bb0':(n.scc?'#e0c07a':'#0b0e14')))
  .attr('stroke-width',n=>n.id===d.id?4.5:(dist1.has(n.id)?2.8:(n.scc?2.4:1)));
}
function clearEgo(){egoOn=null; const S=(curK<1?Math.min(1/curK,3.2):1);
 node.style('opacity',1).style('pointer-events',null);
 link.classed('hl',false).style('opacity',.75).attr('stroke-width',d=>baseW(d)*S);
 linkHit.style('pointer-events',null);
 groupG.style('opacity',1);
 applyLinkVis(); applyLabels();
 node.select('circle.core').attr('stroke',n=>n.dual?'#b54a3c':(n.scc?'#e0c07a':'#0b0e14')).attr('stroke-width',n=>n.dual||n.scc?2.4:1);
}
function neighbors(d){const ins=[],outs=[];
 LINKS.forEach(l=>{const s=lerp(l.source),t=lerp(l.target);
  if(s===d.id)outs.push({n:t,i:l.instrument,k:l.kind}); if(t===d.id)ins.push({n:s,i:l.instrument,k:l.kind});});
 return {ins,outs};}
function showPanel(d){
 const p=document.getElementById('panel'), b=document.getElementById('pbody');
 const {ins,outs}=neighbors(d);
 const nb=a=>a.length?('<ul>'+a.slice(0,16).map(x=>'<li><a href="#node='+encodeURIComponent(x.n)+'">'+(NLABEL[x.n]||x.n)+'</a> <span style="color:#8a8378">('+(x.k||'')+(x.i?': '+x.i:'')+')</span></li>').join('')+(a.length>16?'<li style="color:#8a8378">+'+(a.length-16)+' more</li>':'')+'</ul>'):'<div style="color:#8a8378;font-size:12px">—</div>';
 b.innerHTML='<div class="kicker">'+(d.type||'')+' · '+(d.bucket||'')+' · deg '+d.deg+'</div><h2>'+d.label+'</h2>'
  +'<span class="pill" style="background:'+(COLORS[d.bucket]||'#6e6a63')+'">'+(d.bucket||'')+'</span>'
  +(d.dual?'<span class="tag dual">dual-use</span> ':'')
  +(d.scc?'<span class="tag">SCC core</span> ':'')
  +(d.fragile?'<span class="tag">CRQC-fragile</span>':'')
  +'<p style="color:#c9c2b3;font-size:13px">'+(d.notes||'').replace(/</g,'&lt;')+'</p>'
  +'<div class="k">Out ('+outs.length+')</div>'+nb(outs)
  +'<div class="k">In ('+ins.length+')</div>'+nb(ins)
  +((d.files&&d.files.length)?'<div class="k">Documented in</div><div>'+d.files.map(f=>{const s=String(f).replace('.json',''); return '<a href="r-'+s+'.html">'+s+'</a>';}).join(' · ')+'</div>':'');
 p.style.display='block';
}
function centerOn(d){const k=Math.max(curK,1.4); svg.transition().duration(550).call(zoomB.transform,d3.zoomIdentity.translate(W()/2-k*d.x,H()/2-k*d.y).scale(k));}
function focusNode(id){const d=id2n.get(id); if(!d)return; showPanel(d); egoFocus(d); centerOn(d);}
document.getElementById('close').onclick=()=>{document.getElementById('panel').style.display='none'; clearEgo();};
document.getElementById('tCluster').onchange=e=>{clustered=e.target.checked; applyFlk(true);};
document.getElementById('tAgg').onchange=e=>{aggregate=e.target.checked; drawGroups(); fitted=false; sim.alpha(.5).restart();};
document.getElementById('tLab').onchange=e=>{allLab=e.target.checked; applyLabels();};
const _maxDeg=d3.max(NODES,d=>d.deg||1);
(function initDeg(){
 const mx=document.getElementById('degMax');
 mx.max=_maxDeg; mx.value=_maxDeg; degMax=_maxDeg;
 document.getElementById('degMaxV').textContent=_maxDeg;
})();
function updDegCount(){
 const shown=NODES.reduce((a,d)=>a+(nodeHidden(d)?0:1),0);
 document.getElementById('degCount').textContent=shown+' / '+NODES.length+' shown';
}
function applyLinkVis(){
 const ov=document.getElementById('tOverlay').checked;
 const vis=d=>{
  if(d.overlay&&!ov) return 'none';
  const s=id2n.get(lerp(d.source)), t=id2n.get(lerp(d.target));
  if(nodeHidden(s)||nodeHidden(t)) return 'none';
  return null;
 };
 link.style('display',vis); linkHit.style('display',vis);
 node.style('display',d=>nodeHidden(d)?'none':null);
 updDegCount();
 if(!egoOn) applyLabels();
}
document.getElementById('tOverlay').onchange=applyLinkVis;
document.getElementById('tIso').onchange=applyLinkVis;
document.getElementById('degMin').oninput=e=>{degMin=+e.target.value; document.getElementById('degMinV').textContent=degMin; applyLinkVis();};
document.getElementById('degMax').oninput=e=>{degMax=+e.target.value; document.getElementById('degMaxV').textContent=(degMax>=_maxDeg?_maxDeg:degMax); applyLinkVis();};
updDegCount();
document.getElementById('hops').onchange=()=>{if(egoOn){const d=id2n.get(egoOn); if(d) egoFocus(d);}};
document.getElementById('tCore').onchange=e=>{const on=e.target.checked;
 node.style('opacity',d=>!on||d.scc?1:.14);
 link.style('opacity',d=>{if(!on)return .75; const s=id2n.get(lerp(d.source)),t=id2n.get(lerp(d.target)); return (s&&t&&s.scc&&t.scc)?.85:.12;});};
document.getElementById('bFit').onclick=fit;
document.getElementById('bReset').onclick=()=>{clearEgo(); soloB=null; document.getElementById('panel').style.display='none';
 NODES.forEach(n=>{n.fx=null;n.fy=null;}); fitted=false; sim.alpha(.5).restart();};
const q=document.getElementById('q'), qres=document.getElementById('qres');
const _norm=s=>(s||'').toLowerCase().replace(/[_/]/g,' ').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
NODES.forEach(d=>{d._lab=_norm(d.label); d._id=_norm(d.id); d._notes=_norm(d.notes);});
let qsel=-1, qhits=[];
function pickHit(d){focusNode(d.id); qres.className=''; q.value='';}
function runSearch(){
 const raw=q.value.trim();
 if(raw.length<2){qres.className=''; qhits=[]; return;}
 const qn=_norm(raw);
 qhits=NODES.map(d=>{const s=Math.max(d._lab.includes(qn)?0.96:0, d._id.includes(qn)?0.9:0, d._notes.includes(qn)?0.55:0); return {d,s};})
  .filter(x=>x.s>=0.3).sort((a,b)=>b.s-a.s).slice(0,12);
 qres.className='on';
 if(!qhits.length){qres.innerHTML='<div class=rnone>No match. Try a partial name.</div>'; return;}
 qsel=0;
 qres.innerHTML=qhits.map((x,i)=>'<div class=ri data-i="'+i+'"><span class=rs>'+Math.round(x.s*100)+'%</span><b>'+x.d.label+'</b> <span class=rm>'+x.d.bucket+'</span></div>').join('');
 Array.from(qres.querySelectorAll('.ri')).forEach(el=>el.onclick=()=>pickHit(qhits[+el.dataset.i].d));
}
q.oninput=runSearch;
q.onkeydown=e=>{if(!qhits.length)return;
 if(e.key==='ArrowDown'){e.preventDefault(); qsel=Math.min(qsel+1,qhits.length-1);}
 else if(e.key==='ArrowUp'){e.preventDefault(); qsel=Math.max(qsel-1,0);}
 else if(e.key==='Enter'){e.preventDefault(); if(qhits[qsel])pickHit(qhits[qsel].d);}
 else if(e.key==='Escape'){q.value=''; runSearch();}
 Array.from(qres.querySelectorAll('.ri')).forEach((el,i)=>el.classList.toggle('sel',i===qsel));};
document.addEventListener('click',e=>{if(!e.target.closest('#hud')) qres.className='';});
document.querySelectorAll('.lg').forEach(el=>el.onclick=()=>{
 const b=el.dataset.b;
 if(soloB===b){soloB=null; clearEgo(); document.querySelectorAll('.lg').forEach(x=>x.classList.remove('off','solo')); return;}
 soloB=b; egoOn=null;
 document.querySelectorAll('.lg').forEach(x=>{x.classList.toggle('solo',x.dataset.b===b); x.classList.toggle('off',x.dataset.b!==b);});
 node.style('opacity',n=>n.bucket===b?1:.05).style('pointer-events',n=>n.bucket===b?null:'none');
 labels.style('display',n=>n.bucket===b&&labVisible(n)?null:'none');
 const vis=l=>{const s=id2n.get(lerp(l.source)),t=id2n.get(lerp(l.target)); return !!(s&&t&&s.bucket===b&&t.bucket===b);};
 link.classed('hl',false).style('display',l=>vis(l)?null:'none').style('opacity',.88);
 linkHit.style('display',l=>vis(l)?null:'none');
 groupG.style('opacity',.15);
});
function fromHash(){const m=/^#node=(.+)$/.exec(location.hash); if(!m)return;
 const id=decodeURIComponent(m[1]); if(sim.alpha()<0.06) focusNode(id); else pendingFocus=id;}
window.addEventListener('hashchange',fromHash); fromHash();
document.getElementById('panel').addEventListener('click',function(e){
 const a=e.target.closest('a[href^="#node="]'); if(!a)return;
 e.preventDefault(); focusNode(decodeURIComponent(a.getAttribute('href').slice(6)));
});
(function(){
 const box=document.getElementById('flk');
 const spec=[
  ['velDecay','friction',0.10,0.90,0.01],
  ['alphaDecay','cool-down',0.005,0.100,0.005],
  ['charge','repulsion',-300,-5,5],
  ['chargeMax','repulsion range',80,800,10],
  ['linkStr','link strength',0,0.60,0.01],
  ['linkDist','link distance',20,140,2],
  ['cohesion','sector cohesion',0,0.80,0.01],
  ['collidePad','collide padding',0,40,1],
  ['collideStr','collide strength',0.10,1.00,0.05],
  ['collideIter','collide iters',1,4,1],
  ['spreadX','sector spread X',0.10,0.60,0.01],
  ['spreadY','sector spread Y',0.10,0.60,0.01]
 ];
 const DEF=Object.assign({},FLK); let deb=null;
 spec.forEach(function(s){
  const k=s[0], row=document.createElement('div'); row.className='row';
  row.innerHTML='<label>'+s[1]+'</label><input type=range min='+s[2]+' max='+s[3]+' step='+s[4]+' value='+FLK[k]+'><span class=v>'+FLK[k]+'</span>';
  const rng=row.querySelector('input'), v=row.querySelector('.v');
  rng.addEventListener('input',function(){FLK[k]=parseFloat(rng.value); v.textContent=rng.value;
    clearTimeout(deb); deb=setTimeout(function(){applyFlk(true);},150);});
  box.appendChild(row);
 });
 const btns=document.createElement('div'); btns.className='btns';
 btns.innerHTML='<button id=flkReset>Reset</button><button id=flkCopy>Copy params</button>';
 box.appendChild(btns);
 document.getElementById('tFlk').addEventListener('change',function(e){box.classList.toggle('on',e.target.checked);});
 document.getElementById('flkReset').addEventListener('click',function(){
  Object.assign(FLK,DEF);
  [].forEach.call(box.querySelectorAll('.row'),function(row,i){const k=spec[i][0],r=row.querySelector('input'); r.value=FLK[k]; row.querySelector('.v').textContent=FLK[k];});
  applyFlk(true);});
 document.getElementById('flkCopy').addEventListener('click',function(){
  const txt=JSON.stringify(FLK); const b=document.getElementById('flkCopy');
  if(navigator.clipboard){navigator.clipboard.writeText(txt).then(function(){b.textContent='Copied!'; setTimeout(function(){b.textContent='Copy params';},1200);});}
  else {prompt('FLK params:',txt);}
 });
})();
</script>
"""


def _md2html(md: str) -> str:
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def inline(t):
        t = esc(t)
        t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        return t

    lines = md.split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            th = "".join(f"<th>{inline(c)}</th>" for c in cells(rows[0]))
            trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells(r)) + "</tr>" for r in rows[2:])
            out.append(f"<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>")
            continue
        if re.match(r"^#{1,6}\s", ln):
            lvl = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{lvl}>{inline(ln.lstrip('#').strip())}</h{lvl}>")
            i += 1
            continue
        if ln.strip() == "":
            i += 1
            continue
        if ln.startswith("- "):
            buf = []
            while i < len(lines) and lines[i].startswith("- "):
                buf.append(inline(lines[i][2:]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{b}</li>" for b in buf) + "</ul>")
            continue
        buf = [ln]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "-", "|")):
            buf.append(lines[i])
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)


CARD_LABELS = {
    "actors-expanded-from-bubblemap": "Actors",
    "apt-state-actors": "State APTs",
    "clear-world-affiliates": "Clear-world",
    "commercial-spyware-and-hacktivism": "Spyware",
    "criminal-enterprise": "Crime",
    "crypto-standards-and-researchers": "Crypto",
    "dual-use-and-accountability": "Dual-use",
    "intel-facilities-capabilities": "Facilities",
    "malware-taxonomy": "Malware",
    "pqc-silicon-tpm-hsm-vaults": "PQC silicon",
    "protectors-and-blue-team": "Blue team",
    "protectors-huntress-mdr": "Huntress",
    "protectors-snyk-appsec": "Snyk",
    "supply-xlight-substrate-lithography": "Lithography",
    "intel-defense-tech-neoprimes": "Neoprimes",
    "intel-iqt-portfolio": "In-Q-Tel",
    "intel-iqt-roster": "IQT roster",
    "intel-xfel-facilities": "XFELs",
    "quantum-builders-modalities": "Builders",
    "quantum-crqc": "CRQC",
    "quantum-supply-chain-chips-minerals": "Supply chain",
    "recurring-targets-and-routes": "Targets",
}


def short_label(stub: str) -> str:
    if stub in CARD_LABELS:
        return CARD_LABELS[stub]
    skip = {
        "from", "and", "the", "vs", "of", "in", "a", "an", "to", "for", "with",
        "on", "expanded", "bubblemap", "catalogs", "catalog", "their", "etc",
    }
    acr = {
        "apt": "APTs", "pqc": "PQC", "crqc": "CRQC", "hndl": "HNDL",
        "tpm": "TPM", "hsm": "HSM", "raas": "RaaS", "iab": "IABs",
    }
    parts = [p for p in stub.replace("_", "-").split("-") if p not in skip]
    parts = parts[:2] if len(parts) > 2 else parts
    return " ".join(acr.get(p, p.capitalize()) for p in parts) or stub


def strip_dup_heading(md: str, title: str) -> str:
    lines = md.splitlines()
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].startswith("# "):
        h = lines[i][2:].strip()
        if h.lower() == title.lower() or title.lower().startswith(h.lower()[:24]) or h.lower().startswith(title.lower()[:24]):
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines) and lines[i].lstrip().startswith("*Layer:"):
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
    return "\n".join(lines[i:])


def build_research(g):
    res = os.path.join(ROOT, "research")
    n = 0
    index_rows = []
    for jpath in sorted(glob.glob(os.path.join(res, "*.json"))):
        stub = os.path.basename(jpath)[:-5]
        doc = json.load(open(jpath, encoding="utf-8"))
        meta = doc.get("metadata") or {}
        title = meta.get("title") or stub
        md_path = os.path.join(res, stub + ".md")
        md = open(md_path, encoding="utf-8").read() if os.path.exists(md_path) else ""
        md = strip_dup_heading(md, title)
        ents = doc.get("entities") or []
        edges = doc.get("edges") or []
        srcs = []
        for e in ents + edges:
            for s in e.get("source") or []:
                if s not in srcs:
                    srcs.append(s)
        etable = "".join(
            f"<tr><td><a href='bubblemap.html#node={html.escape(e.get('name',''))}'>{html.escape(e.get('name',''))}</a></td>"
            f"<td>{html.escape(str(e.get('type','')))}</td>"
            f"<td>{html.escape((e.get('notes') or '')[:240])}</td></tr>"
            for e in ents
        )
        edgetable = "".join(
            f"<tr><td>{html.escape(ed.get('from',''))}</td><td>{html.escape(ed.get('kind',''))}</td>"
            f"<td>{html.escape(ed.get('to',''))}</td><td>{html.escape(ed.get('instrument') or '')}</td>"
            f"<td>{html.escape(ed.get('grade') or '')}</td></tr>"
            for ed in edges
        )
        srclist = "".join(f'<li><a href="{html.escape(s)}">{html.escape(s)}</a></li>' for s in srcs)
        body = f"""
<div class="wrap">
  <div class="kicker">{html.escape(meta.get('theme') or '')} · {html.escape(meta.get('layer') or '')}</div>
  <h1>{html.escape(title)}</h1>
  {_md2html(md) if md else ''}
  <h2>Entities ({len(ents)})</h2>
  <table><thead><tr><th>Name</th><th>Type</th><th>Notes</th></tr></thead><tbody>{etable}</tbody></table>
  <h2>Edges ({len(edges)})</h2>
  <table><thead><tr><th>From</th><th>Kind</th><th>To</th><th>Instrument</th><th>Grade</th></tr></thead>
  <tbody>{edgetable}</tbody></table>
  <h2>Sources</h2>
  <ul>{srclist or '<li>see JSON</li>'}</ul>
  <p class="foot"><a href="research.html">Research index</a> · <a href="bubblemap.html">Bubble map</a></p>
</div>"""
        write(f"r-{stub}.html", title[:80], body, "Research")
        index_rows.append((stub, short_label(stub), len(ents), len(edges), len(srcs)))
        n += 1
    cards = "".join(
        f'<a class="rcard" href="r-{html.escape(s)}.html"><b>{html.escape(lab)}</b>'
        f'<span>{ne} entities · {ed} edges</span></a>'
        for s, lab, ne, ed, ns in index_rows
    )
    body = f"""
<div class="wrap">
  <div class="kicker">Research</div>
  <h1>Subject pages</h1>
  <p class="lede">{n} cited blocks. Short names on the cards; full titles on the pages.</p>
  <div class="rgrid">{cards}</div>
</div>"""
    write("research.html", "Research", body, "Research")
    print(f"  rendered {n} research pages")


def main():
    g = load_graph()
    build_index(g)
    build_dashboard(g)
    build_methodology()
    build_atlas(g)
    build_globe(g)
    build_bubblemap(g)
    build_research(g)
    print("wrote docs/ index dashboard methodology atlas globe bubblemap research")


if __name__ == "__main__":
    main()
