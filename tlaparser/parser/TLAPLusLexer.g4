/*
 * ANTLR4 Lexer Grammar for TLA+
 *
 * Converted from the official TLA+ JavaCC grammar (tla+.jj) at:
 * https://github.com/tlaplus/tlaplus/blob/master/tlatools/org.lamport.tlatools/javacc/tla%2B.jj
 *
 * Original Copyright (c) 2003 Compaq Corporation. All rights reserved.
 * Modifications by Leslie Lamport, J-Ch, and others.
 */

lexer grammar TLAPLusLexer;

// ============================================================================
// Fragments (hidden token patterns from JavaCC)
// ============================================================================

fragment LETTER : [a-zA-Z] ;
fragment DIGIT  : [0-9] ;
fragment NUMBER_SET : [\u2115\u2124\u211D] ; // ℕ | ℤ | ℝ

// Identifiers starting with underscore followed by letters/digits
fragment CASE0 : '_' (LETTER | '_' | DIGIT)* LETTER (LETTER | '_' | DIGIT)* ;

// Identifiers starting with digit followed by letters
fragment CASE1 : DIGIT (LETTER | '_' | DIGIT)* LETTER (LETTER | '_' | DIGIT)* ;

// Junction-like identifiers: digit prefix with .\/ or ./\
fragment CASE1b : DIGIT (LETTER | DIGIT)* '.' '\\/' ;
fragment CASE1c : DIGIT (LETTER | DIGIT)* '.' './\\' ;
fragment CASE1c_expr : DIGIT (LETTER | DIGIT)* '.' './' ;

// Identifiers starting with W or S (but not WF or SF)
fragment CASE2 : [WS] ([a-zA-EG-Z_0-9])? (LETTER | '_' | DIGIT)* ;
fragment CASE2b : [WS] ([a-zA-EG-Z0-9])? (LETTER | DIGIT)* '.' '\\/' ;
fragment CASE2c : [WS] ([a-zA-EG-Z0-9])? (LETTER | DIGIT)* '.' './\\' ;

// WF_ and SF_ identifiers
fragment CASE3 : ('WF' | 'SF') ((LETTER | DIGIT) (LETTER | '_' | DIGIT)*)? ;

// Standard identifiers (letters not starting with W, S, U, or reserved)
fragment CASE6 : [a-zA-EG-Z] (LETTER | '_' | DIGIT)* ;
fragment CASE6b : [a-zA-EG-Z] (LETTER | DIGIT)* '.' '\\/' ;
fragment CASE6c : [a-zA-EG-Z] (LETTER | DIGIT)* '.' './\\' ;

// Number followed by letter identifier
fragment CASEN : DIGIT+ LETTER (LETTER | DIGIT | '_')* ;

// ============================================================================
// Default mode: scan for module start or pragma
// ============================================================================

// Module header marker: ---- ... MODULE
BEGIN_MODULE : '----' '-'* ' '* 'MODULE' -> mode(SPEC_MODE) ;
BEGIN_PRAGMA : '--->' -> mode(PRAGMA_MODE) ;

// Skip everything else in default mode
DEFAULT_SKIP : . -> skip ;

// ============================================================================
// SPEC mode: main TLA+ specification parsing
// ============================================================================

mode SPEC_MODE ;

// Skip whitespace
SPEC_SKIP : [ \t\n\r] -> skip ;

// Comments
fragment BLOCK_COMMENT_START : '(*.' | '(*' ;
SPEC_BLOCK_COMMENT_OPEN : BLOCK_COMMENT_START -> pushMode(IN_COMMENT_MODE) ;
SPEC_LINE_COMMENT : '\\*' -> pushMode(IN_EOL_COMMENT_MODE) ;

// Structural markers
SEPARATOR : '----' '-'* ;
END_MODULE : '====' '='* ;

