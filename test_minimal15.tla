---- MODULE Test ----
EXTENDS Naturals
CONSTANTS Nodes, NodeState, STRING, MaxLogSize, LogEntry
VARIABLES node_state, current_leader, logs, commit_index, current_term, voted_for, timers, messages, msg_id
LogEntry == [term: Nat, command: STRING]
LastLogTerm(log) == IF Len(log) = 0 THEN 0 ELSE log[Len(log)].term
MatchEntry(log, index, term) == index \in DOMAIN log /\ log[index].term = term
Init == /\ node_state \in ([Nodes -> NodeState]) /\ current_leader \in ([Nodes -> STRING]) /\ logs \in ([Nodes -> [0..MaxLogSize -> LogEntry]]) /\ commit_index \in Nat /\ current_term \in Nat /\ voted_for \in ([Nodes -> [Nodes -> BOOLEAN]]) /\ timers \in ([Nodes -> Nat]) /\ messages = {} /\ msg_id = 0
====
