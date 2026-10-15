# weak.intel — a dual-use map of the cyber / operator landscape

The earnings-bubble analogue for cryptography, APTs, crime, protectors, intelligence
facilities, malware classes, blue-team controls, and cryptographically relevant
quantum computers.

This repo **is** weak.intel. Nested under bubble-map it keeps that subname and
lives at **https://pq-cybarg.github.io/bubble-map/weak.intel/** (site path
`bubble-map/weak.intel`). Source: [pq-cybarg/weak-intel](https://github.com/pq-cybarg/weak-intel).
Parent capital/power graph: [pq-cybarg/bubble-map](https://github.com/pq-cybarg/bubble-map).

**Start here:** [`report/UNMASKING.md`](report/UNMASKING.md)

**Reproduce:**

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
bash run_all.sh
```

## One sentence
The landscape is **one stack with two faces**: the same primitives, vendor products,
and concentration points (identity, mail, VPN, PKI, lawful intercept) are the
recurring targets of APTs and criminals, the product line of blue-team vendors,
and the collection surface of SIGINT — and a **CRQC** is the forcing event that
reprices harvested RSA/ECC ciphertext (**HNDL**) and classical signatures (**TNFL**).

## What is proven vs evidenced vs speculative
- **Proven (runnable):** dual-use door cannot be exclusive (Z3 S2); leak cascade
  violates `Inv_NoCascade` (TLA+); RSA confidentiality ∩ CRQC is UNSAT (Z3 Q2);
  injectable EDR is not a safety invariant (Z3 B2); remainder SAT (AES-256,
  segmentation, ML-KEM).
- **Evidenced:** CISA/MITRE/DOJ/Citizen Lab public record (Salt Typhoon on CALEA
  LI, EternalBlue → WannaCry/NotPetya, APT clusters, RaaS, Pegasus).
- **Speculative (graded, out of proofs):** silent Q-Day concealment; current
  harvest scale; intent.

## Map
After `bash run_all.sh`:

- `docs/index.html` — thesis
- `docs/bubblemap.html` — interactive mesh (ember/ice dual-use rings)
- `docs/dashboard.html` — dual-use, recurring targets, CRQC split, accountability sinks
- `docs/globe.html` — public facilities
- `docs/methodology.html` — honesty rules

## Nested under bubble-map
bubble-map submodules this repo at `weak.intel/` and copies `docs/` to
`docs/weak.intel/` so GitHub Pages serves it as `/bubble-map/weak.intel/`.
The nested tab and pages call themselves **weak.intel**. Attack-layer proofs
stay in this repo; they are not mixed into bubble-map's financial SCC.

## Ideas taken from bubble-map
CALEA backdoor paradox, HNDL + **TNFL**, Shadow Brokers boomerang, weaponize-the-guard
(DoubleAgent/BYOVD), Volt Typhoon as pre-positioning not theft, Lazarus as
revenue-driven state/crime blur, spyware vs device-forensics split, RaaS as
franchise, Unit 8200 alumni pipeline, Pine Gap as allied SIGINT chokepoint.

## License
MIT. Independent research. Not an accusation, not classified disclosure, not legal advice.
