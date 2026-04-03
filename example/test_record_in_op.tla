---- MODULE TestRecordInOp ----
VARIABLES node_state, current_term
Op(node, msg) ==
  /\ node_state[node] \in {"a","b"}
  /\ current_term >= msg.term
====
