# coding: utf-8

from sly import Lexer
import os

PRACTICA = os.path.join("E:\\", "UNI", "4O CURSO",
                        "2O CUATRI", "LENGUAJES DE PROGRAMACION",
                        "CoolCompiler")
DIR = os.path.join(PRACTICA, "grading")
FICHEROS = os.listdir(DIR)
TESTS = [fich for fich in FICHEROS
         if os.path.isfile(os.path.join(DIR, fich))
         and fich.endswith(".cool")]
SINGLE_TESTS= [
#     "all_else_true.cl.cool",
#     "arith.cool",
#     "atoi.cool",
    # "backslash.cool",
    # "backslash2.cool",
    # "badkeywords.cool"
    # "bothcomments.cool"
#     "badidentifiers.cool",
#     "comment_in_string.cl.cool",
        # "eofstring.cool"
    # "escaped_chars_in_comment.cl.cool"
        # "escapedeof.cool"
        # "escapedquote.cool"
    # "escapednull.cool",
    # "escapedunprintables.cool"
#     "integers2.cool", 
    # "invalidcharacters.cool",
    # "invalidinvisible.cool"
#     "keywords.cool",
    # "longstring_escapedbackslashes.cool"
    # "nestedcomment.cool"
    # "null_in_string.cl.cool"
#     "life.cool",
    # "null_in_string_followed_by_tokens.cl.cool"
    # "null_in_string_unescaped_newline.cl.cool"
    # "lineno2.cool"
#     "null_in_string.cl.cool",
    # "opencomment.cool",
#     "operators.cool",
#     "palindrome.cool",
    # "pathologicalstrings.cool"
#     "twice_512_nested_comments.cl.cool",
#     "validcharacters.cool",
#     "weirdcharcomment.cool",
    # "s04.test.cool"
    # "s05.test.cool"
    # "s33.test.cool"
]

if SINGLE_TESTS:
    TESTS = SINGLE_TESTS

TESTS.sort()

CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                      for i in ['0','1']
                      for j in range(16)]

CARACTERES_CONTROL += [bytes.fromhex(hex(127)[-2:]).decode('ascii')]

class CommentLexer(Lexer):

    tokens = { COMMENT }
    
    _nivel = 0

    @_(r'\\\*|\\\)|\\\(')
    def escapedAndChars(self, t):
        pass

    @_(r'\(\*')
    def nestComment(self, t):
        self._nivel += 1

    @_(r'\*\)\Z|\n\Z|.\Z')
    def ignore_eofcomment(self, t):
        if '\n' in t.value:
            t.lineno += 1
        if '*)' in t.value and self._nivel == 0:
            self.begin(CoolLexer)
            return
        t.value = '"EOF in comment"'
        t.type = 'ERROR'
        self.begin(CoolLexer)
        return t    

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'\*\)')
    def ignore_comment(self, t):
        if self._nivel == 0:
            self.begin(CoolLexer)
            return
        self._nivel -= 1

    @_(r'.')
    def anyChar(self, t):
        pass



class StringLexer(Lexer):

    tokens = { STR_CONST }

    _valorStr = ''

    @_(r'\\\\')
    def escapedBackslash(self, t):
        self._valorStr += t.value

    @_(r'\\\n')
    def escapedLineBreak(self, t):
        self._valorStr += '\\n'
        self.lineno += 1

    @_(r'[^"]*\\\0[^"]*"')
    def escapedNull(self, t):
        self.begin(CoolLexer)
        t.type = 'ERROR'
        t.value = '"String contains escaped null character."'
        return t

    @_(r'\0[^"\n]*(\n|")')
    def nullCharacter(self, t):
        self.begin(CoolLexer)
        if '\n' in t.value:
            self.lineno += 1
        t.type = 'ERROR'
        t.value = '"String contains null character."'
        return t

    @_(r'\\(\t|\f|\x08)')
    def escapedEspecialChar(self, t):
        if t.value[1] == '\t':
            self._valorStr += '\\t'
        if t.value[1] == '\f':
            self._valorStr += '\\f'
        if t.value[1] == '\b':
            self._valorStr += '\\b'

    @_(r'.\Z|.\\\n\Z|\\"\Z')
    def inStringEOF(self, t):
        self.begin(CoolLexer)
        t.type = 'ERROR'
        t.value = '"EOF in string constant"'
        return t

    @_(r'\\[ntfb"]')
    def escapedNoEspecialChar(self, t):
        self._valorStr += t.value

    @_(r'\\.')
    def anyOtherEscapedChar(self, t):
        self._valorStr += t.value[1]

    @_(r'\x0d|\r|\015|\x1b|\t|\f|\022|\013')
    def unprintableCharacters(self, t):
        if t.value == '\t':
            self._valorStr += r'\t'
        elif t.value == '\f':
            self._valorStr += r'\f'
        elif t.value == '\r':
            self._valorStr += '\\015'
        elif t.value == '\x1b':
            self._valorStr += '\\033'
        elif t.value == '\022':
            self._valorStr += '\\022'
        elif t.value == '\013':
            self._valorStr += '\\013'

    @_(r'\n')
    def lineBreak(self, t):
        self.begin(CoolLexer)
        self._valorStr = ''
        self.lineno += 1
        t.lineno = self.lineno
        t.type = 'ERROR'
        t.value = '"Unterminated string constant"'
        return t

    @_(r'"')
    def StringOut(self, t):
        if self.countChars() > 1024:
            t.type = 'ERROR'
            t.value = '"String constant too long"'
        else:
            t.type = 'STR_CONST'
            t.value = f'"{self._valorStr}"' if t.value else '""'
        self._valorStr = ''
        self.begin(CoolLexer)
        return t

    @_(r'.')
    def anyChar(self, t):
        self._valorStr += t.value

    def countChars(self):
        totalchars = len(self._valorStr)
        newlines = self._valorStr.count('\\n')
        escapedBS = self._valorStr.count('\\\\')
        count = totalchars - newlines - escapedBS
        # print(count)
        return count


