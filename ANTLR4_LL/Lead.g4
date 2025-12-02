grammar Lead;

// --- Entry Point ---

program
    : (declaration | statement | functionDeclaration)* EOF
    ;

// --- Declarations ---

declaration
    : 'var' identList ':' type ('=' expression)?
    ;

identList
    : IDENTIFIER (',' IDENTIFIER)*
    ;

type
    : 'int' | 'float' | 'bool' | 'string'
    ;

// --- Functions ---

// Примітка: Я додав paramList для оголошення, щоб відрізнити його від виклику (ArgList)
functionDeclaration
    : 'func' IDENTIFIER '(' paramList? ')' ('->' type)? '{' statement* returnStatement? '}'
    ;

paramList
    : param (',' param)*
    ;

param
    : IDENTIFIER ':' type
    ;

returnStatement
    : 'return' (expression | IDENTIFIER)?
    ;

// --- Statements ---

statement
    : assignStatement
    | inputStatement
    | outputStatement
    | forStatement
    | whileStatement
    | repeatWhileStatement
    | ifStatement
    | guardStatement
    | switchStatement
    | expressionStatement // Дозволяє викликати функції як окремі інструкції
    ;

assignStatement
    : IDENTIFIER '=' expression
    ;

inputStatement
    : IDENTIFIER '=' 'input' '(' ')'
    ;

outputStatement
    : 'print' '(' (expression | STRING) ')'
    ;

// Об'єднана логіка для всіх типів If (Simple, Else, Chained)
ifStatement
    : 'if' condition codeBlock
      ('else' 'if' condition codeBlock)* ('else' codeBlock)?
    ;

guardStatement
    : 'guard' '(' condition ')' 'else' '{' statement* '}'
    ;

// Switch structure
switchStatement
    : 'switch' IDENTIFIER '{' caseBlock* defaultBlock? '}'
    ;

caseBlock
    : 'case' ('-')? NUMBER ':' statement*
    ;

defaultBlock
    : 'default' ':' statement*
    ;

forStatement
    : 'for' '(' (declaration | assignStatement) ';' condition ';' assignStatement ')' codeBlock
    ;

whileStatement
    : 'while' '(' condition ')' codeBlock
    ;

repeatWhileStatement
    : 'repeat' codeBlock 'while' boolExpression
    ;

expressionStatement
    : expression
    ;

codeBlock
    : '{' statement* '}'
    ;

// --- Expressions ---

// Узагальнений Expression
expression
    : boolExpression
    | arithmExpression
    ;

condition
    : boolExpression
    | expression // Дозволяє загальні вирази як умови
    ;

// Boolean Logic
boolExpression
    : boolTerm ('||' boolTerm)*
    ;

boolTerm
    : boolFactor ('&&' boolFactor)*
    ;

boolFactor
    : 'true'
    | 'false'
    | comparison
    | '!' boolFactor
    | '(' boolExpression ')'
    ;

comparison
    : arithmExpression relOp arithmExpression
    ;

relOp
    : '==' | '!=' | '<' | '<=' | '>' | '>='
    ;

// Arithmetic Logic
arithmExpression
    : sign? term (('+' | '-') term)*
    ;

term
    : factor (('*' | '/' | '**') factor)*
    ;

factor
    : IDENTIFIER
    | NUMBER
    | funcCall         // Додано можливість виклику функції всередині виразу
    | '(' arithmExpression ')'
    ;

sign
    : '+' | '-'
    ;

funcCall
    : IDENTIFIER '(' argList? ')'
    ;

argList
    : expression (',' expression)*
    ;

// --- Lexer Rules (Tokens) ---

// Keywords definition isn't strictly necessary if defined explicitly in literals above,
// but good for precedence.

IDENTIFIER
    : [a-zA-Z][a-zA-Z0-9]*
    ;

NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

STRING
    : '"' .*? '"'
    | '\'' .*? '\''
    ;

// Comments: skip them so parser doesn't need to handle them explicitly in grammar
COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;

// Whitespace handling
WS
    : [ \t\r\n]+ -> skip
    ;