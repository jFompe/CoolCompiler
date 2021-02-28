# simplelex.py

from sly import Lexer

class SimpleLexer(Lexer):
    # Token names
    tokens = { NUMBER, ID }

    # Ignored characters
    ignore = ' \t'

    # Token regexs
    NUMBER = r'\d+'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    @_(r'\n+')
    def ignore_newline(self,  t):
        self.lineno += t.value.count('\n')
        
    def error(self, t):
        print('Bad character %r' % t.value[0])
        self.index += 1

# Example
if __name__ == '__main__':
    text = 'abc 123 $ cde 456'
    lexer = SimpleLexer()
    for tok in lexer.tokenize(text):
        print(tok)
