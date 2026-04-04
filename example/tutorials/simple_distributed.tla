---- MODULE SimpleDistributed ----

VARIABLES state, leader, log_index, term

NodeState == {"follower","candidate","leader"}

Nodes == {"n1","n2","n3"}

Init ==
  state \in [Nodes -> NodeState]
    /\ leader = ""
    /\ log_index = 0
    /\ term = 1

Tick == UNCHANGED <<state, leader, log_index, term>>

ElectionTimeout(n) ==
  state[n] = "follower"
    /\ state' = [state EXCEPT ![n] = "candidate"]
    /\ term' = term + 1
    /\ UNCHANGED <<leader, log_index>>

BecomeLeader(n) ==
  state[n] = "candidate"
    /\ state' = [state EXCEPT ![n] = "leader"]
    /\ leader' = n
    /\ UNCHANGED <<log_index, term>>

Heartbeat ==
  leader # ""
    /\ UNCHANGED <<state, leader, log_index, term>>

AppendEntry(entry) ==
  leader # ""
    /\ log_index' = log_index + 1
    /\ UNCHANGED <<state, leader, term>>

Next ==
  Tick
    \/ (\E n \in Nodes: ElectionTimeout(n))
    \/ (\E n \in Nodes: BecomeLeader(n))
    \/ Heartbeat
    \/ (\E e: AppendEntry(e))

====
