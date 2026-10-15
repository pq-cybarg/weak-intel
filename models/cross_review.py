#!/usr/bin/env python3
"""cross_review.py — dangling edge endpoints, grade coverage. Writes report/CROSS-REVIEW.md."""
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
g = json.load(open(os.path.join(ROOT, "data", "graph.json"), encoding="utf-8"))
ents = g["entities"]
edges = g["edges"]
dangling = [e for e in edges if e["from"] not in ents or e["to"] not in ents]
grades = Counter(e.get("grade") for e in edges)
kinds = Counter(e.get("kind") for e in edges)
out = ["# Cross-review\n", f"- dangling endpoints: **{len(dangling)}**"]
if dangling:
    out += [f"  - {d['from']} -> {d['to']}" for d in dangling[:20]]
out.append("\n## Edge grades")
for k, v in grades.most_common():
    out.append(f"- {k}: {v}")
out.append("\n## Edge kinds")
for k, v in kinds.most_common():
    out.append(f"- {k}: {v}")
os.makedirs(os.path.join(ROOT, "report"), exist_ok=True)
open(os.path.join(ROOT, "report", "CROSS-REVIEW.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("\n".join(out))
