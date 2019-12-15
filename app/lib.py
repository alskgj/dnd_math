"""

    lib.py
    ======

    Useful to calculate dnd stuff

a = Atk.from_string(+11 2d6+8)
a = Atk(to_hit=11, var_dmg='2d6', con_dmg=8)

dmg = a.expected_dmg(ac=15)
dmg = a.expected_dmg(ac=15, advantage=True)
dmg = a.expected_dmg(ac=15, reroll_ones=True)

"""
# standard library
import logging
import typing

from config import Config
from base64 import urlsafe_b64encode, urlsafe_b64decode
import json

# third party
from lark import Lark


class VarDmg:
    """
    Represents variable damage, which is determined by dice rolls.
    Rolling 3 dice which each have 20 sides is noted as 3d20.
    It is necessary to not just calculate the expected value of the dice roll, since
    those dice are not always rolled the same way (e.g. on a crit the number of rolled dice is doubled
    and a half orc may even reroll his worst attack die).
    """

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


class Attack:
    """
    Represents an attack and can calculate its expected dmg.
    Different types of attack:
    > +10 1d8+3    -> The standard attack, can crit, has a hit percentage and does 1d8+3 dmg on hit
    > 1d8+3        -> An attack like magic missile, always hits and can't crit
    > +6 6d8 (saving throw)  -> An attack life fireball, always hits. Only deals half damage if hostiles make the save
    ( not implemented)


    """
    def __init__(self, to_hit: typing.Union[None, int], var_dmg: typing.List[VarDmg], con_dmg=0, advantage=False):

        self.to_hit = to_hit
        self.var_dmg = var_dmg
        self.con_dmg = con_dmg
        self.advantage = advantage

    def __str__(self):
        """Short version string for endusers"""
        if self.to_hit is None:
            to_hit = ''
        elif self.to_hit > 0:
            to_hit = f'+{self.to_hit} '
        else:
            to_hit = f'(self.to_hit) '

        if self.con_dmg is None:
            con_dmg = ''
        elif self.con_dmg > 0:
            con_dmg = f'+{self.con_dmg}'
        else:
            con_dmg = str(self.con_dmg)

        v_string = "".join([str(v) for v in self.var_dmg])
        return f'{to_hit}{v_string}{con_dmg}'

    def __repr__(self):
        """Debug string"""
        if self.to_hit is None:
            to_hit = '[always hits]'
        elif self.to_hit > 0:
            to_hit = f'+{self.to_hit}'
        else:
            to_hit = str(self.to_hit)

        v_string = " ".join([str(v) for v in self.var_dmg])

        return f'Attack: {to_hit} {v_string} {self.con_dmg}, E[damage against ac 15]: {self.expected_damage(15)}'

    @classmethod
    def from_string(cls, atk_string: str):
        """ #
        Parses the DSL to describe a dnd attack.
        Accepted patterns:
        +10 2d8
        +10 2d8+4
        +10 10-3 + 5 - 2 3d8 + 2d8 -1d8
        2d8-2
        2d8
        ...

        :param atk_string: '+hitchance (var_dmg+con_dmg)+' for example '+11 3d8+3'
        :return: an Attack object
        """

        syntax = Config().attack_syntax
        lark = Lark(syntax)
        line = lark.parse(atk_string).children[0]

        to_hit, var_dmg, con_dmg, advantage = None, [], 0, False
        for t in line.children:
            if t.data == 'mod':
                if t.children[0].type == 'ADVANTAGE':
                    advantage = True
                elif t.children[0].type == 'DISADVANTAGE':
                    logging.error("Disadvantage is not implemented")
            if t.data == 'tohit':
                multiplier = 1
                for child in t.children:
                    if child.value == '-':
                        multiplier = -1
                    if child.type == 'NUMBER':
                        to_hit = int(child.value) * multiplier

            elif t.data == 'condmg':
                multiplier = 1
                for child in t.children:
                    if child.value == '-':
                        multiplier = -1
                    if child.type == 'NUMBER':
                        con_dmg += int(child.value) * multiplier

            elif t.data == 'vardmg':
                kids = t.children
                sign = '+'
                if len(kids) == 4:
                    sign = kids[0].value
                    number, die = int(kids[1].value), int(kids[3].value)
                else:
                    number, die = int(kids[0].value), int(kids[2].value)
                var_dmg.append(VarDmg(number, die, sign))

        return cls(to_hit, var_dmg, con_dmg, advantage)

    def expected_damage(self, ac, crit_chance=0.05, advantage=False, round_=True):
        """
        Given some parameters, what damage can be expected

        :param ac: armor class, typically between 10 and 20
        :param crit_chance: The chance to critically hit, typically 1/20, sometimes 1/10
        :param crit_modifier: The crit dmg modifier, typically 2, sometimes (e.g. half-orcs) 3
        :param advantage: True if we have advantage, else false. Defaults to false
        :return:
        """

        # if 1d20 + self.to_hit >= ac, we have a hit
        # 1 never hits, 20 always hits
        if self.to_hit is None:
            return self.expected_damage_always_hit()

        # two dice can roll critically, then we subtract the overlap
        if advantage:
            crit_chance = 2*crit_chance - crit_chance**2

        expected_dmg = self.chance_to_hit(ac, advantage) * self.dmg
        expected_dmg_w_crit = expected_dmg + crit_chance*self.total_var_dmg

        if round_:
            return round(expected_dmg_w_crit, 2)
        else:
            return expected_dmg_w_crit

    @property
    def total_var_dmg(self):
        """Noncritical var_dmg"""
        return sum([v.expected_dmg for v in self.var_dmg])

    @property
    def dmg(self):
        """Noncritical total dmg"""
        return self.total_var_dmg + self.con_dmg

    def chance_to_hit(self, ac, advantage=False):
        chance_to_hit = (21 - (ac - self.to_hit))/20
        if chance_to_hit > 0.95:
            chance_to_hit = 0.95
        if chance_to_hit < 0.05:
            chance_to_hit = 0.05

        if advantage:
            chance_to_hit = 1 - (1-chance_to_hit)**2
        return chance_to_hit

    def expected_damage_always_hit(self):
        """For attacks like magic missile that can't crit"""
        return self.total_var_dmg + self.con_dmg


