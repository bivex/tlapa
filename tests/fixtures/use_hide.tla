---- MODULE TestUseHide ----
EXTENDS Naturals

F(x) == x + 1

G(x) == x * 2

THEOREM Thm1 == F(1) = 2
PROOF
    USE F
    HAVE F(1) = 2
    QED
====
