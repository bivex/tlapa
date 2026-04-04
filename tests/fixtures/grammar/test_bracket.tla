---- MODULE TestBracket ----
VARIABLES x
Init ==
  x = 1
  /\ y \in [A -> B]
====
