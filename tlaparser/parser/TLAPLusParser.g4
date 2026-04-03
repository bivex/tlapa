/*
 * ANTLR4 Parser Grammar for TLA+
 *
 * Converted from the official TLA+ JavaCC grammar (tla+.jj) at:
 * https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/javacc/tla%2B.jj
 *
 * Original Copyright (c) 2003 Compaq Corporation. All rights reserved.
 * Modifications by Leslie Lamport, J-Ch, and others.
 *
 * Key differences from the JavaCC grammar:
 * 1. Operator precedence is handled via ANTLR4's built-in left-recursive rules
 *    instead of a manual OperatorStack.
 * 2. The belchDEF() mechanism for injecting DEFBREAK tokens is removed;
 *    definition boundaries are determined by the parser structure.
 * 3. Semantic actions (AST construction) are deferred to Python listener/visitor code.
 */

parser grammar TLAPLusParser ;

options { tokenVocab=TLAPLusLexer; }

// ============================================================================
// Top-level structure
// ============================================================================

unit
    : firstModule module* EOF
    ;

firstModule
    : IDENTIFIER SEPARATOR extends? moduleBody endModule
    ;

module
    : SEPARATOR IDENTIFIER SEPARATOR extends? moduleBody endModule
    ;

endModule
    : END_MODULE
    ;

extends
    : EXTENDS_KW IDENTIFIER (COMMA IDENTIFIER)*
    ;

moduleBody
    : (   variableDeclaration
        | parameterDeclaration
        | operatorOrFunctionDefinition
        | recursiveDeclaration
        | instance
        | assumption
        | theorem
        | useOrHide
        | proof
      )*
    ;

// ============================================================================
// Declarations
// ============================================================================

variableDeclaration
    : VARIABLE_KW IDENTIFIER (COMMA IDENTIFIER)*
    ;

parameterDeclaration
    : CONSTANT_KW constantDeclItem (COMMA constantDeclItem)*
    ;

constantDeclItem
    : IDENTIFIER (LBR US (COMMA US)* RBR)?
    | prefixDecl
    | infixDecl
    | postfixDecl
    ;

prefixDecl
    : prefixOp US
    ;

infixDecl
    : US infixOp US
    ;

postfixDecl
    : US postfixOp
    ;

recursiveDeclaration
    : RECURSIVE_KW constantDeclItem (COMMA constantDeclItem)*
    ;

// ============================================================================
// Operator and Function Definitions
// ============================================================================

operatorOrFunctionDefinition
    : LOCAL_KW? (functionDefinition | operatorDefinition | moduleDefinition)
    ;

functionDefinition
    : (IDENTIFIER | identifierTuple) LSB quantBound (COMMA quantBound)* RSB DEF functionBody
    ;

operatorDefinition
    : identLhs DEF expression
    | prefixLhs DEF expression
    | infixLhs DEF expression
    | postfixLhs DEF expression
    ;

moduleDefinition
    : IDENTIFIER (LBR (constantDeclItem (COMMA constantDeclItem)*)? RBR)? DEF expression
    ;

identLhs
    : IDENTIFIER (LBR (constantDeclItem (COMMA constantDeclItem)*)? RBR)?
    ;

prefixLhs
    : nonExpPrefixOp IDENTIFIER
    ;

infixLhs
    : IDENTIFIER infixOp IDENTIFIER
    ;

postfixLhs
    : IDENTIFIER postfixOp
    ;

functionBody
    : expression
    ;

identifierTuple
    : LAB IDENTIFIER (COMMA IDENTIFIER)* RAB
    ;

// ============================================================================
// Instance
// ============================================================================

instance
    : LOCAL_KW? instantiation
    ;

instantiation
    : INSTANCE_KW IDENTIFIER (WITH_KW substitution (COMMA substitution)*)?
    ;

substitution
    : (IDENTIFIER | nonExpPrefixOp | infixOp | postfixOp) SUBSTITUTE opOrExpr
    ;

opOrExpr
    : nonExpPrefixOp
    | infixOp
    | postfixOp
    | lambdaExpression
    | expression
    ;

