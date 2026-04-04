---- MODULE TestTemporal ----
EXTENDS Naturals

VARIABLE x

Init == x = 0

Next == x' = x + 1

AlwaysSafe == [] (x >= 0)

EventuallyTrue == <> (x >= 0)

WF_Fair == WF_x(x)
SF_Fair == SF_x(x)

TempSpec == [] (x >= 0)
====
