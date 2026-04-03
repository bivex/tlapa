# Generated from tlaparser/parser/TLAPLusParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .TLAPLusParser import TLAPLusParser
else:
    from TLAPLusParser import TLAPLusParser

# This class defines a complete listener for a parse tree produced by TLAPLusParser.
class TLAPLusParserListener(ParseTreeListener):

    # Enter a parse tree produced by TLAPLusParser#unit.
    def enterUnit(self, ctx:TLAPLusParser.UnitContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#unit.
    def exitUnit(self, ctx:TLAPLusParser.UnitContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#firstModule.
    def enterFirstModule(self, ctx:TLAPLusParser.FirstModuleContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#firstModule.
    def exitFirstModule(self, ctx:TLAPLusParser.FirstModuleContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#module.
    def enterModule(self, ctx:TLAPLusParser.ModuleContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#module.
    def exitModule(self, ctx:TLAPLusParser.ModuleContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#endModule.
    def enterEndModule(self, ctx:TLAPLusParser.EndModuleContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#endModule.
    def exitEndModule(self, ctx:TLAPLusParser.EndModuleContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#extends.
    def enterExtends(self, ctx:TLAPLusParser.ExtendsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#extends.
    def exitExtends(self, ctx:TLAPLusParser.ExtendsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#moduleBody.
    def enterModuleBody(self, ctx:TLAPLusParser.ModuleBodyContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#moduleBody.
    def exitModuleBody(self, ctx:TLAPLusParser.ModuleBodyContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:TLAPLusParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:TLAPLusParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#parameterDeclaration.
    def enterParameterDeclaration(self, ctx:TLAPLusParser.ParameterDeclarationContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#parameterDeclaration.
    def exitParameterDeclaration(self, ctx:TLAPLusParser.ParameterDeclarationContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#constantDeclItem.
    def enterConstantDeclItem(self, ctx:TLAPLusParser.ConstantDeclItemContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#constantDeclItem.
    def exitConstantDeclItem(self, ctx:TLAPLusParser.ConstantDeclItemContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#prefixDecl.
    def enterPrefixDecl(self, ctx:TLAPLusParser.PrefixDeclContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#prefixDecl.
    def exitPrefixDecl(self, ctx:TLAPLusParser.PrefixDeclContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#infixDecl.
    def enterInfixDecl(self, ctx:TLAPLusParser.InfixDeclContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#infixDecl.
    def exitInfixDecl(self, ctx:TLAPLusParser.InfixDeclContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#postfixDecl.
    def enterPostfixDecl(self, ctx:TLAPLusParser.PostfixDeclContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#postfixDecl.
    def exitPostfixDecl(self, ctx:TLAPLusParser.PostfixDeclContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#recursiveDeclaration.
    def enterRecursiveDeclaration(self, ctx:TLAPLusParser.RecursiveDeclarationContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#recursiveDeclaration.
    def exitRecursiveDeclaration(self, ctx:TLAPLusParser.RecursiveDeclarationContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#operatorOrFunctionDefinition.
    def enterOperatorOrFunctionDefinition(self, ctx:TLAPLusParser.OperatorOrFunctionDefinitionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#operatorOrFunctionDefinition.
    def exitOperatorOrFunctionDefinition(self, ctx:TLAPLusParser.OperatorOrFunctionDefinitionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#functionDefinition.
    def enterFunctionDefinition(self, ctx:TLAPLusParser.FunctionDefinitionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#functionDefinition.
    def exitFunctionDefinition(self, ctx:TLAPLusParser.FunctionDefinitionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#operatorDefinition.
    def enterOperatorDefinition(self, ctx:TLAPLusParser.OperatorDefinitionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#operatorDefinition.
    def exitOperatorDefinition(self, ctx:TLAPLusParser.OperatorDefinitionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#moduleDefinition.
    def enterModuleDefinition(self, ctx:TLAPLusParser.ModuleDefinitionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#moduleDefinition.
    def exitModuleDefinition(self, ctx:TLAPLusParser.ModuleDefinitionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#identLhs.
    def enterIdentLhs(self, ctx:TLAPLusParser.IdentLhsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#identLhs.
    def exitIdentLhs(self, ctx:TLAPLusParser.IdentLhsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#prefixLhs.
    def enterPrefixLhs(self, ctx:TLAPLusParser.PrefixLhsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#prefixLhs.
    def exitPrefixLhs(self, ctx:TLAPLusParser.PrefixLhsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#infixLhs.
    def enterInfixLhs(self, ctx:TLAPLusParser.InfixLhsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#infixLhs.
    def exitInfixLhs(self, ctx:TLAPLusParser.InfixLhsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#postfixLhs.
    def enterPostfixLhs(self, ctx:TLAPLusParser.PostfixLhsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#postfixLhs.
    def exitPostfixLhs(self, ctx:TLAPLusParser.PostfixLhsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#functionBody.
    def enterFunctionBody(self, ctx:TLAPLusParser.FunctionBodyContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#functionBody.
    def exitFunctionBody(self, ctx:TLAPLusParser.FunctionBodyContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#identifierTuple.
    def enterIdentifierTuple(self, ctx:TLAPLusParser.IdentifierTupleContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#identifierTuple.
    def exitIdentifierTuple(self, ctx:TLAPLusParser.IdentifierTupleContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#instance.
    def enterInstance(self, ctx:TLAPLusParser.InstanceContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#instance.
    def exitInstance(self, ctx:TLAPLusParser.InstanceContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#instantiation.
    def enterInstantiation(self, ctx:TLAPLusParser.InstantiationContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#instantiation.
    def exitInstantiation(self, ctx:TLAPLusParser.InstantiationContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#substitution.
    def enterSubstitution(self, ctx:TLAPLusParser.SubstitutionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#substitution.
    def exitSubstitution(self, ctx:TLAPLusParser.SubstitutionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#opOrExpr.
    def enterOpOrExpr(self, ctx:TLAPLusParser.OpOrExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#opOrExpr.
    def exitOpOrExpr(self, ctx:TLAPLusParser.OpOrExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#prefixOp.
    def enterPrefixOp(self, ctx:TLAPLusParser.PrefixOpContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#prefixOp.
    def exitPrefixOp(self, ctx:TLAPLusParser.PrefixOpContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#nonExpPrefixOp.
    def enterNonExpPrefixOp(self, ctx:TLAPLusParser.NonExpPrefixOpContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#nonExpPrefixOp.
    def exitNonExpPrefixOp(self, ctx:TLAPLusParser.NonExpPrefixOpContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#infixOp.
    def enterInfixOp(self, ctx:TLAPLusParser.InfixOpContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#infixOp.
    def exitInfixOp(self, ctx:TLAPLusParser.InfixOpContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#postfixOp.
    def enterPostfixOp(self, ctx:TLAPLusParser.PostfixOpContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#postfixOp.
    def exitPostfixOp(self, ctx:TLAPLusParser.PostfixOpContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#assumeProve.
    def enterAssumeProve(self, ctx:TLAPLusParser.AssumeProveContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#assumeProve.
    def exitAssumeProve(self, ctx:TLAPLusParser.AssumeProveContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#assumption.
    def enterAssumption(self, ctx:TLAPLusParser.AssumptionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#assumption.
    def exitAssumption(self, ctx:TLAPLusParser.AssumptionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#newSymb.
    def enterNewSymb(self, ctx:TLAPLusParser.NewSymbContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#newSymb.
    def exitNewSymb(self, ctx:TLAPLusParser.NewSymbContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#identDecl.
    def enterIdentDecl(self, ctx:TLAPLusParser.IdentDeclContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#identDecl.
    def exitIdentDecl(self, ctx:TLAPLusParser.IdentDeclContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#theorem.
    def enterTheorem(self, ctx:TLAPLusParser.TheoremContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#theorem.
    def exitTheorem(self, ctx:TLAPLusParser.TheoremContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#maybeBound.
    def enterMaybeBound(self, ctx:TLAPLusParser.MaybeBoundContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#maybeBound.
    def exitMaybeBound(self, ctx:TLAPLusParser.MaybeBoundContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#proof.
    def enterProof(self, ctx:TLAPLusParser.ProofContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#proof.
    def exitProof(self, ctx:TLAPLusParser.ProofContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#terminalProof.
    def enterTerminalProof(self, ctx:TLAPLusParser.TerminalProofContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#terminalProof.
    def exitTerminalProof(self, ctx:TLAPLusParser.TerminalProofContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#useOrHide.
    def enterUseOrHide(self, ctx:TLAPLusParser.UseOrHideContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#useOrHide.
    def exitUseOrHide(self, ctx:TLAPLusParser.UseOrHideContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#stepStartToken.
    def enterStepStartToken(self, ctx:TLAPLusParser.StepStartTokenContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#stepStartToken.
    def exitStepStartToken(self, ctx:TLAPLusParser.StepStartTokenContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#step.
    def enterStep(self, ctx:TLAPLusParser.StepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#step.
    def exitStep(self, ctx:TLAPLusParser.StepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#qedStep.
    def enterQedStep(self, ctx:TLAPLusParser.QedStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#qedStep.
    def exitQedStep(self, ctx:TLAPLusParser.QedStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#defStep.
    def enterDefStep(self, ctx:TLAPLusParser.DefStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#defStep.
    def exitDefStep(self, ctx:TLAPLusParser.DefStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#haveStep.
    def enterHaveStep(self, ctx:TLAPLusParser.HaveStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#haveStep.
    def exitHaveStep(self, ctx:TLAPLusParser.HaveStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#takeStep.
    def enterTakeStep(self, ctx:TLAPLusParser.TakeStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#takeStep.
    def exitTakeStep(self, ctx:TLAPLusParser.TakeStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#witnessStep.
    def enterWitnessStep(self, ctx:TLAPLusParser.WitnessStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#witnessStep.
    def exitWitnessStep(self, ctx:TLAPLusParser.WitnessStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#pickStep.
    def enterPickStep(self, ctx:TLAPLusParser.PickStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#pickStep.
    def exitPickStep(self, ctx:TLAPLusParser.PickStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#caseStep.
    def enterCaseStep(self, ctx:TLAPLusParser.CaseStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#caseStep.
    def exitCaseStep(self, ctx:TLAPLusParser.CaseStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#assertStep.
    def enterAssertStep(self, ctx:TLAPLusParser.AssertStepContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#assertStep.
    def exitAssertStep(self, ctx:TLAPLusParser.AssertStepContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#expression.
    def enterExpression(self, ctx:TLAPLusParser.ExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#expression.
    def exitExpression(self, ctx:TLAPLusParser.ExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#QuantifierExpression.
    def enterQuantifierExpression(self, ctx:TLAPLusParser.QuantifierExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#QuantifierExpression.
    def exitQuantifierExpression(self, ctx:TLAPLusParser.QuantifierExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#TemporalQuantifierExpression.
    def enterTemporalQuantifierExpression(self, ctx:TLAPLusParser.TemporalQuantifierExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#TemporalQuantifierExpression.
    def exitTemporalQuantifierExpression(self, ctx:TLAPLusParser.TemporalQuantifierExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#QuantifierPassThrough.
    def enterQuantifierPassThrough(self, ctx:TLAPLusParser.QuantifierPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#QuantifierPassThrough.
    def exitQuantifierPassThrough(self, ctx:TLAPLusParser.QuantifierPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ChooseExpression.
    def enterChooseExpression(self, ctx:TLAPLusParser.ChooseExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ChooseExpression.
    def exitChooseExpression(self, ctx:TLAPLusParser.ChooseExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ChoosePassThrough.
    def enterChoosePassThrough(self, ctx:TLAPLusParser.ChoosePassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ChoosePassThrough.
    def exitChoosePassThrough(self, ctx:TLAPLusParser.ChoosePassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#IfThenElseExpression.
    def enterIfThenElseExpression(self, ctx:TLAPLusParser.IfThenElseExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#IfThenElseExpression.
    def exitIfThenElseExpression(self, ctx:TLAPLusParser.IfThenElseExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#IfPassThrough.
    def enterIfPassThrough(self, ctx:TLAPLusParser.IfPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#IfPassThrough.
    def exitIfPassThrough(self, ctx:TLAPLusParser.IfPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#CaseExpression.
    def enterCaseExpression(self, ctx:TLAPLusParser.CaseExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#CaseExpression.
    def exitCaseExpression(self, ctx:TLAPLusParser.CaseExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#CasePassThrough.
    def enterCasePassThrough(self, ctx:TLAPLusParser.CasePassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#CasePassThrough.
    def exitCasePassThrough(self, ctx:TLAPLusParser.CasePassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#caseArm.
    def enterCaseArm(self, ctx:TLAPLusParser.CaseArmContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#caseArm.
    def exitCaseArm(self, ctx:TLAPLusParser.CaseArmContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#otherArm.
    def enterOtherArm(self, ctx:TLAPLusParser.OtherArmContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#otherArm.
    def exitOtherArm(self, ctx:TLAPLusParser.OtherArmContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#LetInExpression.
    def enterLetInExpression(self, ctx:TLAPLusParser.LetInExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#LetInExpression.
    def exitLetInExpression(self, ctx:TLAPLusParser.LetInExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#LetPassThrough.
    def enterLetPassThrough(self, ctx:TLAPLusParser.LetPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#LetPassThrough.
    def exitLetPassThrough(self, ctx:TLAPLusParser.LetPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#letDefinition.
    def enterLetDefinition(self, ctx:TLAPLusParser.LetDefinitionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#letDefinition.
    def exitLetDefinition(self, ctx:TLAPLusParser.LetDefinitionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#EquivPassThrough.
    def enterEquivPassThrough(self, ctx:TLAPLusParser.EquivPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#EquivPassThrough.
    def exitEquivPassThrough(self, ctx:TLAPLusParser.EquivPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#EquivBinaryExpr.
    def enterEquivBinaryExpr(self, ctx:TLAPLusParser.EquivBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#EquivBinaryExpr.
    def exitEquivBinaryExpr(self, ctx:TLAPLusParser.EquivBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ImpliesBinaryExpr.
    def enterImpliesBinaryExpr(self, ctx:TLAPLusParser.ImpliesBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ImpliesBinaryExpr.
    def exitImpliesBinaryExpr(self, ctx:TLAPLusParser.ImpliesBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ImpliesPassThrough.
    def enterImpliesPassThrough(self, ctx:TLAPLusParser.ImpliesPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ImpliesPassThrough.
    def exitImpliesPassThrough(self, ctx:TLAPLusParser.ImpliesPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#OrBinaryExpr.
    def enterOrBinaryExpr(self, ctx:TLAPLusParser.OrBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#OrBinaryExpr.
    def exitOrBinaryExpr(self, ctx:TLAPLusParser.OrBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#OrPassThrough.
    def enterOrPassThrough(self, ctx:TLAPLusParser.OrPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#OrPassThrough.
    def exitOrPassThrough(self, ctx:TLAPLusParser.OrPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#AndPassThrough.
    def enterAndPassThrough(self, ctx:TLAPLusParser.AndPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#AndPassThrough.
    def exitAndPassThrough(self, ctx:TLAPLusParser.AndPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#AndBinaryExpr.
    def enterAndBinaryExpr(self, ctx:TLAPLusParser.AndBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#AndBinaryExpr.
    def exitAndBinaryExpr(self, ctx:TLAPLusParser.AndBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ConjunctionList.
    def enterConjunctionList(self, ctx:TLAPLusParser.ConjunctionListContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ConjunctionList.
    def exitConjunctionList(self, ctx:TLAPLusParser.ConjunctionListContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#DisjunctionList.
    def enterDisjunctionList(self, ctx:TLAPLusParser.DisjunctionListContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#DisjunctionList.
    def exitDisjunctionList(self, ctx:TLAPLusParser.DisjunctionListContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#JunctionPassThrough.
    def enterJunctionPassThrough(self, ctx:TLAPLusParser.JunctionPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#JunctionPassThrough.
    def exitJunctionPassThrough(self, ctx:TLAPLusParser.JunctionPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#EqualityBinaryExpr.
    def enterEqualityBinaryExpr(self, ctx:TLAPLusParser.EqualityBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#EqualityBinaryExpr.
    def exitEqualityBinaryExpr(self, ctx:TLAPLusParser.EqualityBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#EqualityPassThrough.
    def enterEqualityPassThrough(self, ctx:TLAPLusParser.EqualityPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#EqualityPassThrough.
    def exitEqualityPassThrough(self, ctx:TLAPLusParser.EqualityPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ComparePassThrough.
    def enterComparePassThrough(self, ctx:TLAPLusParser.ComparePassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ComparePassThrough.
    def exitComparePassThrough(self, ctx:TLAPLusParser.ComparePassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#CompareBinaryExpr.
    def enterCompareBinaryExpr(self, ctx:TLAPLusParser.CompareBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#CompareBinaryExpr.
    def exitCompareBinaryExpr(self, ctx:TLAPLusParser.CompareBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetRelPassThrough.
    def enterSetRelPassThrough(self, ctx:TLAPLusParser.SetRelPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetRelPassThrough.
    def exitSetRelPassThrough(self, ctx:TLAPLusParser.SetRelPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetRelBinaryExpr.
    def enterSetRelBinaryExpr(self, ctx:TLAPLusParser.SetRelBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetRelBinaryExpr.
    def exitSetRelBinaryExpr(self, ctx:TLAPLusParser.SetRelBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#DotsBinaryExpr.
    def enterDotsBinaryExpr(self, ctx:TLAPLusParser.DotsBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#DotsBinaryExpr.
    def exitDotsBinaryExpr(self, ctx:TLAPLusParser.DotsBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#DotsPassThrough.
    def enterDotsPassThrough(self, ctx:TLAPLusParser.DotsPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#DotsPassThrough.
    def exitDotsPassThrough(self, ctx:TLAPLusParser.DotsPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#AddPassThrough.
    def enterAddPassThrough(self, ctx:TLAPLusParser.AddPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#AddPassThrough.
    def exitAddPassThrough(self, ctx:TLAPLusParser.AddPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#AddBinaryExpr.
    def enterAddBinaryExpr(self, ctx:TLAPLusParser.AddBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#AddBinaryExpr.
    def exitAddBinaryExpr(self, ctx:TLAPLusParser.AddBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#MultPassThrough.
    def enterMultPassThrough(self, ctx:TLAPLusParser.MultPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#MultPassThrough.
    def exitMultPassThrough(self, ctx:TLAPLusParser.MultPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#MultBinaryExpr.
    def enterMultBinaryExpr(self, ctx:TLAPLusParser.MultBinaryExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#MultBinaryExpr.
    def exitMultBinaryExpr(self, ctx:TLAPLusParser.MultBinaryExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#PrefixExpression.
    def enterPrefixExpression(self, ctx:TLAPLusParser.PrefixExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#PrefixExpression.
    def exitPrefixExpression(self, ctx:TLAPLusParser.PrefixExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#PrefixPassThrough.
    def enterPrefixPassThrough(self, ctx:TLAPLusParser.PrefixPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#PrefixPassThrough.
    def exitPrefixPassThrough(self, ctx:TLAPLusParser.PrefixPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#PostfixExpression.
    def enterPostfixExpression(self, ctx:TLAPLusParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#PostfixExpression.
    def exitPostfixExpression(self, ctx:TLAPLusParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#PostfixPassThrough.
    def enterPostfixPassThrough(self, ctx:TLAPLusParser.PostfixPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#PostfixPassThrough.
    def exitPostfixPassThrough(self, ctx:TLAPLusParser.PostfixPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ApplicationPassThrough.
    def enterApplicationPassThrough(self, ctx:TLAPLusParser.ApplicationPassThroughContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ApplicationPassThrough.
    def exitApplicationPassThrough(self, ctx:TLAPLusParser.ApplicationPassThroughContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#FunctionApplication.
    def enterFunctionApplication(self, ctx:TLAPLusParser.FunctionApplicationContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#FunctionApplication.
    def exitFunctionApplication(self, ctx:TLAPLusParser.FunctionApplicationContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ModulePrefixExpr.
    def enterModulePrefixExpr(self, ctx:TLAPLusParser.ModulePrefixExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ModulePrefixExpr.
    def exitModulePrefixExpr(self, ctx:TLAPLusParser.ModulePrefixExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#RecordFieldExpr.
    def enterRecordFieldExpr(self, ctx:TLAPLusParser.RecordFieldExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#RecordFieldExpr.
    def exitRecordFieldExpr(self, ctx:TLAPLusParser.RecordFieldExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#keywordAsIdentifier.
    def enterKeywordAsIdentifier(self, ctx:TLAPLusParser.KeywordAsIdentifierContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#keywordAsIdentifier.
    def exitKeywordAsIdentifier(self, ctx:TLAPLusParser.KeywordAsIdentifierContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#bangExtension.
    def enterBangExtension(self, ctx:TLAPLusParser.BangExtensionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#bangExtension.
    def exitBangExtension(self, ctx:TLAPLusParser.BangExtensionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#structOp.
    def enterStructOp(self, ctx:TLAPLusParser.StructOpContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#structOp.
    def exitStructOp(self, ctx:TLAPLusParser.StructOpContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#IdentifierExpression.
    def enterIdentifierExpression(self, ctx:TLAPLusParser.IdentifierExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#IdentifierExpression.
    def exitIdentifierExpression(self, ctx:TLAPLusParser.IdentifierExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#StringExpression.
    def enterStringExpression(self, ctx:TLAPLusParser.StringExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#StringExpression.
    def exitStringExpression(self, ctx:TLAPLusParser.StringExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#NumberExpression.
    def enterNumberExpression(self, ctx:TLAPLusParser.NumberExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#NumberExpression.
    def exitNumberExpression(self, ctx:TLAPLusParser.NumberExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ParenExpression.
    def enterParenExpression(self, ctx:TLAPLusParser.ParenExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ParenExpression.
    def exitParenExpression(self, ctx:TLAPLusParser.ParenExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetExpression.
    def enterSetExpression(self, ctx:TLAPLusParser.SetExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetExpression.
    def exitSetExpression(self, ctx:TLAPLusParser.SetExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#StandaloneBracketExpr.
    def enterStandaloneBracketExpr(self, ctx:TLAPLusParser.StandaloneBracketExprContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#StandaloneBracketExpr.
    def exitStandaloneBracketExpr(self, ctx:TLAPLusParser.StandaloneBracketExprContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#TupleOrActionExpression.
    def enterTupleOrActionExpression(self, ctx:TLAPLusParser.TupleOrActionExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#TupleOrActionExpression.
    def exitTupleOrActionExpression(self, ctx:TLAPLusParser.TupleOrActionExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ProofStepExpression.
    def enterProofStepExpression(self, ctx:TLAPLusParser.ProofStepExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ProofStepExpression.
    def exitProofStepExpression(self, ctx:TLAPLusParser.ProofStepExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#FairnessExprPrimary.
    def enterFairnessExprPrimary(self, ctx:TLAPLusParser.FairnessExprPrimaryContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#FairnessExprPrimary.
    def exitFairnessExprPrimary(self, ctx:TLAPLusParser.FairnessExprPrimaryContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#proofStepRef.
    def enterProofStepRef(self, ctx:TLAPLusParser.ProofStepRefContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#proofStepRef.
    def exitProofStepRef(self, ctx:TLAPLusParser.ProofStepRefContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#reducedExpression.
    def enterReducedExpression(self, ctx:TLAPLusParser.ReducedExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#reducedExpression.
    def exitReducedExpression(self, ctx:TLAPLusParser.ReducedExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetSubsetOf.
    def enterSetSubsetOf(self, ctx:TLAPLusParser.SetSubsetOfContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetSubsetOf.
    def exitSetSubsetOf(self, ctx:TLAPLusParser.SetSubsetOfContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetEnumerate.
    def enterSetEnumerate(self, ctx:TLAPLusParser.SetEnumerateContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetEnumerate.
    def exitSetEnumerate(self, ctx:TLAPLusParser.SetEnumerateContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetOfAll.
    def enterSetOfAll(self, ctx:TLAPLusParser.SetOfAllContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetOfAll.
    def exitSetOfAll(self, ctx:TLAPLusParser.SetOfAllContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#FunctionConstructor.
    def enterFunctionConstructor(self, ctx:TLAPLusParser.FunctionConstructorContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#FunctionConstructor.
    def exitFunctionConstructor(self, ctx:TLAPLusParser.FunctionConstructorContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#RecordConstructor.
    def enterRecordConstructor(self, ctx:TLAPLusParser.RecordConstructorContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#RecordConstructor.
    def exitRecordConstructor(self, ctx:TLAPLusParser.RecordConstructorContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetOfRecords.
    def enterSetOfRecords(self, ctx:TLAPLusParser.SetOfRecordsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetOfRecords.
    def exitSetOfRecords(self, ctx:TLAPLusParser.SetOfRecordsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#FunctionApplication2.
    def enterFunctionApplication2(self, ctx:TLAPLusParser.FunctionApplication2Context):
        pass

    # Exit a parse tree produced by TLAPLusParser#FunctionApplication2.
    def exitFunctionApplication2(self, ctx:TLAPLusParser.FunctionApplication2Context):
        pass


    # Enter a parse tree produced by TLAPLusParser#SetOfFunctions.
    def enterSetOfFunctions(self, ctx:TLAPLusParser.SetOfFunctionsContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#SetOfFunctions.
    def exitSetOfFunctions(self, ctx:TLAPLusParser.SetOfFunctionsContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ExceptExpression.
    def enterExceptExpression(self, ctx:TLAPLusParser.ExceptExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#ExceptExpression.
    def exitExceptExpression(self, ctx:TLAPLusParser.ExceptExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#ActionExpression2.
    def enterActionExpression2(self, ctx:TLAPLusParser.ActionExpression2Context):
        pass

    # Exit a parse tree produced by TLAPLusParser#ActionExpression2.
    def exitActionExpression2(self, ctx:TLAPLusParser.ActionExpression2Context):
        pass


    # Enter a parse tree produced by TLAPLusParser#fieldVal.
    def enterFieldVal(self, ctx:TLAPLusParser.FieldValContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#fieldVal.
    def exitFieldVal(self, ctx:TLAPLusParser.FieldValContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#fieldSet.
    def enterFieldSet(self, ctx:TLAPLusParser.FieldSetContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#fieldSet.
    def exitFieldSet(self, ctx:TLAPLusParser.FieldSetContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#exceptSpec.
    def enterExceptSpec(self, ctx:TLAPLusParser.ExceptSpecContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#exceptSpec.
    def exitExceptSpec(self, ctx:TLAPLusParser.ExceptSpecContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#exceptComponent.
    def enterExceptComponent(self, ctx:TLAPLusParser.ExceptComponentContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#exceptComponent.
    def exitExceptComponent(self, ctx:TLAPLusParser.ExceptComponentContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#quantBound.
    def enterQuantBound(self, ctx:TLAPLusParser.QuantBoundContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#quantBound.
    def exitQuantBound(self, ctx:TLAPLusParser.QuantBoundContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#tupleBody.
    def enterTupleBody(self, ctx:TLAPLusParser.TupleBodyContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#tupleBody.
    def exitTupleBody(self, ctx:TLAPLusParser.TupleBodyContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#fairnessExpression.
    def enterFairnessExpression(self, ctx:TLAPLusParser.FairnessExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#fairnessExpression.
    def exitFairnessExpression(self, ctx:TLAPLusParser.FairnessExpressionContext):
        pass


    # Enter a parse tree produced by TLAPLusParser#lambdaExpression.
    def enterLambdaExpression(self, ctx:TLAPLusParser.LambdaExpressionContext):
        pass

    # Exit a parse tree produced by TLAPLusParser#lambdaExpression.
    def exitLambdaExpression(self, ctx:TLAPLusParser.LambdaExpressionContext):
        pass



del TLAPLusParser