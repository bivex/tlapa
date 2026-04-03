---- MODULE TestHRV ----
EXTENDS Naturals
VARIABLES node_state, current_term, messages
HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower","candidate"}
  /\ current_term >= msg.term
  /\ IF current_term > msg.term THEN
       /\ messages' = messages
     ELSE
       IF TRUE THEN
         /\ messages' = messages
====
