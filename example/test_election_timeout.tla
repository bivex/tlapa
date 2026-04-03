---- MODULE TestElectionTimeout ----
EXTENDS Naturals
CONSTANTS Nodes, ElectionTimeoutMax
VARIABLES node_state, timers, current_term, voted_for, messages
NodeState == {"follower"}

ElectionTimeout(node) ==
  /\ node_state[node] = "follower"
  /\ timers[node] = 0
  /\ node_state' = [node_state EXCEPT ![node] = "follower"]
  /\ current_term' = current_term + 1
  /\ voted_for' = [n \in Nodes | IF n = node THEN [n \in Nodes |-> TRUE] ELSE voted_for[n]]
  /\ timers' = [n \in Nodes | IF n = node THEN ElectionTimeoutMax ELSE timers[n]]
  /\ messages' = messages \/ {
      [type |-> "RequestVote", to |-> node]
    }
====
