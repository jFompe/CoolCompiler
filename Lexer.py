# coding: utf-8

from sly import Lexer
import os
from pprint import pprint

PRACTICA = os.path.join("E:\\", "UNI", "4O CURSO",
                        "2O CUATRI", "LENGUAJES DE PROGRAMACION",
                        "CoolCompiler")
DIR = os.path.join(PRACTICA, "grading")
FICHEROS = os.listdir(DIR)
TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(DIR, fich))
         and fich.endswith(".cool")]
TESTS= ["integers2.cool"]
TESTS.sort()

CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                      for i in ['0','1']
                      for j in range(16)]

CARACTERES_CONTROL += [bytes.fromhex(hex(127)[-2:]).decode('ascii')]

class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID, ELSE}
    literals = {'=', '+', '-', '*', '/', '(', ')'}

    ELSE = r'[eE][lL][sS][eE]'

    @_(r'\d+')
    def INT_CONST(self, t):
        # t.value = int(t.value)
        return t

    @_(r't[rR][uU][eE]')
    def BOOL_CONST(self, t):
        t.value = True
        return t

    @_(r'[A-Z][a-zA-Z0-9]*')
    def TYPEID(self, t):
        t.value = str(t.value)
        return t

    @_(r'[a-z_][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        return t

    @_(r'\t| ')
    def spaces(self, t):
        pass


    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

    def salida(self, texto):
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings

    def tests(self):
        for fich in TESTS:
            f = open(os.path.join(DIR, fich), 'r')
            g = open(os.path.join(DIR, fich + '.out'), 'r')
            resultado = g.read()
            entrada = f.read()
            texto = '\n'.join(self.salida(entrada))
            texto = f'#name "{fich}"\n' + texto
            f.close(), g.close()
            if texto.strip().split() != resultado.strip().split():
                print(f"Revisa el fichero {fich}")


lexer = CoolLexer()


if __name__ == '__main__':
    for fich in TESTS:
        lexer = CoolLexer()
        f = open(os.path.join(DIR, fich), 'r')
        g = open(os.path.join(DIR, fich + '.out'), 'r')
        resultado = g.read()
        texto = ''
        entrada = f.read()
        lexer_out = lexer.salida(entrada)
        pprint(lexer_out)
        texto = '\n'.join(lexer_out)
        texto = f'#name "{fich}"\n' + texto
        f.close(), g.close()
        if texto.strip().split() != resultado.strip().split():
            print(f"Revisa el fichero {fich}")
