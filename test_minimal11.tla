---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes, NodeState, STRING, MaxLogSize, LogEntry
VARIABLES x, y, z, w
LogEntry == [term: Nat, command: STRING]
Init == /\ x \in ([Nodes -> NodeState])
           /\ y \in ([Nodes -> [1 -> 2]])
           /\ z \in ([Nodes -> STRING])
           /\ w = 1
====
