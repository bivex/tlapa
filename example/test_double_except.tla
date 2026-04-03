---- MODULE TestDoubleExcept ----
VARIABLES voted_for
Update ==
  voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]
====
