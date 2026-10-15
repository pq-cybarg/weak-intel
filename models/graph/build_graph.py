#!/usr/bin/env python3
"""
build_graph.py — consolidate research/*.json into one dual-use landscape graph.

Analysis (stdlib):
  - alias-free entity merge
  - directed edges with kind/grade
  - Tarjan SCCs (the formal 'loop' in the operator mesh)
  - dual-use nodes: protect AND get targeted / explicit dual_use
  - recurring targets: in-degree of targets|exploits|route
  - CRQC fragile vs surviving
  - got-away vs did-not

Outputs: data/graph.json, data/entities.csv, data/edges.csv
"""
from __future__ import annotations

import csv
import glob
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RES = os.path.join(ROOT, "research")
DATA = os.path.join(ROOT, "data")
os.makedirs(DATA, exist_ok=True)

BUCKET_OF = {
    "apt": "actor",
    "criminal": "actor",
    "malware": "malware",
    "researcher": "people",
    "person": "people",
    "university": "people",
    "standard": "crypto",
    "method": "crypto",
    "vendor": "protectors",
    "agency": "intel",
    "facility": "intel",
    "system": "targets",
    "control": "blue",
    "quantum": "quantum",
    "affiliate": "clear",
    "capability": "capability",
    "target": "targets",
}

# Headline core = SCC over ATTACK/DOOR edges only (bubble-map's "financial layer").
# Mixing affiliation/capability edges into "the core" is the composition fallacy
# the earnings-bubble graph forbids.
ATTACK = {"targets", "exploits", "route", "harvests", "dual_use"}
CAPABILITY = {"uses", "has_capability"}
OVERLAY = {
    "affiliates", "hosted_at", "standardizes", "authored", "attributed_to",
    "protects", "got_away", "did_not_get_away", "survives_crqc", "dies_under_crqc",
}


def load_blocks():
    blocks = []
    for path in sorted(glob.glob(os.path.join(RES, "*.json"))):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        doc["_file"] = os.path.basename(path)
        blocks.append(doc)
    return blocks


def merge(blocks):
    ents = {}
    edges = []
    for b in blocks:
        src_file = b["_file"]
        meta = b.get("metadata") or {}
        for e in b.get("entities") or []:
            name = e.get("name")
            if not name:
                continue
            rec = ents.setdefault(name, {
                "id": name,
                "type": e.get("type") or "capability",
                "notes": [],
                "sources": [],
                "lat": None,
                "lon": None,
                "capability_tier": None,
                "files": [],
            })
            rec["type"] = e.get("type") or rec["type"]
            rec["bucket"] = e.get("bucket") or BUCKET_OF.get(rec["type"], "other")
            if e.get("notes"):
                rec["notes"].append(e["notes"])
            if e.get("lat") is not None:
                rec["lat"] = e["lat"]
                rec["lon"] = e.get("lon")
            if e.get("capability_tier"):
                rec["capability_tier"] = e["capability_tier"]
            for s in e.get("source") or []:
                rec["sources"].append(s)
            rec["files"].append(src_file)
        for ed in b.get("edges") or []:
            a, c = ed.get("from"), ed.get("to")
            if not a or not c:
                continue
            for n in (a, c):
                if n not in ents:
                    ents[n] = {
                        "id": n, "type": "capability", "bucket": "other",
                        "notes": [], "sources": [], "lat": None, "lon": None,
                        "capability_tier": None, "files": [src_file],
                    }
            kind = ed.get("kind") or "affiliates"
            if kind in ATTACK:
                elayer = "attack"
            elif kind in CAPABILITY:
                elayer = "capability"
            else:
                elayer = "overlay"
            edges.append({
                "from": a, "to": c,
                "kind": kind,
                "instrument": ed.get("instrument") or "",
                "confidence": ed.get("confidence") or "moderate",
                "status": ed.get("status") or "public-record",
                "grade": ed.get("grade") or "moderate",
                "notes": ed.get("notes") or "",
                "source": ed.get("source") or [],
                "source_file": src_file,
                "theme": meta.get("theme"),
                "research_layer": meta.get("layer"),
                "layer": elayer,
            })
    for rec in ents.values():
        rec["notes"] = " | ".join(dict.fromkeys(rec["notes"]))[:800]
        rec["sources"] = list(dict.fromkeys(rec["sources"]))
        rec["files"] = list(dict.fromkeys(rec["files"]))
        rec["bucket"] = rec.get("bucket") or BUCKET_OF.get(rec["type"], "other")
    return ents, edges


def tarjan(nodes, edges):
    index = 0
    stack = []
    idx, low, on = {}, {}, set()
    sccs = []
    adj = defaultdict(list)
    for e in edges:
        adj[e["from"]].append(e["to"])

    def strong(v):
        nonlocal index
        idx[v] = low[v] = index
        index += 1
        stack.append(v)
        on.add(v)
        for w in adj.get(v, []):
            if w not in idx:
                strong(w)
                low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = stack.pop()
                on.discard(w)
                comp.append(w)
                if w == v:
                    break
            sccs.append(comp)

    for n in nodes:
        if n not in idx:
            strong(n)
    return [c for c in sccs if len(c) > 1]


