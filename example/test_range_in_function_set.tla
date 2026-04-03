---- MODULE TestRange ----
CONSTANTS MaxLogSize, LogEntry
VARIABLES x
Init ==
  /\ x \in [0..MaxLogSize -> LogEntry]
====
