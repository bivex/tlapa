---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes, NodeState, STRING, BOOLEAN
VARIABLES x, y, z
Init == /\ x \in ([Nodes -> NodeState])
           /\ y \in ([Nodes -> STRING])
           /\ z \in ([Nodes -> BOOLEAN])
====