// Keywords
ACTION_KW    : 'ACTION' | 'ACTIONS' ;
ASSUME_KW    : 'ASSUME' ;
BOXASSUME_KW : '[]ASSUME' ;
ASSUMPTION_KW: 'ASSUMPTION' | 'AXIOM' ;
CASE_KW      : 'CASE' ;
CHOOSE_KW    : 'CHOOSE' ;
CONSTANT_KW  : 'CONSTANT' | 'CONSTANTS' ;
ELSE_KW      : 'ELSE' ;
EXCEPT_KW    : 'EXCEPT' ;
EXISTS_KW    : '\\E' | '\\exists' | '\u2203' ; // ∃
EXTENDS_KW   : 'EXTENDS' ;
FORALL_KW    : '\\A' | '\\forall' | '\u2200' ; // ∀
IF_KW        : 'IF' ;
INSTANCE_KW  : 'INSTANCE' ;
LET_KW       : 'LET' ;
IN_KW        : 'IN' ;
LOCAL_KW     : 'LOCAL' ;
MODULE_KW    : 'MODULE' ;
NEW_KW       : 'NEW' ;
OTHER_KW     : 'OTHER' ;
PROPOSITION_KW : 'PROPOSITION' | 'LEMMA' | 'COROLLARY' ;
SF_KW        : 'SF_' ;
T_EXISTS_KW  : '\\EE' ;
T_FORALL_KW  : '\\AA' ;
THEN_KW      : 'THEN' ;
BY_KW        : 'BY' ;
ONLY_KW      : 'ONLY' ;
DEFINE_KW    : 'DEFINE' ;
DF_KW        : 'DEF' | 'DEFS' ;
THEOREM_KW   : 'THEOREM' ;
USE_KW       : 'USE' ;
HIDE_KW      : 'HIDE' ;
HAVE_KW      : 'HAVE' ;
OBVIOUS_KW   : 'OBVIOUS' ;
OMITTED_KW   : 'OMITTED' ;
LAMBDA_KW    : 'LAMBDA' ;
TAKE_KW      : 'TAKE' ;
PROOF_KW     : 'PROOF' ;
PROVE_KW     : 'PROVE' ;
BOXPROVE_KW  : '[]PROVE' ;
QED_KW       : 'QED' ;
RECURSIVE_KW : 'RECURSIVE' ;
STATE_KW     : 'STATE' ;
TEMPORAL_KW  : 'TEMPORAL' | 'TEMPORALS' ;
PICK_KW      : 'PICK' ;
WITNESS_KW   : 'WITNESS' ;
SUFFICES_KW  : 'SUFFICES' ;
VARIABLE_KW  : 'VARIABLE' | 'VARIABLES' ;
WF_KW        : 'WF_' ;
WITH_KW      : 'WITH' ;

// Delimiters
COMMA       : ',' ;
COLON       : ':' ;
COLONCOLON  : '::' | '\u2237' ; // ∷
DOT         : '.' ;
US          : '_' ;
DEF         : '==' | '\u225c' ; // ≜
LBR         : '(' ;
RBR         : ')' ;
LSB         : '[' ;
ARSB        : ']_' ;
RSB         : ']' ;
LBC         : '{' ;
RBC         : '}' ;
LAB         : '<<' | '\u27e8' ; // ⟨
ARAB        : '>>_' | '\u27e9_' ; // ⟩_
RAB         : '>>' | '\u27e9' ; // ⟩
BANG        : '!' ;
ARROW       : '->' | '\u2192' ; // →
SUBSTITUTE  : '<-' | '\u2190' ; // ←
MAPTO       : '|->' | '\u21a6' ; // ↦
EQUALS      : '=' ;

// Fictitious token injected by belchDEF (not in actual input)
// DEFBREAK is handled differently in ANTLR - we don't emit it from the lexer

// Literals
NUMBER_LITERAL
    : DIGIT+
    | '0'
    | '\\' [oO] [0-7]+
    | '\\' [bB] [01]+
    | '\\' [hH] [0-9a-fA-F]+
    ;

