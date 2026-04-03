--------------------------- MODULE DistributedLog ---------------------------

EXTENDS Naturals, Sequences, FiniteSets

CONSTANTS Nodes, ElectionTimeoutMin, ElectionTimeoutMax, MaxLogSize

ASSUME
  ElectionTimeoutMin \in Nat,
  ElectionTimeoutMax \in Nat,
  ElectionTimeoutMax > ElectionTimeoutMin,
  MaxLogSize \in Nat,
  Nodes \subseteq [id -> STRING]

VARIABLES
  node_state,
  current_leader,
  logs,
  commit_index,
  current_term,
  voted_for,
  timers,
  messages,
  msg_id

LogEntry == [term: Nat, command: STRING]

NodeState == {"follower", "candidate", "leader"}

MessageType == {"RequestVote", "RequestVoteReply", "AppendEntries", "AppendEntriesReply"}

Message == [
  type: MessageType,
  to: STRING,
  from: STRING,
  term: Nat,
  last_log_index: Nat,
  last_log_term: Nat,
  prev_log_index: Nat,
  prev_log_term: Nat,
  entries: [Seq(LogEntry)],
  leader_commit: Nat,
  success: BOOLEAN,
  msg_id: Nat
]

SafeLogAt(log, idx) ==
  IF idx \in DOMAIN log THEN log[idx] ELSE [term |-> 0, command |-> ""]

LastLogIndex(log) == Len(log)

LastLogTerm(log) ==
  IF Len(log) = 0 THEN 0 ELSE log[Len(log)].term

LogMoreUpToDate(log_a, log_b) ==
  LET term_a == LastLogTerm(log_a)
      term_b == LastLogTerm(log_b)
  IN term_a > term_b \/ (term_a = term_b /\ Len(log_a) > Len(log_b))

MatchEntry(log, index, term) ==
  index \in DOMAIN log /\ log[index].term = term

Init ==
  /\ node_state \in [Nodes -> NodeState]
  /\ current_leader \in [Nodes -> STRING]
  /\ logs \in [Nodes -> [0..MaxLogSize -> LogEntry]]
  /\ commit_index \in Nat
  /\ current_term \in Nat
  /\ voted_for \in [Nodes -> [Nodes -> BOOLEAN]]
  /\ timers \in [Nodes -> Nat]
  /\ messages = {}
  /\ msg_id = 0

Tick ==
  /\ msg_id' = msg_id + 1
  /\ node_state' = node_state
  /\ current_leader' = current_leader
  /\ logs' = logs
  /\ commit_index' = commit_index
  /\ current_term' = current_term
  /\ voted_for' = voted_for
  /\ timers' = [n \in Nodes |
      IF timers[n] > 0 THEN timers[n] - 1 ELSE 0]
  /\ messages' = messages

ElectionTimeout(node) ==
  /\ node_state[node] = "follower"
  /\ timers[node] = 0
  /\ node_state' = [node_state EXCEPT ![node] = "candidate"]
  /\ current_term' = current_term + 1
  /\ voted_for' = [n \in Nodes |
      IF n = node THEN [n \in Nodes |-> TRUE] ELSE voted_for[n]]
  /\ timers' = [n \in Nodes |
      IF n = node THEN ElectionTimeoutMax ELSE timers[n]]
  /\ messages' = messages ∪ {
      [type |-> "RequestVote",
       to |-> n',
       from |-> node,
       term |-> current_term',
       last_log_index |-> LastLogIndex(logs[node]),
       last_log_term |-> LastLogTerm(logs[node]),
       msg_id |-> msg_id,
       success |-> FALSE]
      : n' \in Nodes, n' # node
    }

BecomeLeader(node) ==
  /\ node_state[node] = "candidate"
  /\ \A n \in Nodes \ {node}: voted_for[n][node]
  /\ node_state' = [node_state EXCEPT ![node] = "leader"]
  /\ current_leader' = [current_leader EXCEPT ![node] = node]
  /\ timers' = [n \in Nodes | IF n = node THEN ElectionTimeoutMax ELSE timers[n]]
  /\ messages' = messages ∪ {
      [type |-> "AppendEntries",
       to |-> n',
       from |-> node,
       term |-> current_term,
       prev_log_index |-> LastLogIndex(logs[node]),
       prev_log_term |-> LastLogTerm(logs[node]),
       entries |-> <<>>,
       leader_commit |-> commit_index,
       msg_id |-> msg_id + 1,
       success |-> FALSE]
      : n' \in Nodes \ {node}
    }

StepDown(node, new_term) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ new_term > current_term
  /\ node_state' = [node_state EXCEPT ![node] = "follower"]
  /\ current_leader' = [current_leader EXCEPT ![node] = ""]
  /\ current_term' = new_term
  /\ timers' = [n \in Nodes | IF n = node THEN ElectionTimeoutMin ELSE timers[n]]
  /\ voted_for' = [voted_for EXCEPT ![node] = [n \in Nodes |-> FALSE]]

HandleRequestVote(node, msg) ==
  /\ node_state[node] \in {"follower", "candidate"}
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
            /\ messages' = messages ∪ {
                [type |-> "RequestVoteReply",
                 to |-> msg.from,
                 from |-> node,
                 term |-> current_term,
                 msg_id |-> msg_id + 1,
                 success |-> TRUE]
              }
         ELSE
           /\ messages' = messages
  /\ UNCHANGED node_state, current_leader, logs, commit_index, timers, msg_id

