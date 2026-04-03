---- MODULE TestNestedIf ----
VARIABLES x
F(a) ==
  /\ IF a = 1 THEN 2 ELSE 3
====