// ============================================================================
// Operators
// ============================================================================

prefixOp
    : LNOT
    | NEG
    | TILDE
    | DIAMOND
    | ENABLED_KW
    | UNCHANGED_KW
    | SUBSET_KW
    | UNION_KW
    | DOMAIN_KW
    ;

nonExpPrefixOp
    : DOT_NEG
    | prefixOp
    ;

infixOp
    : DOUBLE_SLASH
    | AND
    | NOT_EQUALS
    | SLASH
    | OR
    | APPROX
    | ASYMP
    | BIGCIRC
    | BULLET
    | CAP
    | CDOT
    | CIRC
    | CONG
    | CUP
    | DIV
    | DOTEQ
    | EQUIV
    | GEQ
    | GG
    | IN
    | INTERSECT
    | UNION_OP
    | LAND
    | LEQ
    | LL
    | LOR
    | ODOT
    | OMINUS
    | OPLUS
    | OSLASH
    | OTIMES
    | PREC
    | PRECEQ
    | PROPTO
    | SIM
    | SIMEQ
    | SQCAP
    | SQCUP
    | SQSUBSET
    | SQSUPSET
    | SQSUBSETEQ
    | SQSUPSETEQ
    | STAR
    | SUBSET_OP
    | SUBSETEQ
    | SUCC
    | SUCCEQ
    | SUPSET
    | SUPSETEQ
    | UPLUS
    | WR
    | LEADS_TO
    | IMPLIES
    | IMPLIED_BY
    | ASSERT
    | HASH_HASH
    | HASH
    | CARET_CARET
    | CARET
    | DASH_DASH
    | DASH_BAR
    | PLUS_ARROW
    | STAR_STAR
    | TIMES
    | PLUS_PLUS
    | PLUS
    | IFF
    | LTCOLON
    | LTEQ
    | LT
    | GTEQ
    | GT
    | DOTS3
    | DOTS2
    | BARBAR
    | BAR
    | DASHTURNSTILE
    | TURNSTILE
    | AMPAMP
    | AMP
    | DOLLARDOLLAR
    | DOLLAR
    | QUESQUES
    | PERCENTPERCENT
    | PERCENT
    | ATAT
    | EXCELEXCLAIM
    | COLONGT
    | COLONEQ
    | COLONEQCOLON
    | OPLUS_PAREN
    | OMINUS_PAREN
    | ODOT_PAREN
    | OSLASH_PAREN
    | OTIMES_PAREN
    | NOTIN
    | TIMES_KW
    | CROSS
    | EQUALS
    | BACKSLASH
    | DOT DOT  // ".." as DOT DOT? No, it's a single token DOTS2
    // Unicode variants
    | APPROX_UC | ASSIGN_UC | ASYMP_UC | BIGCIRC_UC | BNF_RULE_UC
    | BULLET_UC | CAP_UC | CDOT_UC | CIRC_UC | CONG_UC | CUP_UC
    | DIV_UC | DOTEQ_UC | DOTS2_UC | DOTS3_UC | EQUIV_UC | EXCL_UC
    | GEQ_UC | GG_UC | IFF_UC | IMPLIES_UC | LD_TTILE_UC | LEADS_TO_UC
    | LEQ_UC | LL_UC | LS_TTILE_UC | NEQ_UC | NOTIN_UC | ODOT_UC
    | OMINUS_UC | OPLUS_UC | OSLASH_UC | OTIMES_UC | PLUS_ARROW_UC
    | PREC_UC | PRECEQ_UC | PROPTO_UC | QQ_UC | RD_TTILE_UC | RS_TTILE_UC
    | SIM_UC | SIMEQ_UC | SQCAP_UC | SQCUP_UC | SQSUBSET_UC | SQSUBSETEQ_UC
    | SQSUPSET_UC | SQSUPSETEQ_UC | STAR_UC | SUBSET_UC | SUBSETEQ_UC
    | SUCC_UC | SUCCEQ_UC | SUPSET_UC | SUPSETEQ_UC | TIMES_UC | UPLUS_UC
    | VERTVERT_UC | WR_UC
    ;

