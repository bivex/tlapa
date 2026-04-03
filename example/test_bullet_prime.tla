---- MODULE TestBulletPrime ----
VARIABLES x, y
Init ==
  /\ x' = x + 1
  /\ y = 2
====
