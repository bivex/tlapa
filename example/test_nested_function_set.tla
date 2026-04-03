---- MODULE TestNested ----
CONSTANTS Nodes, NodeState, BOOLEAN
VARIABLES x
Init ==
  /\ x \in [Nodes -> [NodeState -> BOOLEAN]]
====
