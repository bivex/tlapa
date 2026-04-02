---- MODULE ManyOperators ----
\* A large example with many simple operators to stress-test the diagram renderer

VARIABLES x, y, z, flag1, flag2

\* Simple initialization
Init ==
  /\ x = 0
  /\ y = 0
  /\ z = 0
  /\ flag1 = FALSE
  /\ flag2 = FALSE

\* Arithmetic operators
AddOne == x' = x + 1
AddTwo == y' = y + 2
AddThree == z' = z + 3
DoubleX == x' = 2 * x
DoubleY == y' = 2 * y
IncrementAll ==
  /\ x' = x + 1
  /\ y' = y + 1
  /\ z' = z + 1

\* Comparison operators
GreaterThanZero == x > 0
LessThanTen == x < 10
EqualFive == x = 5
NotEqualToY == x /= y
ZeroOrOne == x = 0 \/ x = 1

\* Logical operators
AndExample == flag1 /\ flag2
OrExample == flag1 \/ flag2
NotFlag1 == ~flag1
ImpliesExample == flag1 => flag2
IffExample == flag1 <=> flag2

\* Combined operators
IncIfPositive ==
  IF x > 0
    THEN x' = x + 1
    ELSE x' = x

AddIfLess ==
  IF y < 5
    THEN y' = y + 1
    ELSE y' = y

CaseExample ==
  CASE x = 0 -> "zero"
      x = 1 -> "one"
      OTHER -> "many"

\* Sequence-like operations (simulated with numbers)
PushX ==
  /\ x' = x + 1
  /\ flag1' = TRUE

PopX ==
  /\ x' = x - 1
  /\ flag1' = FALSE

ToggleFlags ==
  /\ flag1' = ~flag1
  /\ flag2' = ~flag2

\* State machine transitions
Start ==
  /\ x = 0
  /\ flag1 = FALSE

Step1 ==
  /\ flag1 = FALSE
  /\ x' = x + 1
  /\ flag1' = TRUE

Step2 ==
  /\ flag1 = TRUE
  /\ y' = y + 1
  /\ flag1' = FALSE

Step3 ==
  /\ flag2 = FALSE
  /\ z' = z + 1
  /\ flag2' = TRUE

\* Parallel composition simulation
ParallelUpdate ==
  /\ x' = x + 1
  /\ y' = y + 1
  /\ z' = z + 1
  /\ UNCHANGED <<flag1, flag2>>

\* Reset operations
ResetX == x' = 0
ResetY == y' = 0
ResetZ == z' = 0
ResetAll ==
  /\ x' = 0
  /\ y' = 0
  /\ z' = 0
  /\ flag1' = FALSE
  /\ flag2' = FALSE

\* Utility predicates
IsZero == x = 0
IsPositive == x > 0
IsEven == x % 2 = 0
IsOdd == x % 2 # 0
AllZero == x = 0 /\ y = 0 /\ z = 0

\* Next state relation
Next ==
  \/ AddOne
  \/ AddTwo
  \/ AddThree
  \/ DoubleX
  \/ DoubleY
  \/ IncrementAll
  \/ PushX
  \/ PopX
  \/ ToggleFlags
  \/ Step1
  \/ Step2
  \/ Step3
  \/ ParallelUpdate
  \/ ResetX
  \/ ResetY
  \/ ResetZ
  \/ ResetAll

\* Invariants
Inv1 == x >= 0
Inv2 == y >= 0
Inv3 == z >= 0
NonNegative == Inv1 /\ Inv2 /\ Inv3

Invariant1 == flag1 \in BOOLEAN
Invariant2 == flag2 \in BOOLEAN
BooleanFlags == Invariant1 /\ Invariant2

\* Temporal properties
Spec == Init /\ [][Next]_<<x, y, z, flag1, flag2>>
Liveness == <> (x > 10)

\* Theorems
THEOREM Spec => []NonNegative
THEOREM Spec => []BooleanFlags
THEOREM Init => NonNegative
THEOREM [][Next]_vars => ([]<>(x > 5))

\* Lemmas
LEMMA Init => IsZero
LEMMA AddOne => IsPositive
LEMMA ResetAll => AllZero
PROOF
  OBVIOUS

===#