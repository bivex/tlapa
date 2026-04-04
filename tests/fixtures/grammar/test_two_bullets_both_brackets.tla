---- MODULE TestTwoBulletsBothBrackets ----
CONSTANTS Nodes, NodeState, STRING
VARIABLES x, y
Init ==
  /\ x \in [Nodes -> NodeState]
  /\ y \in [Nodes -> STRING]
====
