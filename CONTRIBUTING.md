# Contributing & How to Verify

Core claims are reproducible. You don't have to trust the prose — run it.

```bash
python3 -m pip install -r requirements.txt
bash run_all.sh
python3 -m unittest discover -s tests -v
```

## Engines
- `models/z3/shared_substrate.py` — dual-use door, exclusivity UNSAT, EDR injectability
- `models/z3/crqc_unwind.py` — HNDL / TNFL / remainder
- `models/tla/LeakCascade.tla` — EternalBlue-style cascade
- `models/alloy/DualUse.als` — relational dual-use
- `models/graph/build_graph.py` — SCC, dual-use, recurring targets

## Rules
1. Cite primary sources (CISA, MITRE, indictments, declassified reporting).
2. Grade speculation. Never infer intent from adjacency.
3. Re-review on every new `research/*.json`: `bash scripts/new-research.sh`
4. No personal identifying information in commits, files, or metadata.
   This is a pseudonymous project (same identity as bubble-map: pq-cybarg).
   Use a throwaway identity. Do not add names, emails, real-world locations,
   local filesystem paths, or session transcripts.

## License
MIT.
