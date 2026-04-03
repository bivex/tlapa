---- MODULE Demo ----
EXTENDS Naturals

VARIABLES x, y, z, active, count

Init == x = 0

Increment == x' = x + 1

Decrement == x' = x - 1

Double == x' = 2 * x

IsPositive == x > 0

IsZero == x = 0

IncIfPositive == IF x > 0 THEN x' = x + 1 ELSE x' = x

Classify == IF x > 100 THEN "big" ELSE IF x > 10 THEN "medium" ELSE "small"

Label == CASE x = 0 -> "zero" [] x = 1 -> "one" [] OTHER -> "many"

WithHelper == LET sum == x + y + z IN sum > 0

Sum == x + y + z

Negate == ~active

IsReady == active /\ count > 0

====
