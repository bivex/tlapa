---- MODULE TestRecordField ----
VARIABLES msg, current_term
Init ==
  /\ current_term >= msg.term
====
