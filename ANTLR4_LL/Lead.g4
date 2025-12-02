grammar Lead;


program
    : (declaration | statement | functionDeclaration)* EOF
    ;



declaration
    : 'var' identList ':' type ('=' expression)?
    ;

identList
    : IDENTIFIER (',' IDENTIFIER)*
    ;

type
    : 'int' | 'float' | 'bool' | 'string'
    ;


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
    | expressionStatement
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


ifStatement
    : 'if' condition codeBlock
      ('else' 'if' condition codeBlock)* ('else' codeBlock)?
    ;

guardStatement
    : 'guard' '(' condition ')' 'else' '{' statement* '}'
    ;


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


expression
    : boolExpression
    | arithmExpression
    ;

condition
    : boolExpression
    | expression
    ;


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
    | funcCall
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


COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;


WS
    : [ \t\r\n]+ -> skip
    ;