class CoolLexer(Lexer):
    keywords = {
        CLASS, ELSE, FI, IF, IN, INHERITS, ISVOID, LET,
        LOOP, POOL, THEN, WHILE, CASE, ESAC, NEW, OF, NOT
    }
    others = {
        GE, LE, ASSIGN, DARROW
    }

    tokens = keywords | others | { OBJECTID, INT_CONST, BOOL_CONST, TYPEID, STR_CONST }
    literals = {'=', '+', '-', '*', '/', '(', ')', '{', '}', ';', ':', '.', '~', ',', '@', '<'}

    CLASS = r'[cC][lL][aA][sS][sS]\b'
    ELSE = r'[eE][lL][sS][eE]\b'
    FI = r'[fF][iI]\b'
    IF = r'[iI][fF]\b'
    INHERITS = r'[iI][nN][hH][eE][rR][iI][tT][sS]\b'
    IN = r'[iI][nN]\b'
    ISVOID = r'[iI][sS][vV][oO][iI][dD]\b'
    LET = r'[lL][eE][tT]\b'
    LOOP = r'[lL][oO][oO][pP]\b'
    POOL = r'[pP][oO][oO][lL]\b'
    THEN = r'[tT][hH][eE][nN]\b'
    WHILE = r'[wW][hH][iI][lL][eE]\b'
    CASE = r'[cC][aA][sS][eE]\b'
    ESAC = r'[eE][sS][aA][cC]\b'
    NEW = r'[nN][eE][wW]\b'
    OF = r'[oO][fF]\b'
    NOT = r'[nN][oO][tT]\b'

    ASSIGN = r'<-'
    GE = r'>='
    LE = r'<='
    DARROW = r'=>'

    @_(r'\d+')
    def INT_CONST(self, t):
        return t

    @_(r'(t[rR][uU][eE]|f[aA][lL][sS][eE])\b')
    def BOOL_CONST(self, t):
        t.value = t.value.lower() == 'true'
        return t

    @_(r'[A-Z][a-zA-Z0-9_]*')
    def TYPEID(self, t):
        t.value = str(t.value)
        return t

    @_(r'"')
    def STR_CONST(self, t):
        self.begin(StringLexer)

    @_(r'\(\*')
    def COMMENT(self, t):
        self.begin(CommentLexer)

    @_(r'\*\)')
    def UNOPENED_COMMENT(self, t):
        t.type = 'ERROR'
        t.value = '"Unmatched *)"'
        return t

    @_(r'--.*')
    def ignore_comment(self, t):
        return t

    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):
        return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')
    
    @_(r'\s')
    def spaces(self, t):
        pass

    def error(self, t):
        t.type = 'ERROR'
        self.index += 1
        if t.value[0] == '\\':
            t.value = f'"\\\\"'
            return t
        if ord(t.value[0]) < 5:
            t.value = f'"\\00{ord(t.value[0])}"'
            return t
        t.value = f'"{t.value[0]}"'
        return t

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
        print(fich)
        lexer = CoolLexer()
        f = open(os.path.join(DIR, fich), 'r')
        g = open(os.path.join(DIR, fich + '.out'), 'r')
        resultado = g.read()
        texto = ''
        entrada = f.read()
        lexer_out = lexer.salida(entrada)
        texto = '\n'.join(lexer_out)
        if SINGLE_TESTS:
            print(texto)
        texto = f'#name "{fich}"\n' + texto
        f.close(), g.close()
        if texto.strip().split() != resultado.strip().split():
            print(f"Revisa el fichero {fich}")
            f = open(os.path.join(DIR, fich+'.txt'), 'w')
            f.write(texto)
            f.close()
            exit()
