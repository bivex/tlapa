---- MODULE TestExact ----
CONSTANTS Nodes, NodeState
VARIABLES node_state
Init ==
  /\ node_state \in [Nodes -> NodeState]
====
