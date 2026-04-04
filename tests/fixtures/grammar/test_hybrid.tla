---- MODULE TestHybrid ----
VARIABLES node_state, current_term, messages
HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower","candidate"}
  /\ current_term >= b
  /\ IF a > 0 THEN /\ messages' = messages ELSE messages' = messages
====
