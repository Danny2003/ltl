"""
ltl_parser.py

This module contains a lexer and a parser for parsing LTL formulas.

It defines the lexical rules for LTL formulas, including various operators and atomic propositions.

Note that the LTL formula parser supports `true`.

Lexers and parsers are implemented using the PLY (Python Lex-Yacc) library.

"""
import ply.lex as lex
import ply.yacc as yacc

tokens = (
    'NOT', 'AND', 'OR', 'IMPLIES', 'NEXT', 'ALWAYS', 'EVENTUALLY', 'UNTIL',
    'LPAREN', 'RPAREN', 'ATOM'
)

t_NOT = r'!'
t_AND = r'/\\'
t_OR = r'\\/'
t_IMPLIES = r'->'
t_NEXT = r'X'
t_ALWAYS = r'G'
t_EVENTUALLY = r'F'
t_UNTIL = r'U'
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_ATOM(t):
    r'[a-z_][a-z0-9_]*'
    return t

t_ignore = ' \t'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

# Grammar for LTL
def p_formula_atom(p):
    '''formula : ATOM'''
    p[0] = ('atom', p[1])

def p_formula_not(p):
    '''formula : NOT formula'''
    p[0] = ('not', p[2])

def p_formula_and(p):
    '''formula : formula AND formula'''
    p[0] = ('and', p[1], p[3])

def p_formula_or(p):
    '''formula : formula OR formula'''
    p[0] = ('or', p[1], p[3])

def p_formula_implies(p):
    '''formula : formula IMPLIES formula'''
    p[0] = ('implies', p[1], p[3])

def p_formula_next(p):
    '''formula : NEXT formula'''
    p[0] = ('next', p[2])

def p_formula_always(p):
    '''formula : ALWAYS formula'''
    p[0] = ('always', p[2])

def p_formula_eventually(p):
    '''formula : EVENTUALLY formula'''
    p[0] = ('eventually', p[2])

def p_formula_until(p):
    '''formula : formula UNTIL formula'''
    p[0] = ('until', p[1], p[3])

def p_formula_paren(p):
    '''formula : LPAREN formula RPAREN'''
    p[0] = p[2]

def p_error(p):
    '''error information'''
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

parser = yacc.yacc()
