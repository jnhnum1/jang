import ply.lex as lex
import ply.yacc as yacc

from bools import Bool
from context import *
from control import IfElseStatement, WhileStatement
from expressions import *
from functions import FuncDeclaration, FunctionCall
from lists import ListExpr
from objects import ObjectExpression
from ranges import RangeReference
from tuples import TupleExpression

# define a bunch of parsing rules for ply to use

reserved = {
        'function': 'FUNCTION',
        'return': 'RETURN',
        'if': 'IF',
        'else': 'ELSE',
        'var': 'VAR',
        'const': 'CONST',
        'print': 'PRINT',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'is': 'EQUALS',
        'true': 'TRUE',
        'false': 'FALSE',
        'xor': 'XOR',
        'while': 'WHILE',
        'new': 'NEW',
        'in': 'IN',
        'return': 'RETURN',
        'del': 'DEL',
        'undefined' : 'UNDEFINED',
        }

operators = {
        '+': 'PLUS',
        '-': 'MINUS',
        '*': 'TIMES',
        '^': 'EXPT',
        '/': 'DIVIDE',
        '=': 'ASSIGN',
        '==': 'EQUALS',
        '&&': 'AND',
        '||': 'OR',
        '^^': 'XOR',
        '!': 'NOT',
        '!=': 'NE',
        '>': 'GT',
        '<': 'LT',
        '>=': 'GE',
        '<=': 'LE',
        '%' : 'MOD',
        '.' : 'DOT',
        '+=': 'PLUSEQUALS',
        '-=': 'MINUSEQUALS',
        '*=': 'TIMESEQUALS',
        '/=': 'DIVEQUALS',
        }


tokens = [
        'FLOAT',
        'INT',
        'STRING',
        'ID',
        'LPAREN',
        'RPAREN',
        'LSQUARE',
        'RSQUARE',
        'LBRACE',
        'RBRACE',
        'OBJ_BEGIN',
        'OBJ_END',
        'STATEMENT_END',
        ] + list(set(list(reserved.values()) + list(operators.values())))

states = (
        ('parens', 'inclusive'),
        ('braces', 'inclusive'),
        )

def t_lparen(t):
    r'\('
    t.type = 'LPAREN'
    t.lexer.push_state('parens')
    return t

def t_rparen(t):
    r'\)'
    t.type = 'RPAREN'
    t.lexer.pop_state()
    return t

def t_obj_begin(t):
    r'{\|'
    t.type = 'OBJ_BEGIN'
    t.lexer.push_state('parens')
    return t

def t_obj_end(t):
    r'\|}'
    t.type = 'OBJ_END'
    t.lexer.pop_state()
    return t

def t_lbrace(t):
    r'{'
    t.type = 'LBRACE'
    t.lexer.push_state('braces')
    return t

def t_rbrace(t):
    r'}'
    t.type = 'RBRACE'
    t.lexer.pop_state()
    return t

def t_lsquare(t):
    r'\['
    t.type = 'LSQUARE'
    t.lexer.push_state('parens')
    return t

def t_rsquare(t):
    r'\]'
    t.type = 'RSQUARE'
    t.lexer.pop_state()
    return t

t_parens_ignore = ' \t'

t_ignore = ' \t'

literals = ",;:"

# primitives

# This needs to come first to get precedence over t_OP
def t_LINE_COMMENT(t):
    r'//.*'
    pass

def t_BLOCK_COMMENT(t):
    r'/\*(.|[\n\r])*\*/'
    pass

def t_braces_newline(t):
    r'[\n;]+'
    t.type = 'STATEMENT_END'
    endlines = [x for x in t.value if x == "\n"]
    t.lexer.lineno += len(endlines)
    return t

def t_parens_newline(t):
    r'[\n]+'
    t.lexer.lineno += len(t.value)

def t_parens_semicolon(t):
    r';+'
    t.type = 'STATEMENT_END'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_INT(t):
    r'(([1-9][0-9]*)|0)'
    t.value = int(t.value)
    return t

def t_FLOAT(t):
    # +/- float with or without scientific notation
    r'((([0-9]*)\.[0-9]+)|([0-9]+\.))([eE][1-9][0-9]*)?|[1-9][0-9]*[eE][1-9][0-9]*'
    t.value = float(t.value)
    return t

def t_OP(t):
    r'[\+\^\*\.\-=/&|!<>%]+'
    t.type = operators[t.value]
    return t

