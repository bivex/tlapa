---- MODULE TestTwoBulletsMixed ----
CONSTANTS Nodes, NodeState
VARIABLES x, y
Init ==
  /\ x \in Nodes
  /\ y \in [Nodes -> NodeState]
====
