---- MODULE TestLambdaChoose ----
EXTENDS Naturals

ChooseMin(x) == CHOOSE x \in Nat : x < 10

ChooseBound == CHOOSE val \in {1, 2, 3} : val > 0

ApplyLambda(f) == f(3)

UseLambda == ApplyLambda(LAMBDA x : x * 2)

====