STRING_LITERAL
    : '"' (~["\n\r\\] | '\\' [ntrf\\"])* '"'
    ;

// Junction tokens (bulleted lists)
// These are identifiers ending in .\/ or ./\ 
// We handle them as special identifier forms
BAND : BAND_FRAG ;
BOR  : BOR_FRAG ;

fragment BAND_FRAG
    : (DIGIT (LETTER | DIGIT)* '.' './' '\\')
    | ([WS] [a-zA-EG-Z0-9]? (LETTER | DIGIT)* '.' './' '\\')
    | ([a-zA-EG-Z] (LETTER | DIGIT)* '.' './' '\\')
    ;

fragment BOR_FRAG
    : (DIGIT (LETTER | DIGIT)* '.' '\\' '/')
    | ([WS] [a-zA-EG-Z0-9]? (LETTER | DIGIT)* '.' '\\' '/')
    | ([a-zA-EG-Z] (LETTER | DIGIT)* '.' '\\' '/')
    ;

// Postfix operators
PRIME    : '\'' ;                          // op_57
PLUS_SUP : '^+' | '\u207a' ;              // op_68: ⁺
STAR_SUP : '^*' ;                          // op_69
HASH_SUP : '^#' ;                          // op_70

// Prefix operators
DOT_NEG   : '-.' ;                         // op_76
LNOT      : '\\lnot' | '\u00ac' ;         // op_26: ¬
NEG       : '\\neg' ;                      // op_29
TILDE     : '~' ;                          // op_58
BOX       : '[]' | '\u25a1' ;             // CASESEP: □
DIAMOND   : '<>' | '\u25c7' ;             // op_61: ◇
ENABLED_KW  : 'ENABLED' ;                 // op_112
UNCHANGED_KW: 'UNCHANGED' ;              // op_113
SUBSET_KW   : 'SUBSET' ;                 // op_114
UNION_KW    : 'UNION' ;                  // op_115
DOMAIN_KW   : 'DOMAIN' ;                 // op_116

