---- MODULE TestNestedIfBranches ----
VARIABLES x
F(a) ==
  /\ IF a = 1 THEN
       /\ x = 1
     ELSE
       IF a = 2 THEN
         /\ x = 2
       ELSE
         /\ x = 3
====
