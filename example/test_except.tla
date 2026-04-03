---- MODULE TestExcept ----
VARIABLES node_state
Assume(node_state) ==
  node_state' = [node_state EXCEPT ![node] = "candidate"]
====
