---- MODULE BigExample ----

VARIABLES a, b, c, d, e

Init ==
  /\ a = 0
  /\ b = 0
  /\ c = 0
  /\ d = 0
  /\ e = 0

Add1 == a' = a + 1
Add2 == b' = b + 2
Add3 == c' = c + 3
Mul2 == d' = 2 * d
Dec1 == e' = e - 1

Gt0 == a > 0
Lt5 == b < 5
Eq3 == c = 3
Ne0 == d # 0
Le2 == e <= 2

AndAB == a > 0 /\ b < 10
OrCD == c = 0 \/ d # 0
NotE == ~(e = 0)
Imp1 == a = 0 => b = 0
Iff1 == (a = b) <=> (c = d)

State1 ==
  /\ a' = a + 1
  /\ b' = b + 1
  /\ UNCHANGED <<c, d, e>>

State2 ==
  /\ c' = c + 1
  /\ d' = d + 1
  /\ UNCHANGED <<a, b, e>>

Combined == State1 \/ State2

Next ==
  \/ Add1
  \/ Add2
  \/ Add3
  \/ Mul2
  \/ Dec1
  \/ State1
  \/ State2

InvA == a >= 0
InvB == b >= 0
InvC == c >= 0
InvD == d >= 0
InvE == e >= 0
AllInv == InvA /\ InvB /\ InvC /\ InvD /\ InvE

Spec == Init /\ [][Next]_<<a, b, c, d, e>>

THEOREM Spec => []AllInv
THEOREM Init => AllInv

===#