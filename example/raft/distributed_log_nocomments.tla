---- MODULE DistributedLogNoComments ----
EXTENDS Naturals
VARIABLES x
Init == x = 0
Next == x' = x + 1
Spec == Init /\ [][Next]_<<x>>
====
