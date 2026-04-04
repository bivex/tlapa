---- MODULE TestWrongBar ----
CONSTANTS Nodes
VARIABLES timers
Tick ==
  /\ timers' = [n \in Nodes | n > 0]
====