HandleAppendEntries(node, msg) ==
  /\ node_state[node] \in {"follower", "candidate"}
  /\ IF msg.term < current_term THEN
       /\ messages' = messages
     ELSE
       IF msg.term > current_term THEN
         /\ node_state' = [node_state EXCEPT ![node] = "follower"]
       ELSE
         /\ node_state' = node_state
       /\ current_term' = msg.term
       /\ current_leader' = [current_leader EXCEPT ![node] = msg.from]
       /\ timers' = [timers EXCEPT ![node] = ElectionTimeoutMax]
       /\ IF msg.prev_log_index = 0 \/ MatchEntry(logs[node], msg.prev_log_index, msg.prev_log_term) THEN
            LET new_entries == IF Len(msg.entries) > 0 THEN msg.entries ELSE <<>>
                new_log == [i \in 1..(msg.prev_log_index + Len(new_entries)) |
                  IF i <= msg.prev_log_index THEN logs[node][i]
                  ELSE new_entries[i - msg.prev_log_index]]
                trimmed_log == [i \in 1..Min(MaxLogSize, Len(new_log)) |-> new_log[i]]
            THEN
               /\ logs' = [logs EXCEPT ![node] = trimmed_log]
               /\ commit_index' = Max(commit_index, msg.leader_commit)
               /\ answer_success = TRUE
         ELSE
           /\ logs' = logs
           /\ commit_index' = commit_index
           /\ answer_success = FALSE
       /\ messages' = messages ∪ {
           [type |-> "AppendEntriesReply",
            to |-> msg.from,
            from |-> node,
            term |-> current_term',
            msg_id |-> msg_id + 1,
            success |-> answer_success,
            match_index |-> IF answer_success THEN LastLogIndex(logs'[node]) ELSE 0]
         }

HandleAppendEntriesReply(leader, msg) ==
  /\ node_state[leader] = "leader"
  /\ current_term = msg.term
  /\ IF msg.success THEN
        /\ commit_index' = Max(commit_index, Min(MaxLogSize, msg.match_index))
     ELSE
        /\ commit_index' = commit_index
  /\ UNCHANGED node_state, current_leader, logs, voted_for, timers, msg_id, messages

ClientSubmit(node, cmd) ==
  /\ node_state[node] = "leader"
  /\ msg_id' = msg_id + 1
  /\ current_term' = current_term
  /\ logs' = [logs EXCEPT ![node] = Append(logs[node],
        [term |-> current_term, command |-> cmd])]
  /\ messages' = messages ∪ {
      [type |-> "AppendEntries",
       to |-> n,
       from |-> node,
       term |-> current_term,
       prev_log_index |-> LastLogIndex(logs[node]) - 1,
       prev_log_term |-> IF LastLogIndex(logs[node]) > 1 THEN logs[node][LastLogIndex(logs[node]) - 1].term ELSE 0,
       entries |-> <<[term |-> current_term, command |-> cmd]>>,
       leader_commit |-> commit_index,
       msg_id |-> msg_id + 1,
       success |-> FALSE]
      : n \in Nodes \ {node}
    }

Next ==
  Tick
  \/ (\E n \in Nodes: ElectionTimeout(n))
  \/ (\E n \in Nodes: BecomeLeader(n))
  \/ (\E n \in Nodes, m \in messages: m.type = "RequestVote" /\ m.to = n /\ HandleRequestVote(n, m))
  \/ (\E n \in Nodes, m \in messages: m.type = "AppendEntries" /\ m.to = n /\ HandleAppendEntries(n, m))
  \/ (\E n \in Nodes, m \in messages: m.type = "AppendEntriesReply" /\ m.to = n /\ HandleAppendEntriesReply(n, m))
  \/ (\E n \in Nodes, cmd \in STRING: ClientSubmit(n, cmd))
  \/ messages' = messages \ {m \in messages: m.type \in {"RequestVoteReply","AppendEntriesReply"}}
  \/ UNCHANGED <<node_state, logs, commit_index, current_term, voted_for, timers, msg_id>>

LeaderAppendOnly ==
  \A n \in Nodes: node_state[n] = "leader" =>
    \A i \in 1..(LastLogIndex(logs[n]) - 1):
      logs[n][i] = logs[n]'[i]

LogsMatchCommonPrefix ==
  \A n1, n2 \in Nodes, i \in DOMAIN logs[n1] \cap DOMAIN logs[n2]:
    (logs[n1][i].term = logs[n2][i].term) => logs[n1][i] = logs[n2][i]

CommitOnlyIfQuorum ==
  \A idx > commit_index:
    \E quorum \subseteq Nodes:
      Card(quorum) > (Card(Nodes) \div 2) /\
      \A n \in quorum: idx \in DOMAIN logs[n] /\ logs[n][idx].term = current_term

LeaderCompleteness ==
  \A n \in Nodes, idx \in 1..commit_index:
    \E l \in Nodes: node_state[l] = "leader" /\
      idx \in DOMAIN logs[l] /\ logs[l][idx].term = current_term

EventualLeader ==
  <> (\E n \in Nodes: node_state[n] = "leader")

TypeInvariant ==
  /\ node_state \in [Nodes -> NodeState]
  /\ logs \in [Nodes -> [0..MaxLogSize -> LogEntry]]
  /\ commit_index \in 0..MaxLogSize
  /\ current_term \in Nat
  /\ voted_for \in [Nodes -> [Nodes -> BOOLEAN]]
  /\ timers \in [Nodes -> 0..ElectionTimeoutMax]
  /\ messages \subseteq Message
  /\ msg_id \in Nat

Spec == Init /\ [][Next]_<<node_state, logs, commit_index, current_term, voted_for, timers, messages, msg_id>>

THEOREM Spec => []TypeInvariant

=============================================================================
