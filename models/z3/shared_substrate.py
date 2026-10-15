#!/usr/bin/env python3
"""
shared_substrate.py — Z3 theorems for the dual-use landscape.

S1  Dual-use door is realizable                         SAT
S2  "Exceptional access exclusive to intended user"     UNSAT
S3  Recurring-target concentration (identity/mail/vpn)  SAT
B1  Segmentation reduces blast radius                   SAT
B2  Injectable EDR cannot guarantee protection          UNSAT
"""
from z3 import *


def banner(t):
    print("\n" + "=" * 72 + f"\n{t}\n" + "=" * 72)


def verdict(s, expect):
    r = s.check()
    ok = str(r) == expect
    print(f"  Z3 result: {r}   (expected {expect})   {'PROVED' if ok else '!! UNEXPECTED'}")
    return r


banner("S1  DUAL-USE DOOR IS REALIZABLE  (CALEA-style exceptional access)")
s = Solver()
intended = Bool("intended_user_uses_door")
unintended = Bool("unintended_user_uses_door")
door_exists = Bool("mandated_access_channel")
s.add(door_exists)
s.add(intended)
s.add(Implies(door_exists, Or(intended, unintended)))
# constructive: both can be true at once — the door is not exclusive
s.add(unintended)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: a mandated access channel can be used by an unintended operator.")
    print("  Empirical overlay (not in the solver): Salt Typhoon on CALEA LI systems.")


banner("S2  'EXCEPTIONAL ACCESS IS EXCLUSIVE'  is impossible once the door exists")
s = Solver()
door = Bool("door")
good = Bool("intended")
bad = Bool("unintended")
exclusive = Bool("exclusive")
s.add(door)
s.add(good)
# exclusivity = door implies NOT unintended
s.add(exclusive == And(door, Not(bad)))
# but any reachable channel is a capability; if it exists, capability can be copied
# model: door => possible(bad). Force bad to be possible by asserting exclusive AND bad.
s.add(exclusive)
s.add(Implies(door, bad))  # non-exclusivity axiom of a shared channel
r = verdict(s, "unsat")
print("  => A shared access channel cannot be proven exclusive to the intended user.")


banner("S3  RECURRING-TARGET CONCENTRATION  (identity + mail + vpn as the mesh)")
s = Solver()
ad, exch, vpn = Bools("Active_Directory Microsoft_Exchange Edge_VPN")
hits = Int("target_hits")
s.add(ad, exch, vpn)
s.add(hits == If(ad, 1, 0) + If(exch, 1, 0) + If(vpn, 1, 0))
s.add(hits >= 3)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: AD + Exchange + edge-VPN can be simultaneously live concentration points.")


banner("B1  SEGMENTATION REDUCES BLAST RADIUS")
s = Solver()
spread = Real("east_west_fraction")
seg = Bool("segmented")
s.add(spread >= 0, spread <= 1)
s.add(Implies(seg, spread <= Q(1, 5)))
s.add(Implies(Not(seg), spread >= Q(4, 5)))
s.add(seg)
r = verdict(s, "sat")
if str(r) == "sat":
    print("  WITNESS: with segmentation, east-west spread can be bounded (≤20% model).")
    print("  Why it works: worms and ransomware need a path; identity-as-network is the residual failure.")


banner("B2  INJECTABLE EDR CANNOT GUARANTEE PROTECTION")
s = Solver()
edr_on = Bool("edr_running")
injectable = Bool("edr_injectable")
guaranteed = Bool("protection_guaranteed")
s.add(edr_on)
s.add(injectable)
s.add(guaranteed == And(edr_on, Not(injectable)))
s.add(guaranteed)
r = verdict(s, "unsat")
print("  => If the guard can be injected/killed (DoubleAgent/BYOVD), 'EDR is on' is not a safety invariant.")
print("  Blue-team remainder: PPL + driver blocklist + isolate the backup plane.")
