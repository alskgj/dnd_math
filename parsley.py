from lark import Lark

syntax = """
start: line

line        : (tohit)? (vardmg | condmg)+ 
tohit       : SIGN NUMBER WHITESPACE 
vardmg      : SIGN? NUMBER D NUMBER 
condmg      : SIGN? NUMBER 

NUMBER              : ("0".."9")+
WHITESPACE          : (" "|"\\n")+
%ignore WHITESPACE
SIGN                : ("+"|"-")
D                   : "d"
"""


class VarDmg:
    def __init__(self, number: int, die: int, sign='+'):
        self.number = number
        self.die = die
        self.sign = sign

    @classmethod
    def from_string(cls, vardmg: str):
        number, die = vardmg.split('d')
        return cls(int(number), int(die))

    @property
    def expected_dmg(self):
        """This returns expected NONCRITICAL damage"""
        return self.number * (self.die+1)/2

    @property
    def expected_critical_dmg(self):
        # todo implement half-orc
        return 2*self.expected_dmg

    def __repr__(self):
        return f'{self.sign}{self.number}d{self.die}'


def parse(attackstring):
    """
    Parses the DSL to describe a dnd attack.
    This will parse

    parse("+10 10-3 + 5 - 2 3d8 + 2d8 -1d8") -->

    tohit: 10
    condmg: 10
    vardmg: [+3d8, +2d8, -1d8]


    """
    lark = Lark(syntax)
    line = lark.parse(attackstring).children[0]

    tohit = None
    condmg = 0
    vardmg = []
    for t in line.children:
        if t.data == 'tohit':
            multiplicator = 1
            for t in t.children:
                if t.value == '-':
                    multiplicator = -1
                if t.type == 'NUMBER':
                    tohit = int(t.value)*multiplicator

        elif t.data == 'condmg':
            multiplicator = 1
            for t in t.children:
                if t.value == '-':
                    multiplicator = -1
                if t.type == 'NUMBER':
                    condmg += int(t.value)*multiplicator

        elif t.data == 'vardmg':
            kids = t.children
            sign = '+'
            if len(kids) == 4:
                sign = kids[0].value
                number, die = int(kids[1].value), int(kids[3].value)
            else:
                number, die = int(kids[0].value), int(kids[2].value)
            vardmg.append(VarDmg(number, die, sign))

    print(f'tohit: {tohit}')
    print(f'condmg: {condmg}')
    print(f'vardmg: {vardmg}')



if __name__ == '__main__':
    parse("+10 10-3 + 5 - 2 3d8 + 2d8 -1d8")