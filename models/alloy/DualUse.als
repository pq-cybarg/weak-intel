module DualUse

abstract sig Node {}
sig Actor, System, Vendor, Control, Method extends Node {}

sig Targets { src: Actor, dst: Node }
sig Protects { src: Node, dst: Node }
sig Exploits { src: Node, dst: Node }
sig DualDoor { n: Node }

pred vendorIsAlsoTarget {
  some v: Vendor | some t: Targets | t.dst = v
}

pred dualDoorExists {
  some DualDoor
}

pred recurringSystem {
  some s: System | #{ t: Targets | t.dst = s } >= 2
}

run dualDoor { dualDoorExists } for 8
run recurring { recurringSystem } for 8
run vendorTarget { vendorIsAlsoTarget } for 8
