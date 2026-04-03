# Generated from TLAPLusParser.g4 by ANTLR 4.13.1
from antlr4 import *
if "." in __name__:
    from .TLAPLusParser import TLAPLusParser
else:
    from TLAPLusParser import TLAPLusParser

# This class defines a complete generic visitor for a parse tree produced by TLAPLusParser.

class TLAPLusParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TLAPLusParser#unit.
    def visitUnit(self, ctx:TLAPLusParser.UnitContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#module.
    def visitModule(self, ctx:TLAPLusParser.ModuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#beginModule.
    def visitBeginModule(self, ctx:TLAPLusParser.BeginModuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#endModule.
    def visitEndModule(self, ctx:TLAPLusParser.EndModuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#extends.
    def visitExtends(self, ctx:TLAPLusParser.ExtendsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#moduleBody.
    def visitModuleBody(self, ctx:TLAPLusParser.ModuleBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:TLAPLusParser.VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#parameterDeclaration.
    def visitParameterDeclaration(self, ctx:TLAPLusParser.ParameterDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#constantDeclItem.
    def visitConstantDeclItem(self, ctx:TLAPLusParser.ConstantDeclItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#prefixDecl.
    def visitPrefixDecl(self, ctx:TLAPLusParser.PrefixDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#infixDecl.
    def visitInfixDecl(self, ctx:TLAPLusParser.InfixDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#postfixDecl.
    def visitPostfixDecl(self, ctx:TLAPLusParser.PostfixDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#recursiveDeclaration.
    def visitRecursiveDeclaration(self, ctx:TLAPLusParser.RecursiveDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#operatorOrFunctionDefinition.
    def visitOperatorOrFunctionDefinition(self, ctx:TLAPLusParser.OperatorOrFunctionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#functionDefinition.
    def visitFunctionDefinition(self, ctx:TLAPLusParser.FunctionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#operatorDefinition.
    def visitOperatorDefinition(self, ctx:TLAPLusParser.OperatorDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#moduleDefinition.
    def visitModuleDefinition(self, ctx:TLAPLusParser.ModuleDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#identLhs.
    def visitIdentLhs(self, ctx:TLAPLusParser.IdentLhsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#prefixLhs.
    def visitPrefixLhs(self, ctx:TLAPLusParser.PrefixLhsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#infixLhs.
    def visitInfixLhs(self, ctx:TLAPLusParser.InfixLhsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#postfixLhs.
    def visitPostfixLhs(self, ctx:TLAPLusParser.PostfixLhsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#functionBody.
    def visitFunctionBody(self, ctx:TLAPLusParser.FunctionBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#identifierTuple.
    def visitIdentifierTuple(self, ctx:TLAPLusParser.IdentifierTupleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#instance.
    def visitInstance(self, ctx:TLAPLusParser.InstanceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#instantiation.
    def visitInstantiation(self, ctx:TLAPLusParser.InstantiationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#substitution.
    def visitSubstitution(self, ctx:TLAPLusParser.SubstitutionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#opOrExpr.
    def visitOpOrExpr(self, ctx:TLAPLusParser.OpOrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#prefixOp.
    def visitPrefixOp(self, ctx:TLAPLusParser.PrefixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#nonExpPrefixOp.
    def visitNonExpPrefixOp(self, ctx:TLAPLusParser.NonExpPrefixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#infixOp.
    def visitInfixOp(self, ctx:TLAPLusParser.InfixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#postfixOp.
    def visitPostfixOp(self, ctx:TLAPLusParser.PostfixOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#assumeProve.
    def visitAssumeProve(self, ctx:TLAPLusParser.AssumeProveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#assumption.
    def visitAssumption(self, ctx:TLAPLusParser.AssumptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#newSymb.
    def visitNewSymb(self, ctx:TLAPLusParser.NewSymbContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#identDecl.
    def visitIdentDecl(self, ctx:TLAPLusParser.IdentDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#theorem.
    def visitTheorem(self, ctx:TLAPLusParser.TheoremContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#maybeBound.
    def visitMaybeBound(self, ctx:TLAPLusParser.MaybeBoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#proof.
    def visitProof(self, ctx:TLAPLusParser.ProofContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#terminalProof.
    def visitTerminalProof(self, ctx:TLAPLusParser.TerminalProofContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#useOrHide.
    def visitUseOrHide(self, ctx:TLAPLusParser.UseOrHideContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#stepStartToken.
    def visitStepStartToken(self, ctx:TLAPLusParser.StepStartTokenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#step.
    def visitStep(self, ctx:TLAPLusParser.StepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#qedStep.
    def visitQedStep(self, ctx:TLAPLusParser.QedStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#defStep.
    def visitDefStep(self, ctx:TLAPLusParser.DefStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#haveStep.
    def visitHaveStep(self, ctx:TLAPLusParser.HaveStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#takeStep.
    def visitTakeStep(self, ctx:TLAPLusParser.TakeStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#witnessStep.
    def visitWitnessStep(self, ctx:TLAPLusParser.WitnessStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#pickStep.
    def visitPickStep(self, ctx:TLAPLusParser.PickStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#caseStep.
    def visitCaseStep(self, ctx:TLAPLusParser.CaseStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#assertStep.
    def visitAssertStep(self, ctx:TLAPLusParser.AssertStepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#expression.
    def visitExpression(self, ctx:TLAPLusParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#QuantifierExpression.
    def visitQuantifierExpression(self, ctx:TLAPLusParser.QuantifierExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#TemporalQuantifierExpression.
    def visitTemporalQuantifierExpression(self, ctx:TLAPLusParser.TemporalQuantifierExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#QuantifierPassThrough.
    def visitQuantifierPassThrough(self, ctx:TLAPLusParser.QuantifierPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ChooseExpression.
    def visitChooseExpression(self, ctx:TLAPLusParser.ChooseExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ChoosePassThrough.
    def visitChoosePassThrough(self, ctx:TLAPLusParser.ChoosePassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#IfThenElseExpression.
    def visitIfThenElseExpression(self, ctx:TLAPLusParser.IfThenElseExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#IfPassThrough.
    def visitIfPassThrough(self, ctx:TLAPLusParser.IfPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#CaseExpression.
    def visitCaseExpression(self, ctx:TLAPLusParser.CaseExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#CasePassThrough.
    def visitCasePassThrough(self, ctx:TLAPLusParser.CasePassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#caseArm.
    def visitCaseArm(self, ctx:TLAPLusParser.CaseArmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#otherArm.
    def visitOtherArm(self, ctx:TLAPLusParser.OtherArmContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#LetInExpression.
    def visitLetInExpression(self, ctx:TLAPLusParser.LetInExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#LetPassThrough.
    def visitLetPassThrough(self, ctx:TLAPLusParser.LetPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#letDefinition.
    def visitLetDefinition(self, ctx:TLAPLusParser.LetDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#EquivPassThrough.
    def visitEquivPassThrough(self, ctx:TLAPLusParser.EquivPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#EquivBinaryExpr.
    def visitEquivBinaryExpr(self, ctx:TLAPLusParser.EquivBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ImpliesBinaryExpr.
    def visitImpliesBinaryExpr(self, ctx:TLAPLusParser.ImpliesBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ImpliesPassThrough.
    def visitImpliesPassThrough(self, ctx:TLAPLusParser.ImpliesPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#OrBinaryExpr.
    def visitOrBinaryExpr(self, ctx:TLAPLusParser.OrBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#OrPassThrough.
    def visitOrPassThrough(self, ctx:TLAPLusParser.OrPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#AndPassThrough.
    def visitAndPassThrough(self, ctx:TLAPLusParser.AndPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#AndBinaryExpr.
    def visitAndBinaryExpr(self, ctx:TLAPLusParser.AndBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ConjunctionList.
    def visitConjunctionList(self, ctx:TLAPLusParser.ConjunctionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#DisjunctionList.
    def visitDisjunctionList(self, ctx:TLAPLusParser.DisjunctionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#JunctionPassThrough.
    def visitJunctionPassThrough(self, ctx:TLAPLusParser.JunctionPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#junctionItem.
    def visitJunctionItem(self, ctx:TLAPLusParser.JunctionItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#EqualityBinaryExpr.
    def visitEqualityBinaryExpr(self, ctx:TLAPLusParser.EqualityBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#EqualityPassThrough.
    def visitEqualityPassThrough(self, ctx:TLAPLusParser.EqualityPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ComparePassThrough.
    def visitComparePassThrough(self, ctx:TLAPLusParser.ComparePassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#CompareBinaryExpr.
    def visitCompareBinaryExpr(self, ctx:TLAPLusParser.CompareBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetRelPassThrough.
    def visitSetRelPassThrough(self, ctx:TLAPLusParser.SetRelPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetRelBinaryExpr.
    def visitSetRelBinaryExpr(self, ctx:TLAPLusParser.SetRelBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#DotsBinaryExpr.
    def visitDotsBinaryExpr(self, ctx:TLAPLusParser.DotsBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#DotsPassThrough.
    def visitDotsPassThrough(self, ctx:TLAPLusParser.DotsPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#AddPassThrough.
    def visitAddPassThrough(self, ctx:TLAPLusParser.AddPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#AddBinaryExpr.
    def visitAddBinaryExpr(self, ctx:TLAPLusParser.AddBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#MultPassThrough.
    def visitMultPassThrough(self, ctx:TLAPLusParser.MultPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#MultBinaryExpr.
    def visitMultBinaryExpr(self, ctx:TLAPLusParser.MultBinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#PrefixExpression.
    def visitPrefixExpression(self, ctx:TLAPLusParser.PrefixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#PrefixPassThrough.
    def visitPrefixPassThrough(self, ctx:TLAPLusParser.PrefixPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#PostfixExpression.
    def visitPostfixExpression(self, ctx:TLAPLusParser.PostfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#PostfixPassThrough.
    def visitPostfixPassThrough(self, ctx:TLAPLusParser.PostfixPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ApplicationPassThrough.
    def visitApplicationPassThrough(self, ctx:TLAPLusParser.ApplicationPassThroughContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#FunctionApplication.
    def visitFunctionApplication(self, ctx:TLAPLusParser.FunctionApplicationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ModulePrefixExpr.
    def visitModulePrefixExpr(self, ctx:TLAPLusParser.ModulePrefixExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#RecordFieldExpr.
    def visitRecordFieldExpr(self, ctx:TLAPLusParser.RecordFieldExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#keywordAsIdentifier.
    def visitKeywordAsIdentifier(self, ctx:TLAPLusParser.KeywordAsIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#bangExtension.
    def visitBangExtension(self, ctx:TLAPLusParser.BangExtensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#structOp.
    def visitStructOp(self, ctx:TLAPLusParser.StructOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#IdentifierExpression.
    def visitIdentifierExpression(self, ctx:TLAPLusParser.IdentifierExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#StringExpression.
    def visitStringExpression(self, ctx:TLAPLusParser.StringExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#NumberExpression.
    def visitNumberExpression(self, ctx:TLAPLusParser.NumberExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ParenExpression.
    def visitParenExpression(self, ctx:TLAPLusParser.ParenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetExpression.
    def visitSetExpression(self, ctx:TLAPLusParser.SetExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#TemporalActionExpression.
    def visitTemporalActionExpression(self, ctx:TLAPLusParser.TemporalActionExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#StandaloneBracketExpr.
    def visitStandaloneBracketExpr(self, ctx:TLAPLusParser.StandaloneBracketExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#TupleOrActionExpression.
    def visitTupleOrActionExpression(self, ctx:TLAPLusParser.TupleOrActionExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ProofStepExpression.
    def visitProofStepExpression(self, ctx:TLAPLusParser.ProofStepExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#FairnessExprPrimary.
    def visitFairnessExprPrimary(self, ctx:TLAPLusParser.FairnessExprPrimaryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#proofStepRef.
    def visitProofStepRef(self, ctx:TLAPLusParser.ProofStepRefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#reducedExpression.
    def visitReducedExpression(self, ctx:TLAPLusParser.ReducedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetSubsetOf.
    def visitSetSubsetOf(self, ctx:TLAPLusParser.SetSubsetOfContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetEnumerate.
    def visitSetEnumerate(self, ctx:TLAPLusParser.SetEnumerateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetOfAll.
    def visitSetOfAll(self, ctx:TLAPLusParser.SetOfAllContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#FunctionConstructor.
    def visitFunctionConstructor(self, ctx:TLAPLusParser.FunctionConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#RecordConstructor.
    def visitRecordConstructor(self, ctx:TLAPLusParser.RecordConstructorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetOfRecords.
    def visitSetOfRecords(self, ctx:TLAPLusParser.SetOfRecordsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#FunctionApplication2.
    def visitFunctionApplication2(self, ctx:TLAPLusParser.FunctionApplication2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#SetOfFunctions.
    def visitSetOfFunctions(self, ctx:TLAPLusParser.SetOfFunctionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ExceptExpression.
    def visitExceptExpression(self, ctx:TLAPLusParser.ExceptExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#ActionExpression2.
    def visitActionExpression2(self, ctx:TLAPLusParser.ActionExpression2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#fieldVal.
    def visitFieldVal(self, ctx:TLAPLusParser.FieldValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#fieldSet.
    def visitFieldSet(self, ctx:TLAPLusParser.FieldSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#exceptSpec.
    def visitExceptSpec(self, ctx:TLAPLusParser.ExceptSpecContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#exceptComponent.
    def visitExceptComponent(self, ctx:TLAPLusParser.ExceptComponentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#quantBound.
    def visitQuantBound(self, ctx:TLAPLusParser.QuantBoundContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#tupleBody.
    def visitTupleBody(self, ctx:TLAPLusParser.TupleBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#fairnessExpression.
    def visitFairnessExpression(self, ctx:TLAPLusParser.FairnessExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TLAPLusParser#lambdaExpression.
    def visitLambdaExpression(self, ctx:TLAPLusParser.LambdaExpressionContext):
        return self.visitChildren(ctx)



del TLAPLusParser