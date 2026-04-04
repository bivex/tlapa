---- MODULE TestTick ----
CONSTANTS Nodes
VARIABLES msg_id, node_state, timers
Tick ==
  /\ msg_id' = msg_id + 1
  /\ timers' = [n \in Nodes | IF n > 0 THEN 1 ELSE 0]
====
