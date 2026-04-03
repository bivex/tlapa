---- MODULE TestMessageRecord ----
CONSTANTS STRING, Nat, LogEntry, Seq
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
====
