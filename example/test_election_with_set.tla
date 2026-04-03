---- MODULE TestElectionWithSet ----
VARIABLES node_state, current_term
ElectionTimeout(node) ==
  /\ node_state[node] = "follower"
  /\ current_term \in {1,2,3}
====
