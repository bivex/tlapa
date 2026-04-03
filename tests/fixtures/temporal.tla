---- MODULE TestTemporal ----
EXTENDS Naturals

VARIABLE x

Init == x = 0

Next == x' = x + 1

Spec == Init /\ [][Next]_x

AlwaysSafe == [] (x >= 0)

EventuallyTrue == <> (x >= 0)

WF_Fair == WF_vars(x)
SF_Fair == SF_vars(x)

TempSpec == /\ \A n \in Nat: [] (x >= 0)

LiveTemp == \EE n \in Nat: <> (x > n)
====
