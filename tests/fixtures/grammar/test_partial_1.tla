---- MODULE TestPartial1 ----
VARIABLES node_state, current_term, messages, voted_for, msg_id
CONSTANTS Nodes, NodeState, STRING

HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower","candidate"}
  /\ current_term >= msg.term
  /\ IF current_term > msg.term THEN
       /\ messages' = messages
     ELSE
       IF voted_for[node][msg.from] THEN
         /\ messages' = messages
       ELSE
         /\ voted_for' = [voted_for EXCEPT ![node][msg.from] = TRUE]
         /\ messages' = messages \/ {
             [type |-> "RequestVoteReply"]
           }
  /\ UNCHANGED <<node_state, current_leader, logs, commit_index, timers>>
====