// Infix operators - symbolic
DOUBLE_SLASH : '//' ;                     // op_1
AND          : '/\\' | '\u2227' ;        // op_2: conjunction ∧
NOT_EQUALS   : '/=' ;                     // op_3
SLASH        : '/' ;                      // op_4
OR           : '\\/' | '\u2228' ;        // op_5: disjunction ∨
APPROX       : '\\approx' | '\u2248' ;   // op_6: ≈
ASYMP        : '\\asymp' | '\u224d' ;    // op_7: ≍
BIGCIRC      : '\\bigcirc' | '\u25ef' ;  // op_8: ◯
BULLET       : '\\bullet' | '\u25cf' ;    // op_9: ●
CAP          : '\\cap' | '\u2229' ;      // op_10: ∩
CDOT         : '\\cdot' | '\u22c5' ;     // op_11: ⋅
CIRC         : '\\circ' | '\u2218' ;     // op_12: ∘
CONG         : '\\cong' | '\u2245' ;     // op_13: ≅
CUP          : '\\cup' | '\u222a' ;      // op_14: ∪
DIV          : '\\div' | '\u00f7' ;      // op_15: ÷
DOTEQ        : '\\doteq' | '\u2250' ;    // op_16: ≐
EQUIV        : '\\equiv' | '\u2261' ;    // op_17: ≡
GEQ          : '\\geq' | '\u2265' ;      // op_18: ≥
GG           : '\\gg' | '\u226b' ;       // op_19: ≫
IN           : '\\in' | '\u2208' ;       // op_20: ∈
INTERSECT    : '\\intersect' ;            // op_21
UNION_OP     : '\\union' ;               // op_22
LAND         : '\\land' ;                 // op_23
LEQ          : '\\leq' | '\u2264' ;      // op_24: ≤
LL           : '\\ll' | '\u226a' ;       // op_25: ≪
LOR          : '\\lor' ;                  // op_27
ODOT         : '\\o' | '\\odot' | '\u2299' ; // op_30/31: ⊙
OMINUS       : '\\ominus' | '\u2296' ;   // op_32: ⊖
OPLUS        : '\\oplus' | '\u2295' ;    // op_33: ⊕
OSLASH       : '\\oslash' | '\u2298' ;   // op_34: ⊘
OTIMES       : '\\otimes' | '\u2297' ;   // op_35: ⊗
PREC         : '\\prec' | '\u227a' ;     // op_36: ≺
PRECEQ       : '\\preceq' | '\u227c' ;   // op_37: ≼ (was ⪯)
PROPTO       : '\\propto' | '\u221d' ;   // op_38: ∝
SIM          : '\\sim' | '\u223c' ;      // op_39: ∼
SIMEQ        : '\\simeq' | '\u2243' ;    // op_40: ≃
SQCAP        : '\\sqcap' | '\u2293' ;    // op_41: ⊓
SQCUP        : '\\sqcup' | '\u2294' ;    // op_42: ⊔
SQSUBSET     : '\\sqsubset' | '\u228f' ; // op_43: ⊏
SQSUPSET     : '\\sqsupset' | '\u2290' ; // op_44: ⊐
SQSUBSETEQ   : '\\sqsubseteq' | '\u2291' ; // op_45: ⊑
SQSUPSETEQ   : '\\sqsupseteq' | '\u2292' ; // op_46: ⊒
STAR         : '\\star' | '\u22c6' ;     // op_47: ⋆
SUBSET_OP    : '\\subset' | '\u2282' ;   // op_48: ⊂
SUBSETEQ     : '\\subseteq' | '\u2286' ; // op_49: ⊆
SUCC         : '\\succ' | '\u227b' ;     // op_50: ≻
SUCCEQ       : '\\succeq' | '\u227d' ;   // op_51: ≽ (was ⪰)
SUPSET       : '\\supset' | '\u2283' ;   // op_52: ⊃
SUPSETEQ     : '\\supseteq' | '\u2287' ; // op_53: ⊇
UPLUS        : '\\uplus' | '\u228e' ;    // op_54: ⊎
WR           : '\\wr' | '\u2240' ;       // op_55: ≀
BACKSLASH    : '\\' ;                     // op_56
LEADS_TO     : '~>' | '\u219d' ;         // op_59: ↝
IMPLIES      : '=>' | '\u21d2' ;         // op_62: ⇒
IMPLIED_BY   : '=<' ;                     // op_63
ASSERT       : '=|' ;                    // op_64
HASH_HASH    : '##' ;                    // op_66
HASH         : '#' ;                     // op_67
CARET_CARET  : '^^' ;                   // op_71
CARET        : '^' ;                    // op_72
DASH_DASH    : '--' ;                   // op_73
DASH_BAR     : '-|' ;                   // op_74
PLUS_ARROW   : '-+->' | '\u27fb' ;     // op_75: -+->
MINUS        : '-' ;                    // op_77
STAR_STAR    : '**' ;                   // op_78
TIMES        : '*' ;                    // op_79
PLUS_PLUS    : '++' ;                   // op_80
PLUS         : '+' ;                    // op_81
IFF          : '<=>' | '\u21d4' ;       // op_82: ⇔
LTCOLON      : '<:' ;                   // op_83
LTEQ         : '<=' ;                   // op_84
LT           : '<' ;                    // op_85
GTEQ         : '>=' ;                   // op_86
GT           : '>' ;                    // op_87
DOTS3        : '...' | '\u2026' ;       // op_88: …
DOTS2        : '..' | '\u2025' ;        // op_89: ‥
BARBAR       : '||' | '\u2016' ;        // op_90: ‖
BAR          : '|' ;                    // op_91
DASHTURNSTILE : '|-' | '\u22a2' ;      // op_92: ⊢
TURNSTILE    : '|=' | '\u22a8' ;       // op_93: ⊨
AMPAMP       : '&&' ;                  // op_94
AMP          : '&' ;                   // op_95
DOLLARDOLLAR : '$$' ;                  // op_96
DOLLAR       : '$' ;                   // op_97
QUESQUES     : '??' ;                  // op_98
QUESTION     : '?' ;                   // op_99 (not defined?)
PERCENTPERCENT : '%%' ;                // op_100
PERCENT      : '%' ;                   // op_101
ATAT         : '@@' ;                 // op_102
EXCELEXCLAIM : '!!' ;                 // op_103
COLONGT      : ':>' ;                  // op_104
COLONEQ      : ':=' ;                  // op_105
COLONEQCOLON : '::=' ;                // op_106
OPLUS_PAREN  : '(+)' ;                // op_107
OMINUS_PAREN : '(-)' ;                // op_108
ODOT_PAREN   : '(.)' ;                // op_109
OSLASH_PAREN : '(/)' ;                // op_110
OTIMES_PAREN : '(\\X)' ;              // op_111
NOTIN        : '\\notin' | '\u2209' ; // op_117: ∉
TIMES_KW     : '\\times' ;            // op_118
CROSS        : '\\X' ;                // op_119

