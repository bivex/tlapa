---- MODULE TestCombo ----
VARIABLES node_state, current_term, messages
Op(a,b) ==
  /\ node_state[a] \in {"x","y"}
  /\ current_term >= b
  /\ IF a > 0 THEN /\ messages' = messages ELSE messages' = messages
====
