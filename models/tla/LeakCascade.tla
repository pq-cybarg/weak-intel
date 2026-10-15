------------------------------ MODULE LeakCascade ------------------------------
EXTENDS Naturals
(*
  Shadow Brokers analogue: a hoarded 0-day leaks, then two independent
  operators weaponize it. Inv_NoCascade is expected VIOLATED.
*)
VARIABLES leaked, wannacry, notpetya
vars == <<leaked, wannacry, notpetya>>

TypeOK == leaked \in BOOLEAN /\ wannacry \in BOOLEAN /\ notpetya \in BOOLEAN

Init == leaked = FALSE /\ wannacry = FALSE /\ notpetya = FALSE

Leak == /\ leaked = FALSE
        /\ leaked' = TRUE
        /\ UNCHANGED <<wannacry, notpetya>>

Worm1 == /\ leaked = TRUE
         /\ wannacry = FALSE
         /\ wannacry' = TRUE
         /\ UNCHANGED <<leaked, notpetya>>

Worm2 == /\ leaked = TRUE
         /\ notpetya = FALSE
         /\ notpetya' = TRUE
         /\ UNCHANGED <<leaked, wannacry>>

Next == Leak \/ Worm1 \/ Worm2
Spec == Init /\ [][Next]_vars

Inv_NoCascade == ~(wannacry /\ notpetya)

=============================================================================
