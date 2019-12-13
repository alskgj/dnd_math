from lark import Lark
from config import Config



def parse(attackstring):
    """
    Parses the DSL to describe a dnd attack.
    This will parse

    parse("+10 10-3 + 5 - 2 3d8 + 2d8 -1d8") -->

    tohit: 10
    condmg: 10
    vardmg: [+3d8, +2d8, -1d8]

    """
    syntax = Config().attack_syntax
    lark = Lark(syntax)
    line = lark.parse(attackstring).children[0]

    to_hit = None
    condmg = 0
    vardmg = []
    for t in line.children:
        if t.data == 'tohit':
            multiplier = 1
            for child in t.children:
                if child.value == '-':
                    multiplier = -1
                if child.type == 'NUMBER':
                    to_hit = int(t.value)*multiplier

        elif t.data == 'condmg':
            multiplier = 1
            for child in t.children:
                if child.value == '-':
                    multiplier = -1
                if child.type == 'NUMBER':
                    condmg += int(t.value)*multiplier

        elif t.data == 'vardmg':
            kids = t.children
            sign = '+'
            if len(kids) == 4:
                sign = kids[0].value
                number, die = int(kids[1].value), int(kids[3].value)
            else:
                number, die = int(kids[0].value), int(kids[2].value)
            vardmg.append(VarDmg(number, die, sign))

    print(f'tohit: {to_hit}')
    print(f'condmg: {condmg}')
    print(f'vardmg: {vardmg}')



if __name__ == '__main__':
    parse("+10 10-3 + 5 - 2 3d8 + 2d8 -1d8")