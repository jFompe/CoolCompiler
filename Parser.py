# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os

from Clases import *

DIRECTORIO = os.path.join("E:\\", "UNI", "4O CURSO",
                        "2O CUATRI", "LENGUAJES DE PROGRAMACION",
                        "CoolCompiler")


sys.path.append(DIRECTORIO)

GRADING = os.path.join(DIRECTORIO, 'gradingParser')
FICHEROS = os.listdir(GRADING)

TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(GRADING, fich))
         and fich.endswith(".test")]

SINGLE_TESTS = [
    # "complex.test", # Revisar al poner = nonassoc
    # "unaryassociativity.test",

    # "-- PASADOS --"
    # "addedlet.test",
    # "atoi.test",
    # "attrcapitalname.test",
    # "badblock.test",
    # "baddispatch1.test",
    # "badexprlist.test",
    # "badfeatures.test",
    # "casemultiplebranch.test",
    # "casenoexpr.test",
    # "classnoname.test",
    # "firstbindingerrored.test",
    # "ifnoelse.test",
    # "letinitmultiplebindings.test",
    # "while.test",
    # "whileoneexpression.test",
    # "whilenoloop.test",
]

PRINT_ERRORS = False
if SINGLE_TESTS:
    TESTS = SINGLE_TESTS
    PRINT_ERRORS = True


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS', '~', 'NOT'),
        ('nonassoc', '<', 'LE', '='),
        ('left', '.', 'ISVOID'),
    )


    # program (Programa)

    @_('clases')
    def program(self, p):
        return Programa(0, p.clases)

    @_('clase ";"')
    def clases(self, p):
        return [p.clase]

    @_("clases clase ';'")
    def clases(self, p):
        return p.clases + [p.clase]

    # class (Clase)

    @_('CLASS TYPEID "{" empty "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID, 'Object', self.nombre_fichero, p.empty)

    @_('CLASS TYPEID "{" features "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID, 'Object', self.nombre_fichero, p.features)

    @_('CLASS TYPEID INHERITS TYPEID "{" empty "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID0, p.TYPEID1, self.nombre_fichero, p.empty)

    @_('CLASS TYPEID INHERITS TYPEID "{" features "}"')
    def clase(self, p):
        return Clase(p.lineno, p.TYPEID0, p.TYPEID1, self.nombre_fichero, p.features)

    # feature (Metodo | Atributo)

    @_('feature ";"')
    def features(self, p):
        return [p.feature] 

    @_('error ";"')
    def features(self, p):
        return []

    @_('features feature ";"')
    def features(self, p):
        return p.features + [p.feature]

    @_('OBJECTID "(" empty ")" ":" error')
    def feature(self, p):
        return NoExpr(p.lineno)

    @_('OBJECTID "(" empty ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return NoExpr(p.lineno)

    @_('OBJECTID "(" formals ")" ":" TYPEID "{" error "}"')
    def feature(self, p):
        return NoExpr(p.lineno)

    @_('OBJECTID "(" empty ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(p.lineno, p.OBJECTID, p.TYPEID, p.expr, p.empty)

    @_('OBJECTID "(" error ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return NoExpr(p.lineno)

    @_('OBJECTID "(" formals ")" ":" TYPEID "{" expr "}"')
    def feature(self, p):
        return Metodo(p.lineno, p.OBJECTID, p.TYPEID, p.expr, p.formals)

    @_('OBJECTID ":" TYPEID')
    def feature(self, p):
        return Atributo(p.lineno, p.OBJECTID, p.TYPEID, NoExpr(p.lineno))

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def feature(self, p):
        return Atributo(p.lineno, p.OBJECTID, p.TYPEID, p.expr)

    # formal (Formal)

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(p.lineno, p.OBJECTID, p.TYPEID)

    @_('formal')
    def formals(self, p):
        return [p.formal]

    @_('formals "," formal')
    def formals(self, p):
        return p.formals + [p.formal]


    # expr (Expresion)

    @_('OBJECTID ASSIGN expr')
    def expr(self, p):
        return Asignacion(p.lineno, p.OBJECTID, p.expr)

    @_('expr "." OBJECTID "(" arguments ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, p.expr, p.OBJECTID, p.arguments)

    @_('expr "." OBJECTID "(" empty ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, p.expr, p.OBJECTID, p.empty)

    @_('expr "@" TYPEID "." OBJECTID "(" arguments ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(p.lineno, p.expr, p.TYPEID, p.OBJECTID, p.arguments)

    @_('expr "@" TYPEID "." OBJECTID "(" empty ")"')
    def expr(self, p):
        return LlamadaMetodoEstatico(p.lineno, p.expr, p.TYPEID, p.OBJECTID, p.empty)

    @_('OBJECTID "(" arguments ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, Objeto(p.lineno, 'self'), p.OBJECTID, p.arguments)

    @_('OBJECTID "(" empty ")"')
    def expr(self, p):
        return LlamadaMetodo(p.lineno, Objeto(p.lineno, 'self'), p.OBJECTID, p.empty)

    @_('expr')
    def arguments(self, p):
        return [p.expr]

    @_('arguments "," expr')
    def arguments(self, p):
        return p.arguments + [p.expr]

    @_('IF expr THEN error FI')
    def expr(self, p):
        return NoExpr(p.lineno)

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p):
        return Condicional(p.lineno, p.expr0, p.expr1, p.expr2)

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p):
        return Bucle(p.lineno, p.expr0, p.expr1)

    @_('expr ";"')
    def exprs(self, p):
        return [p.expr]

    @_('exprs expr ";"')
    def exprs(self, p):
        return p.exprs + [p.expr]

    @_('exprs error ";"')
    def exprs(self, p):
        return []

    @_('"{" error "}"')
    def expr(self, p):
        return NoExpr(p.lineno)

    @_('"{" exprs "}"')
    def expr(self, p):
        return Bloque(p.lineno, p.exprs)

    @_('OBJECTID ":" TYPEID')
    def variabledef(self, p):
        return p

    @_('OBJECTID ":" TYPEID ASSIGN error')
    def variabledef(self, p):
        return NoExpr(p.lineno)

    @_('OBJECTID ":" TYPEID ASSIGN expr')
    def variabledef(self, p):
        return p

    @_('variabledef')
    def variabledefs(self, p):
        return [p.variabledef]

    @_('variabledef "," variabledefs')
    def variabledefs(self, p):
        return [p.variabledef] + p.variabledefs

    @_('LET variabledefs IN expr')
    def expr(self, p):
        vars = p.variabledefs
        let = p.expr
        for var in vars[::-1]:
            let = self.createLet(var, let)
        return let

    def createLet(self, vd, expr):
        inic = vd[5] if len(vd) >= 6 else NoExpr(expr.linea)
        return Let(expr.linea, vd[1], vd[3], inic, expr)


    @_('OBJECTID ":" TYPEID DARROW error ";"')
    def arrowFuncts(self, p):
        return []

    @_('OBJECTID ":" TYPEID DARROW expr ";"')
    def arrowFuncts(self, p):
        return [RamaCase(p.lineno, p.OBJECTID, p.TYPEID, p.expr)]

    @_('arrowFuncts OBJECTID ":" TYPEID DARROW error ";"')
    def arrowFuncts(self, p):
        return p.arrowFuncts + []

    @_('arrowFuncts OBJECTID ":" TYPEID DARROW expr ";"')
    def arrowFuncts(self, p):
        return p.arrowFuncts + [RamaCase(p.lineno, p.OBJECTID, p.TYPEID, p.expr)]

    @_('CASE error OF arrowFuncts ESAC')
    def expr(self, p):
        return NoExpr(p.lineno)

    @_('CASE expr OF arrowFuncts ESAC')
    def expr(self, p):
        return Swicht(p.lineno, p.expr, p.arrowFuncts)

    @_('NEW TYPEID')
    def expr(self, p):
        return Nueva(p.lineno, p.TYPEID)

    @_('ISVOID expr')
    def expr(self, p):
        return EsNulo(p.lineno, p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return Suma(p.lineno, p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return Resta(p.lineno, p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return Entero(p.lineno, -int(p.expr))

    @_('expr "*" expr')
    def expr(self, p):
        return Multiplicacion(p.lineno, p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return Division(p.lineno, p.expr0, p.expr1)

    @_('"~" expr')
    def expr(self, p):
        return Neg(p.lineno, p.expr)

    @_('expr "<" expr')
    def expr(self, p):
        return Menor(p.lineno, p.expr0, p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        return LeIgual(p.lineno, p.expr0, p.expr1)

    @_('expr "=" expr')
    def expr(self, p):
        return Igual(p.lineno, p.expr0, p.expr1)

    @_('NOT expr')
    def expr(self, p):
        return Not(p.lineno, p.expr)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('OBJECTID')
    def expr(self, p):
        return Objeto(p.lineno, p.OBJECTID)

    @_('INT_CONST')
    def expr(self, p):
        return Entero(p.lineno, int(p.INT_CONST))

    @_('STR_CONST')
    def expr(self, p):
        return String(p.lineno, p.STR_CONST)

    @_('BOOL_CONST')
    def expr(self, p):
        return Booleano(p.lineno, p.BOOL_CONST in ('true', True))

    @_('')
    def empty(self, p):
        return []

    def error(self, p):
        if PRINT_ERRORS: print('ERROR', p)
        if not p:
            error_msg = f'"{self.nombre_fichero}", line 0: syntax error at or near EOF' 
        elif self.is_id(p) or self.is_constant(p):
            error_msg = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type} = {p.value}'
        elif self.is_literal(p):
            error_msg = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near \'{p.type}\''
        else:
            error_msg = f'"{self.nombre_fichero}", line {p.lineno}: syntax error at or near {p.type}'
        self.errores.append(error_msg)

    def is_id(self, p):
        return p.type in ('TYPEID', 'OBJECTID')

    def is_constant(self, p):
        return p.type in ('STR_CONST', 'INT_CONST')

    def is_literal(self, p):
        return p.type == p.value


for fich in TESTS:
    # print(f'Evaluando {fich}...')
    f = open(os.path.join(GRADING, fich), 'r')
    g = open(os.path.join(GRADING, fich + '.out'), 'r')
    lexer = CoolLexer()
    lexer1 = CoolLexer()
    parser = CoolParser()
    parser.nombre_fichero = fich
    parser.errores = []
    bien = ''.join([c for c in g.readlines() if c and '#' not in c])
    entrada = f.read()
    j = parser.parse(lexer.tokenize(entrada))
    for t0 in lexer1.tokenize(entrada):
        pass
    try:
        if j and not parser.errores:
            resultado = '\n'.join([c for c in j.str(0).split('\n') if c and '#' not in c])
        else:
            resultado = '\n'.join(parser.errores)
            resultado += '\n' + "Compilation halted due to lex and parse errors"
        f.close(), g.close()
        if resultado.lower().strip().split() != bien.lower().strip().split():
            print(f"Revisa el fichero {fich}")
            f = open(os.path.join(GRADING, fich)+'.nuestro', 'w')
            g = open(os.path.join(GRADING, fich)+'.bien', 'w')
            f.write(resultado.strip())
            g.write(bien.strip())
            f.close()
            g.close()

    except:
        print(f"Falla en {fich}")