postfixOp
    : PRIME
    | PLUS_SUP
    | STAR_SUP
    | HASH_SUP
    ;

// ============================================================================
// Assumptions and Theorems
// ============================================================================

assumeProve
    : (IDENTIFIER COLONCOLON assumeProve)?
      (ASSUME_KW | BOXASSUME_KW)
      (assumeProve | newSymb | expression)
      (COMMA (assumeProve | newSymb | expression))*
      (PROVE_KW | BOXPROVE_KW)
      expression
    ;

assumption
    : (ASSUMPTION_KW | ASSUME_KW) (IDENTIFIER DEF)? expression
    ;

newSymb
    : (NEW_KW? CONSTANT_KW | NEW_KW CONSTANT_KW)
      (identDecl (IN_KW expression)? | prefixDecl | infixDecl | postfixDecl)
    | (NEW_KW? VARIABLE_KW) IDENTIFIER
    | (NEW_KW?) (STATE_KW | ACTION_KW | TEMPORAL_KW) (identDecl | prefixDecl | infixDecl | postfixDecl)
    ;

identDecl
    : IDENTIFIER (LBR US (COMMA US)* RBR)?
    ;

theorem
    : (THEOREM_KW | PROPOSITION_KW) (IDENTIFIER DEF)?
      (assumeProve | expression)
      proof?
    ;

maybeBound
    : (IN expression)?
    ;

// ============================================================================
// Proofs
// ============================================================================

proof
    : terminalProof
    | (PROOF_KW)? (OBVIOUS_KW | OMITTED_KW)
    | (PROOF_KW)? step* qedStep
    ;

