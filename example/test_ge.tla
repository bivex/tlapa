---- MODULE TestGE ----
VARIABLES current_term, msg_term
Init ==
  /\ current_term >= msg_term
====