// Unicode infix operators (additional to ASCII)
APPROX_UC      : '\u2248' ; // ≈
ASSIGN_UC      : '\u2254' ; // ≔
ASYMP_UC       : '\u224d' ; // ≍
BIGCIRC_UC     : '\u25ef' ; // ◯
BNF_RULE_UC    : '\u2974' ; // ⩴
BULLET_UC      : '\u25cf' ; // ●
CAP_UC         : '\u2229' ; // ∩
CDOT_UC        : '\u22c5' ; // ⋅
CIRC_UC        : '\u2218' ; // ∘
CONG_UC        : '\u2245' ; // ≅
CUP_UC         : '\u222a' ; // ∪
DIV_UC         : '\u00f7' ; // ÷
DOTEQ_UC       : '\u2250' ; // ≐
DOTS2_UC       : '\u2025' ; // ‥
DOTS3_UC       : '\u2026' ; // …
EQUIV_UC       : '\u2261' ; // ≡
EXCL_UC        : '\u203c' ; // ‼
GEQ_UC         : '\u2265' ; // ≥
GG_UC          : '\u226b' ; // ≫
IFF_UC         : '\u21d4' ; // ⇔
IMPLIES_UC     : '\u21d2' ; // ⇒
LD_TTILE_UC    : '\u2ae4' ; // ⫤
LEADS_TO_UC    : '\u219d' ; // ↝
LEQ_UC         : '\u2264' ; // ≤
LL_UC          : '\u226a' ; // ≪
LS_TTILE_UC    : '\u22a3' ; // ⊣
NEQ_UC         : '\u2260' ; // ≠
NOTIN_UC       : '\u2209' ; // ∉
ODOT_UC        : '\u2299' ; // ⊙
OMINUS_UC      : '\u2296' ; // ⊖
OPLUS_UC       : '\u2295' ; // ⊕
OSLASH_UC      : '\u2298' ; // ⊘
OTIMES_UC      : '\u2297' ; // ⊗
PLUS_ARROW_UC  : '\u21f8' ; // ⇸
PREC_UC        : '\u227a' ; // ≺
PRECEQ_UC      : '\u227c' ; // ≼
PROPTO_UC      : '\u221d' ; // ∝
QQ_UC          : '\u2047' ; // ⁇
RD_TTILE_UC    : '\u22a8' ; // ⊨
RS_TTILE_UC    : '\u22a2' ; // ⊢
SIM_UC         : '\u223c' ; // ∼
SIMEQ_UC       : '\u2243' ; // ≃
SQCAP_UC       : '\u2293' ; // ⊓
SQCUP_UC       : '\u2294' ; // ⊔
SQSUBSET_UC    : '\u228f' ; // ⊏
SQSUBSETEQ_UC  : '\u2291' ; // ⊑
SQSUPSET_UC    : '\u2290' ; // ⊐
SQSUPSETEQ_UC  : '\u2292' ; // ⊒
STAR_UC        : '\u22c6' ; // ⋆
SUBSET_UC      : '\u2282' ; // ⊂
SUBSETEQ_UC    : '\u2286' ; // ⊆
SUCC_UC        : '\u227b' ; // ≻
SUCCEQ_UC      : '\u227d' ; // ≽
SUPSET_UC      : '\u2283' ; // ⊃
SUPSETEQ_UC    : '\u2287' ; // ⊇
TIMES_UC       : '\u00d7' ; // ×
UPLUS_UC       : '\u228e' ; // ⊎
VERTVERT_UC    : '\u2016' ; // ‖
WR_UC          : '\u2240' ; // ≀

