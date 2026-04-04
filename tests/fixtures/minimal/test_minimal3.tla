---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes, NodeState
VARIABLES x, y
Init == /\ x \in ([Nodes -> NodeState])
           /\ y = 1
====
