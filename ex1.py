
import re

ID = r'(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)'
NUMBER = r'(?P<NUMBER>\d+)'
SPACE = r'(?P<SPACE>\s+)'

patterns = [ID, NUMBER]
ignored_patterns = [SPACE]

# Expresión regular general
pat = re.compile('|'.join(patterns))
pat_ignore = re.compile('|'.join(ignored_patterns))

def tokenize(text):
    index = 0
    while index < len(text):
        m = pat.match(text,index)
        if m:
            yield (m.lastgroup, m.group())
            index = m.end()
            continue
        ign_m = pat_ignore.match(text,index)
        if ign_m:
            index = ign_m.end()
            continue    
        raise SyntaxError('Bad char %r' % text[index])

# Ejemplo de uso
text = 'abc 123 cde 456'

for tok in tokenize(text):
    print(tok)
