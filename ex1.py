
import re

ID = r'(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)'
NUMBER = r'(?P<NUMBER>\d+)'
SPACE = r'(?P<SPACE>\s+)'

patterns = [ID, NUMBER, SPACE]

# Expresión regular general
pat = re.compile('|'.join(patterns))

def tokenize(text):
    index = 0
    while index < len(text):
        m = pat.match(text,index)
        if m:
            yield (m.lastgroup, m.group())
            index = m.end()
        else:
            raise SyntaxError('Bad char %r' % text[index])

# Ejemplo de uso
text = 'abc 123 cde 456'

for tok in tokenize(text):
    print(tok)
