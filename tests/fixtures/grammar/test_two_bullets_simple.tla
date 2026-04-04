---- MODULE TestTwoBullets ----
CONSTANTS Nodes, NodeState
VARIABLES x, y
Init ==
  /\ x \in Nodes
  /\ y \in NodeState
====
