---- MODULE TestFixture ----
EXTENDS Naturals

VARIABLES x, y

Init == /\ x = 0
        /\ y = 0

Next == /\ x' = x + 1
        /\ y' = y + x

Spec == Init /\ [][Next]_<<x, y>>

Inv == x >= 0 /\ y >= 0

THEOREM Spec => []Inv
====
