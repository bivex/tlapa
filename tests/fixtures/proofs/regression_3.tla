---- MODULE Regression3 ----
EXTENDS Naturals
THEOREM Thm == TRUE
PROOF
  <1>1. \A x \in Nat : x + 0 = x
    BY <1>, <1>  \* BARE LEVELS
  <1>2. INSTANCE Naturals
  <1>3. QED
    BY <1>1, <1>2
====
