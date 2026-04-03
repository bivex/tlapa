---- MODULE TestNested ----
VARIABLES node_state, current_term, messages, voted_for, logs, msg_id
CONSTANTS Nodes, NodeState, msg, LogEntry, MaxLogSize

HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower","candidate"}
  /\ current_term >= msg.term
  /\ IF current_term > msg.term THEN
       /\ messages' = messages
     ELSE
       IF voted_for[node][msg.from] THEN
         /\ messages' = messages
       ELSE
         IF LogMoreUpToDate(logs[node],
             [msg.last_log_index |-> [term |-> msg.last_log_term, command |-> ""]]) THEN
           /\ voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]
           /\ messages' = messages \/ {
               [type |-> "RequestVoteReply"]
             }
         ELSE
           /\ messages' = messages
  /\ UNCHANGED <<node_state, current_leader, logs, commit_index, timers>>
====
