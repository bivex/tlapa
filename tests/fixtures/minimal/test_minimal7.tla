---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes
VARIABLES x, y
Init == /\ x \in ([Nodes -> [1 -> 2]])
           /\ y = 1
====
