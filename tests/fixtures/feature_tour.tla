---- MODULE FeatureTour ----
EXTENDS Naturals, Sequences

CONSTANTS MaxVal, Node

VARIABLES x, y, vals

Inc(n) == n + 1

Double(n) == n * 2

Range(S) == {x \in S : TRUE}

Max(a, b) == IF a > b THEN a ELSE b

AbsVal(n) == IF n < 0 THEN (0 - n) ELSE n

Fib(n) ==
    LET F(k) == IF k <= 1 THEN k ELSE F(k - 1) + F(k - 2)
    IN F(n)

Swap(seq, i, j) ==
    LET tmp == seq[i]
        with_i == [seq EXCEPT ![i] = seq[j]]
    IN [with_i EXCEPT ![j] = tmp]

MinOf(S) == CHOOSE m \in S : m <= 3

Apply(f, n) == f(n)

UseLambda == Apply(LAMBDA x : x + 10, 5)

Evens == {2 * n : n \in 0..10}

Squared == {n * n : n \in 1..5}

SubsetOf(S) == SUBSET S

UnionOf(F) == UNION F

Init == x = 0 /\ y = 0 /\ vals = <<>>

AddVal(v) == vals' = Append(vals, v)

GetRecord == [name |-> "test", value |-> 42, active |-> TRUE]

NestedRecord ==
    [server |-> [host |-> "localhost", port |-> 8080],
     status |-> "running"]

ConstArray == [i \in 1..10 |-> 0]

IdentMatrix == [r \in 1..3 |-> [c \in 1..3 |-> IF r = c THEN 1 ELSE 0]]

AllPositive(S) == \A n \in S : n > 0

ExistsZero(S) == \E n \in S : n = 0

Safety == []TypeInv

Liveness == <>Done

Fairness == WF_vars(Next)

StrongFair == SF_vars(Next)

LeadsTo == Init ~> Done

AlwaysSafe == []TypeInv

EventuallyDone == <>Done

Step == x' = x + 1 /\ UNCHANGED <<y, vals>>

StutterStep == []Next

CanStep == ENABLED Next

TypeInv == /\ x \in Nat
            /\ y \in Nat
            /\ vals \in Seq(Nat)

Next ==
    /\ \/ IncX
       \/ IncY
       \/ AddSomething
    /\ x <= MaxVal
    /\ y <= MaxVal

IncX == x' = x + 1 /\ UNCHANGED <<y, vals>>

IncY == y' = y + 1 /\ UNCHANGED <<x, vals>>

AddSomething == vals' = Append(vals, x + y) /\ UNCHANGED <<x, y>>

RECURSIVE Fact(_), Sum(_)

Fact(n) == IF n = 0 THEN 1 ELSE n * Fact(n - 1)

Sum(n) == IF n = 0 THEN 0 ELSE n + Sum(n - 1)

ASSUME MaxVal > 0

ASSUME NodeOK == Node # ""

THEOREM ThmIncPositive ==
    \A n \in Nat : Inc(n) > n
PROOF
    <1> TAKE n \in Nat
    <1> HAVE Inc(n) = n + 1
        OBVIOUS
    <1> HAVE n + 1 > n
        OBVIOUS
    <1> QED
        OBVIOUS

THEOREM ThmFactPositive ==
    \A n \in Nat : Fact(n) > 0
PROOF
    <1> ASSERT Fact(n) > 0
    <2> TAKE k \in Nat
    <2> WITNESS Fact(k)
    <2> HAVE Fact(k) > 0
        BY DEF Fact
    <2> QED
        OBVIOUS

THEOREM ThmDouble ==
    \A n \in Nat : Double(n) = 2 * n
PROOF OBVIOUS

THEOREM ThmMaxCommutative ==
    \A a, b \in Nat : Max(a, b) = Max(b, a)
PROOF
    <1> ASSERT Max(a, b) = Max(b, a)
        BY DEF Max
    <1> QED
        OBVIOUS

LEMMA LemmaSum == Sum(3) = 6
PROOF BY DEF Sum

INSTANCE Sequences

a ++ b == a \cup b

Done == x = MaxVal /\ y = MaxVal /\ Len(vals) = MaxVal

====
