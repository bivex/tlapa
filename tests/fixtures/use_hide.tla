---- MODULE TestUseHide ----
EXTENDS Naturals

F(x) == x + 1

G(x) == x * 2

THEOREM Thm1 == F(1) = 2
PROOF
    <1> USE F, G
    <2> HIDE x, y
    <3> HAVE F(1) = 2
    <4> TAKE n \in Nat
    <5> WITNESS n + 1
    <6> OBVIOUS
QED
====