terminalProof
    : (PROOF_KW)? BY_KW ONLY_KW?
      ((MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
      (DF_KW (MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
    ;

useOrHide
    : (PROOF_KW)? BY_KW ONLY_KW?
      ((MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
      (DF_KW (MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
    | USE_KW ONLY_KW?
      ((MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
      (DF_KW (MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
    | HIDE_KW
      ((MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
      (DF_KW (MODULE_KW IDENTIFIER | expression) (COMMA (MODULE_KW IDENTIFIER | expression))*)?
    ;

stepStartToken
    : ProofStepLexeme
    | ProofImplicitStepLexeme
    | ProofStepDotLexeme
    | BareLevelLexeme
    | UnnumberedStepLexeme
    ;

step
    : stepStartToken
      ( useOrHide
      | instantiation
      | defStep
      | haveStep
      | takeStep
      | witnessStep
      | pickStep
      | caseStep
      | assertStep
      )
      proof?
    ;

qedStep
    : stepStartToken QED_KW proof?
    ;

defStep
    : DEFINE_KW? operatorOrFunctionDefinition+
    ;

haveStep
    : HAVE_KW expression
    ;

takeStep
    : TAKE_KW (quantBound (COMMA quantBound)* | IDENTIFIER (COMMA IDENTIFIER)*)
    ;

witnessStep
    : WITNESS_KW expression (COMMA expression)*
    ;

pickStep
    : PICK_KW
      ( IDENTIFIER (COMMA IDENTIFIER)*
      | quantBound (COMMA quantBound)*
      )
      COLON expression
    ;

caseStep
    : CASE_KW expression
    ;

assertStep
    : SUFFICES_KW? (expression | assumeProve)
    ;

// ============================================================================
// Expressions - using ANTLR4 operator precedence
// ============================================================================

/*
 * Expression parsing uses ANTLR4's built-in left-recursive operator
 * precedence mechanism.  The alternatives are ordered from lowest to
 * highest precedence, following the TLA+ operator precedence table.
 *
 * Precedence (lowest to highest):
 *  1. Equiv-like: <=>, \equiv, ≡
 *  2. Implies: =>, -+->, ~>
 *  3. Or: \/, ∨, ∨
 *  4. And: /\, ∧, ∧
 *  5. Equality-like: =, /=, #, ##, ≠
 *  6. Comparison: <, <=, >, >=, \prec, \preceq, \succ, \succeq, etc.
 *  7. Set relations: \in, \notin, ∉, ∈, \subset, \subseteq, etc.
 *  8. Shift-like: .., ..., ‥, …
 *  9. Additive: +, -, ++, --, \oplus, \ominus, \uplus, \sqcup, etc.
 *  10. Multiplicative: *, /, \div, \cdot, \circ, \star, \otimes, etc.
 *  11. Prefix: ~, \lnot, ¬, \neg, DOMAIN, SUBSET, UNION, ENABLED, UNCHANGED, [], <>
 *  12. Postfix: ', ^+, ^*, ^#, ^
 *  13. Application: [expr], !, .
 *
 * Note: The original JavaCC grammar uses a manual OperatorStack.
 * Here we use ANTLR4's left-recursive rule with inline precedence.
 */

expression
    : <assoc=right> quantifierExpr
    ;

quantifierExpr
    : (EXISTS_KW | FORALL_KW)
      (IDENTIFIER (COMMA IDENTIFIER)* | quantBound (COMMA quantBound)*)
      COLON quantifierExpr                                                          #QuantifierExpression
    | (T_EXISTS_KW | T_FORALL_KW) IDENTIFIER (COMMA IDENTIFIER)* COLON quantifierExpr #TemporalQuantifierExpression
    | chooseExpr                                                                    #QuantifierPassThrough
    ;

chooseExpr
    : CHOOSE_KW (IDENTIFIER | identifierTuple) maybeBound COLON chooseExpr         #ChooseExpression
    | ifExpr                                                                        #ChoosePassThrough
    ;

ifExpr
    : IF_KW ifExpr THEN_KW ifExpr ELSE_KW ifExpr                                   #IfThenElseExpression
    | caseExpr                                                                      #IfPassThrough
    ;

caseExpr
    : CASE_KW caseArm (BOX caseArm)* (BOX otherArm)?                                #CaseExpression
    | letExpr                                                                       #CasePassThrough
    ;

caseArm
    : expression ARROW expression
    ;

otherArm
    : OTHER_KW ARROW expression
    ;

letExpr
    : LET_KW letDefinition+ IN_KW letExpr                                          #LetInExpression
    | equivExpr                                                                     #LetPassThrough
    ;

letDefinition
    : operatorOrFunctionDefinition
    | recursiveDeclaration
    ;

// Precedence level 1: Equivalence
equivExpr
    : <assoc=right> equivExpr (EQUIV | EQUIV_UC | IFF | IFF_UC) impliesExpr        #EquivBinaryExpr
    | impliesExpr                                                                   #EquivPassThrough
    ;

// Precedence level 2: Implication
impliesExpr
    : <assoc=right> impliesExpr (IMPLIES | IMPLIES_UC | PLUS_ARROW | LEADS_TO | LEADS_TO_UC) orExpr  #ImpliesBinaryExpr
    | orExpr                                                                        #ImpliesPassThrough
    ;

// Precedence level 3: Disjunction
orExpr
    : orExpr (OR | LOR) andExpr                                                #OrBinaryExpr
    | junctionExpr                                                                  #OrPassThrough
    ;

// Precedence level 4: Conjunction
andExpr
    : andExpr (AND | LAND) junctionExpr                                         #AndBinaryExpr
    | junctionExpr                                                                  #AndPassThrough
    ;

// Bulleted junctions (/\, \/ at start of line)
junctionExpr
    : AND expression (AND expression)*                                                   #ConjunctionList
    | OR expression (OR expression)*                                                    #DisjunctionList
    | equalityExpr                                                                      #JunctionPassThrough
    ;

// Precedence level 5: Equality-like
equalityExpr
    : equalityExpr (EQUALS | NOT_EQUALS | HASH | HASH_HASH | NEQ_UC | ASSERT | ASSIGN_UC) compareExpr  #EqualityBinaryExpr
    | compareExpr                                                                   #EqualityPassThrough
    ;

// Precedence level 6: Comparison
compareExpr
    : compareExpr (LT | LTEQ | GT | GTEQ | PREC | PRECEQ | SUCC | SUCCEQ
                   | PREC_UC | PRECEQ_UC | SUCC_UC | SUCCEQ_UC | LL | LL_UC | GG | GG_UC
                   | SIM | SIM_UC | SIMEQ | SIMEQ_UC | APPROX | APPROX_UC | ASYMP | ASYMP_UC
                   | SQSUBSET | SQSUBSET_UC | SQSUPSET | SQSUPSET_UC
                   | SQSUBSETEQ | SQSUBSETEQ_UC | SQSUPSETEQ | SQSUPSETEQ_UC
                   | DASH_BAR | RS_TTILE_UC | DASHTURNSTILE | TURNSTILE | RD_TTILE_UC
                   | LD_TTILE_UC | LS_TTILE_UC) setRelExpr                          #CompareBinaryExpr
    | setRelExpr                                                                    #ComparePassThrough
    ;

// Precedence level 7: Set relations
setRelExpr
    : setRelExpr (IN | IN | NOTIN | NOTIN_UC | SUBSET_OP | SUBSET_UC
                 | SUBSETEQ | SUBSETEQ_UC | SUPSET | SUPSET_UC
                 | SUPSETEQ | SUPSETEQ_UC | PROPTO | PROPTO_UC) dotsExpr           #SetRelBinaryExpr
    | dotsExpr                                                                      #SetRelPassThrough
    ;

// Precedence level 8: Dots
dotsExpr
    : dotsExpr (DOTS2 | DOTS3 | DOTS2_UC | DOTS3_UC) addExpr                        #DotsBinaryExpr
    | addExpr                                                                       #DotsPassThrough
    ;

// Precedence level 9: Additive
addExpr
    : addExpr (PLUS | PLUS_PLUS | MINUS | DASH_DASH | OPLUS | OPLUS_UC | OMINUS | OMINUS_UC
              | UPLUS | UPLUS_UC | SQCUP | SQCUP_UC | SQCAP | SQCAP_UC
              | CAP | CAP_UC | CUP | CUP_UC | BACKSLASH | WR | WR_UC
              | OR | LAND | LOR | AND
              | OPLUS_PAREN | OMINUS_PAREN) multExpr                                 #AddBinaryExpr
    | multExpr                                                                       #AddPassThrough
    ;

// Precedence level 10: Multiplicative
multExpr
    : multExpr (TIMES | TIMES_UC | SLASH | DIV | DIV_UC | CDOT | CDOT_UC
               | CIRC | CIRC_UC | STAR | STAR_UC | STAR_STAR
               | OTIMES | OTIMES_UC | OSLASH | OSLASH_UC | ODOT | ODOT_UC
               | INTERSECT | UNION_OP
               | OTIMES_PAREN | OSLASH_PAREN | ODOT_PAREN
               | DOUBLE_SLASH) prefixExpr                                            #MultBinaryExpr
    | prefixExpr                                                                     #MultPassThrough
    ;

// Prefix operators
prefixExpr
    : (TILDE | LNOT | NEG | DIAMOND | BOX
       | ENABLED_KW | UNCHANGED_KW | SUBSET_KW | UNION_KW | DOMAIN_KW
       | DOT_NEG) prefixExpr                                                         #PrefixExpression
    | postfixExpr                                                                     #PrefixPassThrough
    ;

// Postfix operators
postfixExpr
    : postfixExpr (PRIME | PLUS_SUP | STAR_SUP | HASH_SUP)                             #PostfixExpression
    | applicationExpr                                                                  #PostfixPassThrough
    ;

// Function application and module prefix (!)
applicationExpr
    : applicationExpr (LSB expression (COMMA expression)* RSB)                         #FunctionApplication
    | applicationExpr BANG bangExtension                                               #ModulePrefixExpr
    | applicationExpr DOT (IDENTIFIER | keywordAsIdentifier)                           #RecordFieldExpr
    | primaryExpression                                                                #ApplicationPassThrough
    ;

// Keywords that can be used as field names in records
keywordAsIdentifier
    : ACTION_KW | EXCEPT_KW | EXTENDS_KW | IF_KW | IN_KW | INSTANCE_KW
    | LET_KW | SF_KW | THEN_KW | WITH_KW | STATE_KW | ENABLED_KW | UNCHANGED_KW
    | SUBSET_KW | UNION_KW | DOMAIN_KW
    ;

bangExtension
    : (  IDENTIFIER
       | nonExpPrefixOp
       | infixOp
       | postfixOp
      ) (LBR opOrExpr (COMMA opOrExpr)* RBR)?
    | LBR opOrExpr (COMMA opOrExpr)* RBR
    | structOp
    ;

structOp
    : LAB | RAB | COLON | ATAT | NUMBER_LITERAL
    ;

// ============================================================================
// Primary expressions
// ============================================================================

primaryExpression
    : IDENTIFIER (LBR opOrExpr (COMMA opOrExpr)* RBR)?                                #IdentifierExpression
    | STRING_LITERAL                                                                   #StringExpression
    | NUMBER_LITERAL (DOT NUMBER_LITERAL)?                                             #NumberExpression
    | LBR expression RBR                                                               #ParenExpression
    | LBC setBody RBC                                                                  #SetExpression
    | LSB functionBody2 RSB                                                            #StandaloneBracketExpr
    | LAB tupleBody (RAB | ARAB reducedExpression)                                     #TupleOrActionExpression
    | proofStepRef (LBR opOrExpr (COMMA opOrExpr)* RBR)?                               #ProofStepExpression
    | fairnessExpression                                                               #FairnessExprPrimary
    ;

proofStepRef
    : ProofStepLexeme
    | ProofImplicitStepLexeme
    ;

reducedExpression
    : IDENTIFIER (LBR opOrExpr (COMMA opOrExpr)* RBR)?
      (BANG bangExtension)*
    | LBR expression RBR
    | LBC setBody RBC
    | LSB functionBody2 RSB
    | LAB tupleBody (RAB | ARAB reducedExpression)
    ;

// ============================================================================
// Set expressions
// ============================================================================

setBody
    : (identifierTuple | IDENTIFIER) IN expression COLON expression                    #SetSubsetOf
    | expression (COMMA expression)*                                                   #SetEnumerate
    | expression COLON quantBound (COMMA quantBound)*                                  #SetOfAll
    ;

// ============================================================================
// Bracket expressions (functions, records, except, etc.)
// ============================================================================

functionBody2
    : quantBound (COMMA quantBound)* MAPTO expression                                   #FunctionConstructor
    | fieldVal (COMMA fieldVal)*                                                        #RecordConstructor
    | fieldSet (COMMA fieldSet)*                                                        #SetOfRecords
    | expression (COMMA expression)*                                                    #FunctionApplication2
    | expression ARROW expression                                                       #SetOfFunctions
    | expression EXCEPT_KW exceptSpec (COMMA exceptSpec)*                               #ExceptExpression
    | expression ARSB reducedExpression                                                 #ActionExpression2
    ;

fieldVal
    : IDENTIFIER MAPTO expression
    ;

fieldSet
    : IDENTIFIER COLON expression
    ;

exceptSpec
    : BANG exceptComponent+ EQUALS expression
    ;

exceptComponent
    : DOT (IDENTIFIER | keywordAsIdentifier)
    | LSB expression (COMMA expression)* RSB
    ;

quantBound
    : (identifierTuple | IDENTIFIER (COMMA IDENTIFIER)*) IN expression
    ;

// ============================================================================
// Tuple and fairness expressions
// ============================================================================

tupleBody
    : (expression (COMMA expression)*)?
    ;

fairnessExpression
    : (WF_KW | SF_KW) reducedExpression (LBR expression RBR)?
    ;

// ============================================================================
// Lambda
// ============================================================================

lambdaExpression
    : LAMBDA_KW IDENTIFIER (COMMA IDENTIFIER)* COLON expression
    ;
