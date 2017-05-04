# Philip Kaiser-Parlette
# Parser and interpreter for a simple language that allows for class and subclass creation,
# string comparison and concatenation, and class and superclass calls. Classes are able to hold strings.
# BNF grammar of the language is provided.
# 
######################################################################
# Scanner generation
tokens = ('STR', 'CLASSNAME', 'MAKECLASS', 'SUBCLASS', 'SUPER', 'CONCAT', 'COMP',)
literals = ['.',]

# STR token consists of characters (other than newlines) that are surrounded by single or double quotes
# Note: Single quotes can be used inside of a double-quoted string and vice-versa
def t_STR(t): r''' "([^"\n]|(\\"))*"|'([^'\n]|(\\'))*' '''; return t
# CLASSNAME tokens are made of one or more capital letters
def t_CLASSNAME(t): r''' [A-Z]+ '''; return t
# Other language commands are defined here
def t_MAKECLASS(t): r''' makeclass '''; return t
def t_SUBCLASS(t): r''' subclass '''; return t
def t_SUPER(t): r''' super '''; return t
def t_CONCAT(t): r''' concat '''; return t
def t_COMP(t): r''' compare '''; return t

# Whitespace is ignored and not interpreted as a token
t_ignore = ' \t\r'

def t_newline(t): r'\n+'; t.lexer.lineno += t.value.count("\n")

def t_error(t):
    ''' Prints error messages when scan fails '''
    print ("Illegal character at line {} '{}'".format(t.lexer.lineno, \
        t.value[0]))
    t.lexer.skip(1)

# Build the lexer
import ply.lex as lex
lex.lex(debug=0)

######################################################################
# Parser Tree

# Precedence rules to make sure comparison is always done last
precedence = (
	('left','COMP'),
	('left','SUPER','CONCAT')
	)

class Node:
	""" This will store nodes in a parse tree """
	
	allClassesDict = {} # Global dictionary mapping class names to nodes
		
	def doit(self):
		return "Error" # No parser rule should create a generic Node

class MakeclassNode(Node):
	""" This node type will store the name of a class as well as its defined body statements """
	def __init__(self, name, bodyStatements):
		self.name = name
		self.bodyStatements = bodyStatements

	def doit(self):
		Node.allClassesDict[self.name] = self
		return self.name

class SubclassNode(Node):
	""" This node type will store the name of a subclass as well as its defined body statements and its superclass"""
	def __init__(self, supername, name, bodyStatements):
		self.name = name
		self.supername = supername
		self.bodyStatements = bodyStatements

	def doit(self):
		Node.allClassesDict[self.name] = self
		return self.name

class CallNode(Node):
	""" This node performs a class call, returning the result of its body statements """
	def __init__(self, name):
		self.name = name

	def doit(self):
		node = Node.allClassesDict[self.name]
		result = ""
		for statement in node.bodyStatements:
			result = statement.doit()
		return result

class CallSuperNode(Node):
	""" This node performs a superclass call, returning the result of its body statements """
	def __init__(self, name):
		self.name = name

	def doit(self):
		node = Node.allClassesDict[self.name]
		result = "".join((self.name, " is not a subclass."))
		if (isinstance(node, SubclassNode)):
			node = Node.allClassesDict[node.supername]
			for statement in node.bodyStatements:
				result = statement.doit()
		return result

class ConcatNode(Node):
	""" This node performs a string concatenation by combining the results of the two nodes being concatenated """
	def __init__(self, leftNode, rightNode):
		self.leftNode = leftNode
		self.rightNode = rightNode
	
	def doit(self):
		result = self.leftNode.doit() + self.rightNode.doit()
		return result

class CompareNode(Node):
	""" This node performs a string comparison on the results of the two nodes being compared """
	def __init__(self, leftNode, rightNode):
		self.leftNode = leftNode
		self.rightNode = rightNode
	
	def doit(self):
		result = (self.leftNode.doit() == self.rightNode.doit())
		return result

class StringNode(Node):
	""" This node holds a string literal and returns its value """
	def __init__(self, value):
		self.value = value[1:-1]
	
	def doit(self):
		return self.value

######################################################################
# Parser Generation
######################################################################
## BNF Grammar 
##
## <statement_list> ::= <statement>
## | <statement_list> <statement>
## 
## <statement> ::= MAKECLASS CLASSNAME <statement_list> '.'
## | SUBCLASS CLASSNAME CLASSNAME <statement_list> '.'
## | <expr>
##
## <expr> ::= <expr> CONCAT <expr>
## | <expr> COMP <expr>
## | CLASSNAME
## | SUPER CLASSNAME
## | STR
## 
######################################################################

def p_statement_list_single(p):
	" statement_list : statement "
	p[0] = [p[1]] # returns a list

def p_statement_list_multi(p):
	" statement_list : statement_list statement "
	p[0] = p[1].append(p[2]) # returns a list

def p_statement_makeclass(p):
	"statement : MAKECLASS CLASSNAME statement_list '.' "
	p[0] = MakeclassNode(p[2], p[3])

def p_statement_subclass(p):
	" statement : SUBCLASS CLASSNAME CLASSNAME statement_list '.' "
	p[0] = SubclassNode(p[2], p[3], p[4])

def p_statement_expr(p):
	"statement : expr "
	p[0] = p[1]
	
def p_expr_call(p):
	" expr : CLASSNAME "
	p[0] = CallNode(p[1])

def p_expr_supercall(p):
	" expr : SUPER CLASSNAME "
	p[0] = CallSuperNode(p[2])

def p_expr_concat(p):
	" expr : expr CONCAT expr "
	p[0] = ConcatNode(p[1], p[3])

def p_expr_compare(p):
	" expr : expr COMP expr "
	p[0] = CompareNode(p[1], p[3])

def p_expr_str(p):
	" expr : STR "
	p[0] = StringNode(p[1])

######################################################################
# Error reporting
def p_error(p):
	''' Prints error messages when parse fails '''
	if p:
		print ("Syntax error at line {} '{}'".format(p.lineno, p.value))
	else:
		print ("Syntax error at EOF")

	sys.exit(-1)

import ply.yacc as yacc
yacc.yacc() # Build parser

######################################################################
######################################################################
# Test driver
import sys
if sys.version_info[0] >= 3:
	raw_input = input # Done to allow for compatibility with Python 2 & Python 3

allStatements = []

while 1:
	try:
		s = raw_input('calc > ')
	except EOFError:
		break
	if not s: continue
	resultList = yacc.parse(s+'\n') # Parse returns None upon error
	if None != resultList:
		allStatements = allStatements + resultList
		print ([node.doit() for node in resultList])
