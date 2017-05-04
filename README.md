# SimpleLanguage
The SimpleLanguage program is a parser and interpreter for a simmple language with the following capabilities:
  * String comparison and concatenation
  * Class creation, where classes hold string literals or statements that result in string literals
  * Subclass creation, where subclasses act as classes but also reference another class as their superclass
  * Class and superclass calls
This is done in Python using the Python Lex-Yacc (PLY) modules.

BNF grammar for the language is as follows:
   <statement_list> ::= <statement>
   | <statement_list> <statement>
   
   <statement> ::= MAKECLASS CLASSNAME <statement_list> '.'
   | SUBCLASS CLASSNAME CLASSNAME <statement_list> '.'
   | <expr>
  
   <expr> ::= <expr> CONCAT <expr>
   | <expr> COMP <expr>
   | CLASSNAME
   | SUPER CLASSNAME
   | STR 
