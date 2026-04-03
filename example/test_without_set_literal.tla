---- MODULE TestNoSetLiteral ----
CONSTANTS Nodes, NodeState, STRING, Nat, BOOLEAN, MaxLogSize, LogEntry
VARIABLES x, y, z, w, v, u, m, n, p
Init ==
  /\ x \in [Nodes -> NodeState]
  /\ y \in [Nodes -> STRING]
  /\ z \in [Nodes -> [0..MaxLogSize -> LogEntry]]
  /\ w \in Nat
  /\ v \in Nat
  /\ u \in [Nodes -> [Nodes -> BOOLEAN]]
  /\ m \in [Nodes -> Nat]
  /\ n = 0
====
