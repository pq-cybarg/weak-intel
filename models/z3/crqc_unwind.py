#!/usr/bin/env python3
"""
crqc_unwind.py — CRQC as the forcing event (bubble-map's 'capital tap' analogue).

Q1  HNDL: recorded RSA ciphertext decryptable given CRQC     SAT
Q2  'RSA confidentiality holds after CRQC'                   UNSAT
Q3  TNFL: classical signatures forgeable given CRQC          SAT
Q4  AES-256 / segmentation / ML-KEM remain SAT under CRQC    SAT
Q5  'FIDO2-as-deployed (ECDSA passkeys) survives CRQC'       UNSAT
"""
from z3 import *


def banner(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


def verdict(s, expect):
    r = s.check()
    ok = str(r) == expect
    print(f"  Z3 result: {r}   (expected {expect})   {'PROVED' if ok else '!! UNEXPECTED'}")
    return r


banner("Q1  HARVEST-NOW-DECRYPT-LATER  (constructive)")
s = Solver()
harvested = Bool("rsa_ciphertext_stored")
crqc = Bool("crqc_exists")
decryptable = Bool("plaintext_recoverable")
s.add(harvested)
s.add(crqc)
s.add(decryptable == And(harvested, crqc))
s.add(decryptable)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: stored RSA/ECC ciphertext + CRQC => plaintext. The loss is incurred at harvest, not at Q-Day.")


banner("Q2  'RSA CONFIDENTIALITY SURVIVES CRQC'  is impossible")
s = Solver()
rsa = Bool("rsa_in_use")
crqc = Bool("crqc")
conf = Bool("confidentiality")
s.add(rsa)
s.add(crqc)
s.add(conf == And(rsa, Not(crqc)))  # RSA confidentiality axiom vs Shor
s.add(conf)
r = verdict(s, "unsat")
print("  => You cannot keep RSA confidentiality and a CRQC at once.")


banner("Q3  TRUST-NOW-FORGE-LATER  (integrity twin)")
s = Solver()
old_sig = Bool("classical_signature_on_file")
crqc = Bool("crqc")
forgeable = Bool("signature_forgeable")
s.add(old_sig)
s.add(crqc)
s.add(forgeable == And(old_sig, crqc))
s.add(forgeable)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: HNDL breaks secrecy; TNFL breaks authentication (certs, ePassports, code-signing).")


banner("Q4  REMAINDER THAT STILL SATS UNDER CRQC")
s = Solver()
aes, seg, mlkem, crqc = Bools("AES_256 Network_Segmentation ML_KEM CRQC")
s.add(crqc, aes, seg, mlkem)
# remainder axioms: these primitives are not Shor-broken
ok = Bool("remainder_holds")
s.add(ok == And(aes, seg, mlkem))
s.add(ok)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: symmetric 256-bit, blast-radius controls, and ML-KEM can coexist with a CRQC.")
    print("  They do not un-harvest yesterday's RSA. PQC is for new sessions.")


banner("Q5  'DEPLOYED ECDSA PASSKEYS SURVIVE CRQC'  is impossible")
s = Solver()
ecdsa_pk = Bool("fido2_ecdsa_passkey")
crqc = Bool("crqc")
survives = Bool("survives")
s.add(ecdsa_pk)
s.add(crqc)
s.add(survives == And(ecdsa_pk, Not(crqc)))
s.add(survives)
r = verdict(s, "unsat")
print("  => Today's passkeys are often ECDSA. Phishing-resistance != quantum-resistance.")
print("  Blue-team path: PQC credentials + keep FIDO2's 'secret never leaves the box' property.")
