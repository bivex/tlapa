---- MODULE TestElectionSimple ----
VARIABLES node_state
ElectionTimeout(node) ==
  /\ node_state[node] = "follower"
====
