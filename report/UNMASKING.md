# Unmasking the dual-use stack
### A formally-checked map of the cyber / operator landscape

*Compiled 2026-09-04. Every material node cites a file in `research/` (which carries source URLs).
The structural core is machine-checked (Z3, TLA+, Alloy, graph SCC). Attribution and
“got away with” are evidence-graded. Intent is never inferred from adjacency.*

---

## 0. The one-sentence unmasking
**The cyber landscape is a single dual-use stack: the same cryptographic primitives,
vendor products, and concentration points (identity, mail, VPN, PKI, lawful intercept)
are the recurring targets of APTs and criminals, the product of blue-team vendors,
and the collection surface of SIGINT — and a cryptographically relevant quantum
computer is the forcing event that reprices every recorded RSA/ECC ciphertext
(harvest-now-decrypt-later) and every classical signature (trust-now-forge-later),
while isolation, AES-256, and post-quantum migration remain the SAT remainder.**

We prove the structural half. We evidence-grade the rest. We do not yet know the
human story this mesh wants to tell at every scale — that is the point of studying it.

---

## 0b. Headline findings

**1. The dual-use door (S1 SAT, S2 UNSAT).**
A mandated access channel that exists for an intended user cannot be proven exclusive.
The empirical overlay is Salt Typhoon on CALEA lawful-intercept systems at US carriers
(CISA). Historical overlays: Dual_EC in NIST SP 800-90; Crypto AG / Operation Rubicon
(WaPo/ZDF 2020). Same theorem, three decades.

**2. Leak and boomerang (TLA+ `Inv_NoCascade` VIOLATED).**
Hoarded 0-days are dual-use in time. EternalBlue left a stockpile and returned as
WannaCry (Lazarus, public US/UK attribution) and NotPetya (Sandworm/GRU, public
US/UK attribution). The identity of the Shadow Brokers is unresolved and marked as such.

**3. Weaponize the guard (B2 UNSAT).**
“EDR is running” is not a safety invariant if the process is injectable (DoubleAgent)
or the kernel is taken via a signed vulnerable driver (BYOVD / EDR-killers). The
blue-team remainder is PPL on security services, the driver blocklist (lagging),
and identity-isolated backups.

**4. Recurring targets are concentration, not coincidence.**
Active Directory, Exchange, edge VPN, helpdesk-reset, SMBv1, software-update trust,
telecom LI, MOVEit-class file transfer, ICS, mobile messaging. Crime and APT meet
here because the stack is shared, not because they held a meeting.

**5. CRQC as the unwind (Q1-Q5) - and it is not one blob.**
HNDL / TNFL still hold. The map now splits CRQC into modalities (superconducting,
trapped-ion, photonic, neutral-atom, topological, annealing-as-non-path), builders
(IonQ, Quantinuum, IBM, Google, PsiQuantum, QuEra, Origin Quantum, USTC...), PQC
silicon (Infineon/NXP/ST/Thales/Entrust/PQShield vs SEALSQ narrative-beta), TPM/SE
(TPM2 is RSA/ECC until migrated), HSMs/vaults, and the physical gates (GlobalFoundries
photonic wafers, Bluefors fridges, helium-3, ASML/Zeiss, China REE). A CRQC is a
supply-chain event, not a ticker.

**6. Accountability is uneven.**
Got away (delayed exposure): Dual_EC, Crypto AG, the CALEA door before Salt Typhoon.
Did not: APT1 naming, Emotet/QakBot disruptions, DarkSide clawback, Vault 7, Snake/MEDUSA,
Equation-class tooling via Shadow Brokers. LockBit’s *brand* surviving Cronos is graded
moderate — infrastructure seizure ≠ ecosystem death.

---

## 1. How to read the map
Gold ring = operational strongly-connected core. Ice dashed + ember stroke = dual-use
node (protector and target, or an explicit door). Green edges = `protects`.
Criminal vs clear-world is an edge with a grade, not a smear. Commercial spyware
(covert implant) is kept distinct from device forensics (physical custody).

---

## 2. What we still do not know
The macro story (who the landscape is *for*) and the micro stories (one operator,
one year, one system) are not yet a single narrative. That is the research program.
Silent Q-Day — the first CRQC owner’s incentive not to announce — is labeled
speculative and kept out of the solvers.

---

Independent research. Public records. Corrections welcome. Not legal advice.
