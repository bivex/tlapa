---- MODULE LargeExample ----
\* A comprehensive TLA+ example showcasing various language features

EXTENDS Naturals, FiniteSets, Sequences

CONSTANTS
  MaxClients
  MaxResources

ASSUME
  MaxClients \in Nat
  MaxResources \in Nat

VARIABLES
  clientState,
  allocated,
  requestQueue,
  timestamp

\* Type invariants
TypeInvariant ==
  /\ clientState \in [Clients -> {"waiting", "running", "done"}]
  /\ allocated \subseteq Resources
  /\ requestQueue \in Seq(Clients \x (Resources \x Nat))

\* Initial state
Init ==
  /\ clientState = [c \in Clients |-> "waiting"]
  /\ allocated = {}
  /\ requestQueue = <<>>

\* Helper operators
IsFree(r) == r \notin allocated
AvailableClients == {c \in Clients : clientState[c] = "waiting"}

\* Request operation
Request(c) ==
  /\ c \in AvailableClients
  /\ \E r \in Resources : TRUE
        /\ IsFree(r)
        /\ requestQueue' = Append(requestQueue, <<c, r, 0>>)
  /\ UNCHANGED allocated, clientState

\* Allocate operation
Allocate ==
  /\ requestQueue # <<>>
  /\ LET h == Head(requestQueue)
        c == h[1]
        r == h[2]
        t == h[3]
    IN
      /\ r \in Resources
      /\ IsFree(r)
      /\ allocated' = allocated \cup {r}
      /\ requestQueue' = Tail(requestQueue)
      /\ clientState' = [clientState EXCEPT ![c] = "running"]
  /\ UNCHANGED <<timestamp>>

\* Release operation
Release(c, r) ==
  /\ r \in allocated
  /\ clientState[c] = "running"
  /\ allocated' = allocated \ {r}
  /\ clientState' = [clientState EXCEPT ![c] = "done"]
  /\ UNCHANGED requestQueue, timestamp

\* Next state relation
Next ==
  \/ \E c \in Clients : Request(c)
  \/ Allocate
  /\ UNCHANGED clientState, requestQueue, timestamp

\* Safety properties
NoDoubleAllocation ==
  [][\A r \in Resources : Cardinality({c \in Clients : allocated[c][r] = TRUE}) <= 1]]_allocated

Fairness ==
  WF_vars(Allocate)
  /\ SF_vars(<<Request(c): c \in Clients>>)

\* Liveness property
Progress ==
  \A c \in Clients :
    (clientState[c] = "waiting") => <> (clientState[c] # "waiting")

\* Theorem: deadlock freedom
THEOREM
  Init /\ [][Next]_<<clientState, allocated, requestQueue>>
    => []~(requestQueue = <<>> /\ allocated # {})

\* Auxiliary function for computing wait time
WaitTime(c) ==
  LET idx == Index(requestQueue, [c \in Clients |-> TRUE])
  IN
    IF idx = FALSE
      THEN 0
      ELSE timestamp - (requestQueue[idx])[3]

\* Inductive invariant
Inv ==
  /\ TypeInvariant
  /\ \A c \in Clients :
       IF clientState[c] = "running"
         THEN \E r \in Resources : r \in allocated
       ELSE TRUE

\* Inductive proof
LEMMA Init => Inv
PROOF
  OBVIOUS

LEMMA Inv /\ Next => Inv'
PROOF
  OBVIOUS

\* Main correctness theorem
Correctness == Init /\ [][Next]_vars => []Inv

===#