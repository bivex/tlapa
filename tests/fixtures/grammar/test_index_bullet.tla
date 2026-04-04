---- MODULE TestIndexBullet ----
VARIABLES node_state
Init ==
  /\ node_state[node] = "follower"
====
