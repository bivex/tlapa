---- MODULE TestHeaderBullet ----
VARIABLES node_state
HandleRequestVote(node) ==
  /\ node_state[node] = "a"
====
