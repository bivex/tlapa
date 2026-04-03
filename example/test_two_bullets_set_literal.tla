---- MODULE TestTwoBulletsSetLiteral ----
CONSTANTS Nodes, NodeState
VARIABLES x, y
Init ==
  /\ x \in [Nodes -> NodeState]
  /\ y = {}
====
