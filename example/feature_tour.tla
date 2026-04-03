---- MODULE FeatureTour ----
EXTENDS Naturals

CONSTANTS MAX_VAL, MIN_VAL
VARIABLES x, y, z, active, count

Init == x = 0 /\ y = 0 /\ z = 0 /\ active = FALSE /\ count = 0

IsPositive == x > 0

IsInRange == x >= 0 /\ x <= 100

IsZero == x = 0

NotActive == ~active

IsReady == active /\ count > 0

IsDone == ~active \/ count = 0

Increment == x' = x + 1

Decrement == x' = x - 1

Double == x' = 2 * x

Reset == x' = 0 /\ y' = 0 /\ z' = 0

IncIfPositive == IF x > 0 THEN x' = x + 1 ELSE x' = x

Clamp == IF x > MAX_VAL THEN x' = MAX_VAL ELSE IF x < MIN_VAL THEN x' = MIN_VAL ELSE x' = x

Classify == IF x > 100 THEN "huge" ELSE IF x > 10 THEN "medium" ELSE "small"

NestedIf == IF x > 0 THEN IF y > 0 THEN "both" ELSE "x-only" ELSE "neither"

Combined == IncIfPositive \/ Reset

Spec == Init /\ [][FullNext]_<<x, y, z>>

TypeOK == x \in Nat /\ y \in Nat /\ z \in Nat /\ active \in BOOLEAN

Inv == x >= 0 /\ y >= 0 /\ z >= 0 /\ count >= 0

AllInv == Inv /\ TypeOK

THEOREM Spec => []Inv
THEOREM Init => AllInv

====
