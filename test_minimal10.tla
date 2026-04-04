---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes, NodeState, STRING, BOOLEAN, Nat
VARIABLES x, y, z, w, v, u
Init == /\ x \in ([Nodes -> NodeState])
           /\ y = 1
           /\ z \in ([Nodes -> BOOLEAN])
           /\ v = 2
           /\ w \in ([Nodes -> STRING])
           /\ u = 3
====
