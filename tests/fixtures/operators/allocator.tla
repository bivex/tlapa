---- MODULE SimpleAllocator ----
EXTENDS Naturals, FiniteSets

CONSTANTS Clients, Resources

VARIABLES allocated, requests

TypeInvariant ==
    /\ allocated \subseteq Resources
    /\ requests \subseteq Resources

Init ==
    /\ allocated = {}
    /\ requests = {}

Request(c) ==
    /\ \E r \in Resources \ allocated :
        requests' = requests \cup {r}
    /\ allocated' = allocated

Allocate(c, r) ==
    /\ r \in requests
    /\ r \notin allocated
    /\ allocated' = allocated \cup {r}
    /\ requests' = requests \ {r}

Release(c, r) ==
    /\ r \in allocated
    /\ allocated' = allocated \ {r}
    /\ requests' = requests

Next ==
    \E c \in Clients :
        \/ Request(c)
        \/ \E r \in Resources : Allocate(c, r) \/ Release(c, r)

Spec == Init /\ [][Next]_<<allocated, requests>>

NoDeadlock == ~(allocated = Resources /\ requests = {})
====
