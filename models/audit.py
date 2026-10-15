#!/usr/bin/env python3
"""audit.py — JSON validity, coverage, dual-use counts. Writes report/AUDIT.md."""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def J(p):
    try:
        return json.load(open(os.path.join(ROOT, "data", p), encoding="utf-8"))
    except Exception:
        return {}


g = J("graph.json")
an = g.get("analysis") or {}
out = ["# Consistency & Coverage Audit\n"]
out.append("Canonical numbers (from data/graph.json):\n")
out.append(f"- entities = **{an.get('n_entities')}**")
out.append(f"- edges = **{an.get('n_edges')}**")
out.append(f"- dual-use = **{len(an.get('dual_use_nodes') or [])}**")
out.append(f"- core SCC = **{an.get('core_scc_size')}**")
out.append(f"- CRQC-fragile = **{len(an.get('crqc_fragile') or [])}**")

nres = len(glob.glob(os.path.join(ROOT, "research", "*.json")))
nmd = len(glob.glob(os.path.join(ROOT, "research", "*.md")))
out += ["\n## Inventory", f"- research json: {nres} / md: {nmd}"]

bad = []
for f in glob.glob(os.path.join(ROOT, "research", "*.json")) + glob.glob(os.path.join(ROOT, "data", "*.json")):
    try:
        json.load(open(f, encoding="utf-8"))
    except Exception as e:
        bad.append(os.path.basename(f) + ": " + str(e))
out += ["\n## JSON validity", ("- ALL VALID" if not bad else "\n".join("- BAD " + b for b in bad))]

legs = {
    "crypto": "crypto-standards",
    "apt": "apt-state",
    "criminal": "criminal-enterprise",
    "malware": "malware-taxonomy",
    "blue-team": "protectors-and-blue",
    "facilities": "intel-facilities",
    "dual-use": "dual-use-and-accountability",
    "quantum": "quantum-crqc",
    "targets": "recurring-targets",
    "spyware": "commercial-spyware",
    "clear-world": "clear-world-affiliates",
}
out.append("\n## Leg coverage")
for leg, stub in legs.items():
    present = bool(glob.glob(os.path.join(ROOT, "research", stub + "*")))
    out.append(f"- {leg}: {'yes' if present else 'MISSING'}")

nosrc = []
for f in glob.glob(os.path.join(ROOT, "research", "*.json")):
    txt = open(f, encoding="utf-8").read()
    if '"source"' not in txt:
        nosrc.append(os.path.basename(f))
out.append("\n## Research files lacking any source field")
out.append("- none" if not nosrc else "\n".join("- " + x for x in nosrc))

os.makedirs(os.path.join(ROOT, "report"), exist_ok=True)
open(os.path.join(ROOT, "report", "AUDIT.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