def t_STRING(t):
    # Single or double-quoted string with escaped characters
    r'"([^\\\"\n\r]|(\\.))*"|\'([^\\\'\n\r]|(\\.))*\''
    t.value = eval(t.value) # eval() is safe because already regex matched to be
                            # a string
    return t

def t_error(t):
    raise TypeError(t)

lexer = lex.lex()
lexer.begin('braces')

precedence = (
        ('nonassoc', 'RETURN'),
        ('right', 'ASSIGN'),
        ('left', 'OR'),
        ('left', 'XOR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('left', 'EQUALS', 'NE'),
        ('nonassoc', 'IN'),
        ('nonassoc', 'LT', 'GT', 'LE', 'GE'),
        ('nonassoc', 'PLUSEQUALS', 'MINUSEQUALS', 'TIMESEQUALS', 'DIVEQUALS'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MOD'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'EXPT'),
        ('right', 'UMINUS'),
        ('left', 'LSQUARE', 'RSQUARE'), # for ranges
        ('left', 'DOT'),
        ('nonassoc', 'NEW'),
        ('left', 'LPAREN', 'RPAREN'),  # for function application
        )

start = 'statements' 

def p_statement_block_statement(p):
    "statement : block_statement"
    p[0] = p[1]

def p_statement_expr(p):
    "statement : expression"
    p[0] = p[1]

def p_block_statement(p):
    "block_statement : LBRACE statements RBRACE"
    p[0] = BlockExpr(p[2])

def p_enders(p):
    """enders : STATEMENT_END
            | STATEMENT_END enders"""
    pass

def p_statements1_empty(p):
    "statements1 : empty"
    p[0] = []

def p_statements1_singleton(p):
    "statements1 : statement"
    p[0] = [p[1]]

def p_statements1_mult(p):
    "statements1 : statement enders statements1"
    p[0] = [p[1]] + p[3]

def p_statements_start_enders(p):
    "statements : enders statements1"
    p[0] = p[2]

def p_statements_statements1(p):
    "statements : statements1"
    p[0] = p[1]

def p_empty(p):
    "empty : "
    p[0] = []

def p_param_list(p):
    """paramlist : ID 
                 | empty
                 | ID ',' paramlist"""
    if len(p) == 2:
        if p[1]:
            p[0] = [p[1]]
        else:
            p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_expression_list(p):
    """expression_list : expression 
                 | empty
                 | expression ',' expression_list"""
    if len(p) == 2:
        if p[1]:
            p[0] = [p[1]]
        else:
            p[0] = []
    else:
        p[0] = [p[1]] + p[3]

def p_object_literal(p):
    "expression0 : OBJ_BEGIN property_list OBJ_END"
    p[0] = ObjectExpression(dict(p[2]))

def p_object_contains_query(p):
    "expression0 : expression IN expression"
    p[0] = InExpr(p[1], p[3])

def p_property_list_empty(p):
    "property_list : empty"
    p[0] = []

def p_property_list_singleton(p):
    "property_list : ID ':' expression"
    p[0] = [(p[1], p[3])]

def p_property_list_inductive(p):
    "property_list : ID ':' expression ',' property_list"
    p[5].append((p[1], p[3]))
    p[0] = p[5]

def p_list_empty(p):
    "expression0 : LSQUARE empty RSQUARE"
    p[0] = ListExpr([])

def p_list_nonempty(p):
    "expression0 : LSQUARE list_contents RSQUARE"
    p[0] = ListExpr(p[2])

def p_list_contents_singleton(p):
    "list_contents : expression"
    p[0] = [p[1]]

def p_list_contents_more(p):
    "list_contents : list_contents ',' expression"
    p[1].append(p[3])
    p[0] = p[1]

def p_expression_expression1(p):
    # This introduces ambiguities which are semantically meaningless.
    '''expression : expression0
                  | expression1'''
    p[0] = p[1]

def p_expression0_reference0(p):
    '''expression0 : reference0'''
    p[0] = VarAccess(p[1])

def p_expression1_reference1(p):
    '''expression1 : reference1'''
    p[0] = AttributeExpr(p[1])

def p_expression_float(p):
    'expression0 : FLOAT'
    p[0] = Number(p[1])

def p_expression_int(p):
    'expression0 : INT'
    p[0] = Number(p[1])

# Tuples
def p_expression_empty_tuple(p):
    'expression0 : LPAREN tuple_contents RPAREN'
    p[0] = TupleExpression(p[2])

def p_tuple_empty_contents(p):
    'tuple_contents : empty'
    p[0] = []

def p_tuple_singleton_contents(p):
    "tuple_contents2 : expression ','"
    p[0] = [p[1]]

def p_tuple_pair_contents(p):
    "tuple_contents2 : expression ',' expression"
    p[0] = [p[1], p[3]]

def p_tuple_contents(p):
    "tuple_contents : expression ',' tuple_contents2"
    p[0] = [p[1]] + p[3]

def p_tuple_contents_tuple_contents2(p):
    "tuple_contents : tuple_contents2"
    p[0] = p[1]

# Function calls

def p_expression1_new_invocation(p):
    "expression0 : NEW ID LPAREN expression_list RPAREN"
    p[0] = FunctionCall(VarAccess(VarReference(p[2])), p[4], is_new=True)

def p_expression_func_def(p):
    "expression0 : FUNCTION LPAREN paramlist RPAREN block_statement"
    p[0] = FuncDeclaration(p[3], p[5])

def p_expression0_func_call(p):
    """expression0 : expression0 LPAREN expression_list RPAREN"""
    p[0] = FunctionCall(p[1], p[3])

def p_expression1_func_call(p):
    """expression0 : expression1 LPAREN expression_list RPAREN"""
    p[0] = FunctionCall(p[1], p[3], is_method=True)


# Parentheses

def p_paren_expression0(p):
    "expression0 : LPAREN expression0 RPAREN" 
    p[0] = p[2]

def p_paren_expression1(p):
    "expression1 : LPAREN expression1 RPAREN" 
    p[0] = p[2]
    
def p_paren_expression(p):
    "expression : LPAREN expression RPAREN" 
    p[0] = p[2]
# Binary expressions

def make_binary_expression(token, expr_class):
    func_name = "p_%s_%s_%s" % ("expression", expr_class.__name__, token)
    def GrammarRule(p):
        p[0] = expr_class(p[1], p[3])
    GrammarRule.__name__ = func_name
    GrammarRule.__doc__ = 'expression : expression %s expression' % (token,)
    globals()[func_name] = GrammarRule

def make_op_equals_expression(token, op_class):
    func_name = "p_%s_%s" % ("expression", token)
    def GrammarRule(p):
        p[0] = OpEqualsExpr(op_class, p[1], p[3])
    GrammarRule.__name__ = func_name
    GrammarRule.__doc__ = 'expression : reference %s expression' % (token,)
    globals()[func_name] = GrammarRule


# Arithmetic expressions

binary_expressions = [
        ('PLUS', AddExpr),
        ('TIMES', TimesExpr),
        ('MINUS', SubtractExpr),
        ('DIVIDE', DivExpr),
        ('EXPT', ExptExpr),
        ('LT', LtExpr),
        ('GT', GtExpr),
        ('LE', LeExpr),
        ('GE', GeExpr),
        ('NE', NeExpr),
        ('AND', AndExpr),
        ('MOD', ModExpr),
        ('OR', OrExpr),
        ('XOR', XorExpr),
        ('EQUALS', EqualsExpr),
    ]

op_equals_expressions = [
        ('PLUSEQUALS', AddExpr),
        ('MINUSEQUALS', SubtractExpr),
        ('TIMESEQUALS', TimesExpr),
        ('DIVEQUALS', DivExpr),
    ]

for token, expr_class in binary_expressions:
    make_binary_expression(token, expr_class)
for token, op_class in op_equals_expressions:
    make_op_equals_expression(token, op_class)

def p_expr_uminus(p):
  '''expression : MINUS expression %prec UMINUS'''
  p[0] = SubtractExpr(Number(0), p[2])

# Boolean expressions

def p_expression_bool(p):
    '''expression0 : TRUE 
                | FALSE'''
    p[0] = Bool(True) if p[1] == 'true' else Bool(False)

def p_expression_not(p):
    "expression0 : NOT expression"
    p[0] = NotExpr(p[2])

# Strings

def p_expression_string(p):
    "expression0 : STRING"
    p[0] = String(p[1])

# If statements

def p_else_if_chain_else_end(p):
    "else_if_chain : ELSE block_statement"
    p[0] = [(Number(1), p[2])]

def p_else_if_chain_else_if_end(p):
    "else_if_chain : ELSE IF LPAREN expression RPAREN block_statement"
    p[0] = [(p[4], p[6])] 

def p_else_if_chain(p):
    "else_if_chain : ELSE IF LPAREN expression RPAREN block_statement else_if_chain"
    p[0] = [(p[4], p[6])] + p[7]

def p_expression_if(p):
    "expression0 : IF LPAREN expression RPAREN block_statement"
    p[0] = IfElseStatement([(p[3], p[5])])

def p_expression_if_else(p):
    "expression0 : IF LPAREN expression RPAREN block_statement else_if_chain"
    p[0] = IfElseStatement([(p[3], p[5])] + p[6])

# While loops
def p_statement_while(p):
    "statement : WHILE LPAREN expression RPAREN block_statement"
    p[0] = WhileStatement(p[3], p[5])

# References

# reference0 is a reference without a parent or references which can't be a
# function, and reference1 is a reference with a parent
# reference encompasses both of them.

def p_ref1_or_ref2(p):
    """reference : reference0 
                 | reference1"""
    p[0] = p[1]

def p_ref_id(p):
    'reference0 : ID'
    p[0] = VarReference(p[1])

def p_ref_attribute(p):
    "reference1 : expression DOT ID"
    p[0] = AttributeReference(p[1], String(p[3]))

def p_ref_subscript(p):
    "reference1 : expression LSQUARE expression RSQUARE"
    p[0] = AttributeReference(p[1], p[3])

def p_ref_subscript_range(p):
    "reference0 : expression LSQUARE expression ':' expression RSQUARE"
    p[0] = RangeReference(p[1], p[3], p[5])

def p_ref_subscript_whole(p):
    "reference0 : expression LSQUARE ':' RSQUARE"
    p[0] = RangeReference(p[1], None, None)

def p_ref_subscript_left(p):
    "reference0 : expression LSQUARE ':' expression RSQUARE"
    p[0] = RangeReference(p[1], None, p[4])

def p_ref_subscript_right(p):
    "reference0 : expression LSQUARE expression ':' RSQUARE"
    p[0] = RangeReference(p[1], p[3], None)


# Assignment / Declarations

def p_expression_assign(p):
    "expression0 : reference ASSIGN expression"
    p[0] = AssignExpr(p[1], p[3])

def p_local_var_undefined(p):
    "statement : VAR ID"
    p[0] = VarDeclaration(p[2])

def p_const_local_var(p):
    "statement : CONST VAR ID ASSIGN expression"
    p[0] = VarDeclaration(p[3], p[5], const=True, local=True)

def p_local_var(p):
    "statement : VAR ID ASSIGN expression"
    p[0] = VarDeclaration(p[2], p[4], const=False, local=True)

def p_const_var(p):
    "statement : CONST ID ASSIGN expression"
    p[0] = VarDeclaration(p[2], p[4], const=True, local=False)


# I/O / Interaction statements

def p_undefined(p):
    "expression0 : UNDEFINED"
    p[0] = Undefined()

def p_delete(p):
    "statement : DEL reference1"
    p[0] = DelStatement(p[2])

def p_print(p):
    "statement : PRINT expression"
    p[0] = PrintStatement(p[2])

def p_return(p):
    "statement : RETURN expression"
    p[0] = ReturnExpr(p[2])

def p_return_nothing(p):
    "statement : RETURN"
    p[0] = ReturnExpr(Undefined())

def p_error(p):
    raise SyntaxError("Invalid syntax on token: %s" % (p,))

yacc.yacc(debug=1)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (options, args) = parser.parse_args()
    if len(args) > 0:
        context = RootGameContext()
        # run file
        for filename in args:
            print "opening file: " + filename
            with open(filename) as jang_file:
                statements = yacc.parse(jang_file.read())
                for statement in statements:
                    statement.Eval(context)
    else:
        # REPL
        import cPickle as pickle
        context = RootGameContext()
        while True:
            try:
                s = raw_input('> ')
            except EOFError:
                break
            try:
                statements = yacc.parse(s)
                for statement in statements:
                    evaluated = statement.Eval(context)
                    # print pickle.dumps(context)
                if evaluated is not None:
                    print evaluated
            except SyntaxError:
                print "Syntax error!"
                import traceback
                traceback.print_exc()
            except Exception, bl:
                import traceback
                import sys
                print "Runtime error!"
                traceback.print_exc()
