---- MODULE TestProof ----
EXTENDS Naturals

THEOREM Thm1 == TRUE
OBVIOUS

THEOREM Thm2 == TRUE
PROOF OMITTED

THEOREM AddComm == \A x, y \in Nat: x + y = y + x
PROOF
    <1> x + 0 = x
        BY DEF ZeroIdentity
    <2> \A z \in Nat: x + S(z) = S(x + z)
        OBVIOUS
    <3> QED

THEOREM MyThm == TRUE
PROOF BY DEF Thm1

LEMMA Lemma1 == TRUE
BY OBVIOUS
====
