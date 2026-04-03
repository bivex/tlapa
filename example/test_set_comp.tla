---- MODULE TestSetComp ----
VARIABLES x, y
Init ==
  x = { [type |-> "A"] : n \in Nat, n > 1 }
====