def wcc(nodes, edges):
    parent = {n: n for n in nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for e in edges:
        if e["from"] in parent and e["to"] in parent:
            union(e["from"], e["to"])
    comps = defaultdict(list)
    for n in nodes:
        comps[find(n)].append(n)
    ranked = sorted(comps.values(), key=len, reverse=True)
    cid = {}
    for i, c in enumerate(ranked):
        for n in c:
            cid[n] = i
    return ranked, cid


def articulation_points(nodes, edges):
    adj = defaultdict(set)
    for e in edges:
        if e["from"] in nodes and e["to"] in nodes:
            adj[e["from"]].add(e["to"])
            adj[e["to"]].add(e["from"])
    time = 0
    disc, low, parent, ap = {}, {}, {}, set()

    def dfs(u):
        nonlocal time
        children = 0
        disc[u] = low[u] = time
        time += 1
        for v in adj[u]:
            if v not in disc:
                parent[v] = u
                children += 1
                dfs(v)
                low[u] = min(low[u], low[v])
                if parent.get(u) is None and children > 1:
                    ap.add(u)
                if parent.get(u) is not None and low[v] >= disc[u]:
                    ap.add(u)
            elif v != parent.get(u):
                low[u] = min(low[u], disc[v])

    for n in nodes:
        if n not in disc and adj[n]:
            dfs(n)
    return sorted(ap)


def analyze(ents, edges):
    names = list(ents)
    deg_in, deg_out = defaultdict(int), defaultdict(int)
    kinds_in, kinds_out = defaultdict(set), defaultdict(set)
    for e in edges:
        deg_out[e["from"]] += 1
        deg_in[e["to"]] += 1
        kinds_out[e["from"]].add(e["kind"])
        kinds_in[e["to"]].add(e["kind"])

    dual = []
    for n, rec in ents.items():
        protects = "protects" in kinds_out[n]
        targeted = bool({"targets", "exploits", "route"} & kinds_in[n])
        explicit = "dual_use" in kinds_out[n] or "dual_use" in kinds_in[n]
        if explicit or (protects and targeted):
            dual.append(n)

    recurring = []
    for n, rec in ents.items():
        tdeg = sum(1 for e in edges if e["to"] == n and e["kind"] in ("targets", "exploits", "route"))
        if tdeg >= 2 or rec["type"] == "system":
            recurring.append({"id": n, "target_in": tdeg, "type": rec["type"]})
    recurring.sort(key=lambda x: -x["target_in"])

    fragile, survive = set(), set()
    for e in edges:
        if e["kind"] == "dies_under_crqc":
            victim = e["to"] if e["from"] in ("CRQC", "Peter_Shor") else e["from"]
            if victim not in ("CRQC", "Peter_Shor"):
                fragile.add(victim)
        if e["kind"] == "survives_crqc":
            survive.add(e["from"] if e["to"] == "CRQC" else e["to"])

    got, notgot = [], []
    for e in edges:
        if e["kind"] == "got_away" or e["to"] == "got_away":
            got.append(e["from"])
        if e["kind"] == "did_not_get_away" or e["to"] == "did_not_get_away":
            notgot.append(e["from"])

    atk = [e for e in edges if e.get("layer") == "attack"]
    cap = [e for e in edges if e.get("layer") == "capability"]
    ovl = [e for e in edges if e.get("layer") == "overlay"]
    atk_robust = [e for e in atk if e.get("grade") in ("fact", "strong")]

    sccs_atk = tarjan(names, atk)
    sccs_atk.sort(key=len, reverse=True)
    sccs_rob = tarjan(names, atk_robust)
    sccs_rob.sort(key=len, reverse=True)
    sccs_cap = tarjan(names, cap)
    sccs_cap.sort(key=len, reverse=True)
    sccs_ovl = tarjan(names, ovl)
    sccs_ovl.sort(key=len, reverse=True)
    sccs_all = tarjan(names, edges)
    sccs_all.sort(key=len, reverse=True)

    # Headline core: UNION of attack-layer SCCs (size>=2). Empty is a valid result.
    core = set()
    for c in sccs_atk:
        core |= set(c)
    core_robust = set()
    for c in sccs_rob:
        core_robust |= set(c)
    overlay_only = set()
    for c in sccs_all:
        overlay_only |= set(c)
    overlay_only -= core

    wccs, wcc_id = wcc(names, edges)
    isolates = [c[0] for c in wccs if len(c) == 1]
    chokepoints = articulation_points(names, atk if atk else edges)

    def bscore(n):
        neigh = set()
        for e in edges:
            if e["from"] == n:
                neigh.add(ents.get(e["to"], {}).get("bucket"))
            if e["to"] == n:
                neigh.add(ents.get(e["from"], {}).get("bucket"))
        return len(neigh - {None}) + deg_in[n] + deg_out[n]

    connectors = sorted(names, key=bscore, reverse=True)[:18]

    for n, rec in ents.items():
        rec["deg"] = deg_in[n] + deg_out[n]
        rec["deg_in"] = deg_in[n]
        rec["deg_out"] = deg_out[n]
        rec["dual_use"] = n in dual
        rec["scc_core"] = n in core
        rec["scc_robust"] = n in core_robust
        rec["crqc_fragile"] = n in fragile
        rec["crqc_survives"] = n in survive
        rec["wcc_id"] = wcc_id.get(n, -1)
        rec["wcc_size"] = len(wccs[wcc_id[n]]) if n in wcc_id else 1
        rec["isolate"] = rec["wcc_size"] <= 1
        rec["chokepoint"] = n in chokepoints
        rec["connector"] = n in connectors

    return {
        "n_entities": len(ents),
        "n_edges": len(edges),
        "n_attack": len(atk),
        "n_capability": len(cap),
        "n_overlay": len(ovl),
        "core_scc": sorted(core),
        "core_scc_size": len(core),
        "core_scc_robust": sorted(core_robust),
        "core_scc_robust_size": len(core_robust),
        "sccs_attack": sccs_atk,
        "sccs_capability": sccs_cap,
        "sccs_overlay": sccs_ovl,
        "sccs_all": sccs_all,
        "nodes_only_in_all_edges_scc": sorted(overlay_only),
        "dual_use_nodes": sorted(set(dual)),
        "recurring_targets": recurring[:40],
        "crqc_fragile": sorted(fragile),
        "crqc_survives": sorted(survive),
        "got_away": sorted(set(got)),
        "did_not_get_away": sorted(set(notgot)),
        "wcc_sizes": [len(c) for c in wccs[:12]],
        "n_isolates": len(isolates),
        "chokepoints": chokepoints,
        "connectors": connectors,
    }


def main():
    blocks = load_blocks()
    ents, edges = merge(blocks)
    analysis = analyze(ents, edges)
    graph = {
        "as_of": "2026-09-04",
        "project": "Weak.Intel",
        "entities": ents,
        "edges": edges,
        "analysis": analysis,
        "blocks": [b["_file"] for b in blocks],
    }
    with open(os.path.join(DATA, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    with open(os.path.join(DATA, "entities.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "type", "bucket", "deg", "dual_use", "scc_core", "crqc_fragile", "tier"])
        for rec in sorted(ents.values(), key=lambda r: -r["deg"]):
            w.writerow([rec["id"], rec["type"], rec["bucket"], rec["deg"],
                        int(rec["dual_use"]), int(rec["scc_core"]), int(rec["crqc_fragile"]),
                        rec.get("capability_tier") or ""])
    with open(os.path.join(DATA, "edges.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["from", "to", "kind", "layer", "instrument", "grade", "confidence", "file"])
        for e in edges:
            w.writerow([e["from"], e["to"], e["kind"], e.get("layer"), e["instrument"], e["grade"], e["confidence"], e["source_file"]])

    an = analysis
    print(f"entities {an['n_entities']}  edges {an['n_edges']}  attack {an['n_attack']} cap {an['n_capability']} overlay {an['n_overlay']}")
    print(f"[S0] attack-layer SCCs (headline core, no fallback): {an['core_scc_size']} nodes in {len(an['sccs_attack'])} cycle(s)")
    if an['core_scc']:
        print("     " + ", ".join(an['core_scc'][:24]))
    else:
        print("     (empty - no directed cycle on targets/exploits/route/harvests/dual_use)")
    print(f"[S0b] robust (fact|strong only): {an['core_scc_robust_size']}")
    print(f"[S0c] all-edges cycles extra (NOT the core): {len(an['nodes_only_in_all_edges_scc'])} {', '.join(an['nodes_only_in_all_edges_scc'][:16])}")
    print(f"WCC sizes {an['wcc_sizes']}  isolates {an['n_isolates']}  attack chokepoints {an['chokepoints'][:12]}")
    print(f"dual-use (protects AND targeted, or explicit door) ({len(an['dual_use_nodes'])}): {', '.join(an['dual_use_nodes'][:16])}")
    print("recurring targets:")
    for t in an["recurring_targets"][:12]:
        print(f"  {t['id']:28} in={t['target_in']}  type={t['type']}")
    print(f"CRQC-fragile: {', '.join(an['crqc_fragile'])}")
    print(f"CRQC-survives: {', '.join(an['crqc_survives'])}")
    print(f"got away: {', '.join(an['got_away'])}")
    print(f"did not: {', '.join(an['did_not_get_away'])}")


if __name__ == "__main__":
    main()
