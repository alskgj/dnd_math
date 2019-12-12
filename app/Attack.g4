grammar Attack;

/*
 * Parser Rules
 */


line        : (tohit)? (vardmg | condmg)+ ;
tohit       : SIGN NUMBER WHITESPACE ;
vardmg      : SIGN? NUMBER D NUMBER ;
condmg      : SIGN? NUMBER ;

/*
 * Lexer Rules
 */

NUMBER              : [0-9]+ ;
WHITESPACE          : ' '->skip;
SIGN                : ('+'|'-');
D                   : 'd';