// Proof step tokens
ProofStepLexeme
    : '<' DIGIT+ '>' (LETTER | DIGIT | '_')+
    ;

ProofImplicitStepLexeme
    : '<' [+\-] '>' (LETTER | DIGIT)+
    ;

ProofStepDotLexeme
    : '<' (DIGIT+ | [+\-] | '*') '>' (LETTER | DIGIT | '_')+ '.'+
    ;

BareLevelLexeme
    : '<' (DIGIT+ | [+\-] | '*') '>'
    ;

UnnumberedStepLexeme
    : '<' (DIGIT+ | [+\-] | '*') '>' '.'+
    ;

// Identifier - must be after all keywords and operators
IDENTIFIER
    : CASE0
    | CASE1
    | CASE2
    | CASE3
    | CASE6
    | CASEN
    | '@'
    | NUMBER_SET
    ;

// Catch-all for any unrecognized character
SPEC_ERROR_CHAR : . ;

// ============================================================================
// PRAGMA mode
// ============================================================================

mode PRAGMA_MODE ;

PRAGMA_SKIP : [ \t\n\r] -> skip ;
PRAGMA_BLOCK_COMMENT : BLOCK_COMMENT_START -> pushMode(IN_COMMENT_MODE) ;

PRAGMA_NUMBER : DIGIT+ | '0' ;
PRAGMA_BEGIN_MODULE : '----' '-'* ' '* 'MODULE' -> type(BEGIN_MODULE), mode(SPEC_MODE) ;
PRAGMA_IDENTIFIER : CASE0 | CASE1 | CASE2 | CASE3 | CASE6 | CASEN | '@' | NUMBER_SET ;

PRAGMA_CHAR : . -> skip ;

// ============================================================================
// Comment mode (nested block comments)
// ============================================================================

mode IN_COMMENT_MODE ;

COMMENT_NESTED_OPEN  : BLOCK_COMMENT_START -> pushMode(EMBEDDED_COMMENT_MODE) ;
COMMENT_CLOSE        : '*)' -> popMode ;
COMMENT_TEXT         : ~[*)]+ | [*] ~')' | ')' ~'*' ;

// ============================================================================
// Embedded nested comment mode
// ============================================================================

mode EMBEDDED_COMMENT_MODE ;

EMBEDDED_NESTED_OPEN  : BLOCK_COMMENT_START -> pushMode(EMBEDDED_COMMENT_MODE) ;
EMBEDDED_CLOSE        : '*)' -> popMode ;
EMBEDDED_TEXT         : ~[*)]+ | [*] ~')' | ')' ~'*' ;

// ============================================================================
// End-of-line comment mode
// ============================================================================

mode IN_EOL_COMMENT_MODE ;

EOL_COMMENT_NEWLINE : [\n\r] -> popMode ;
EOL_COMMENT_TEXT    : ~[\n\r]+ ;
