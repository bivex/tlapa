---- MODULE TestIfRecord ----
VARIABLES current_term, msg
Init ==
  /\ IF current_term > msg.term THEN current_term' = current_term ELSE current_term' = current_term
====
