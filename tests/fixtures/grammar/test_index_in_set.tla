---- MODULE TestIndexInSet ----
VARIABLES node_state
Init ==
  /\ node_state[x] \in {"a","b"}
====