class Combat:
    def find_breakpoint(self, atk1: Attack, atk2: Attack, advantage=False):
        """Given two attacks finds against what AC one should use atk1 vs atk2"""

        first = max(atk1, atk2, key=lambda a: a.expected_damage(1, advantage=advantage))
        first_ac = 1
        last_ac = 1
        for i in range(1, 40):
            better = max(atk1, atk2, key=lambda a: a.expected_damage(i, advantage=advantage))
            if first == better:
                last_ac = i
            else:
                e1, e2 = atk1.expected_damage(i), atk2.expected_damage(i)
                print(f"Use {first} from ac {first_ac} to ac {last_ac}")
                first, first_ac, last_ac = better, i, i
        print(f"Use {first} from ac {first_ac}+")


def form_encode(arg: dict):
    """Takes an attack and returns its b64 representation"""
    # ensure we only take valid keys
    new_attacks = []
    for attack in arg[:5]:
        new_subattacks = []
        for sub_attack in attack['sub_attacks'][:5]:
            new_subattacks.append({'attack': sub_attack['attack']})
        new_attacks.append({'sub_attacks': new_subattacks})
    return urlsafe_b64encode(json.dumps(new_attacks).encode()).decode()

def form_decode(arg: str):
    return json.loads(urlsafe_b64decode(arg).decode())


if __name__ == '__main__':
    # simulate lvl 11 fighter

    print(Attack.from_string('1d8 +10d7+1 + 3d5'))

