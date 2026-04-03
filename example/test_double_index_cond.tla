---- MODULE TestDoubleIndexCond ----
VARIABLES voted_for, node_state
F(node, msg) ==
  /\ IF voted_for[node][msg.from] THEN node_state[node] = "a" ELSE node_state[node] = "b"
====
