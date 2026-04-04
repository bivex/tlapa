---- MODULE TestStringSet ----
VARIABLES node_state
ElectionTimeout(node) ==
  /\ node_state[node] \in {"follower","candidate"}
====
