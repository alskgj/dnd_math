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
import math
import re
import logging


class Attack:
    def __init__(self, to_hit: int, var_dmg: str, con_dmg=8):
        assert re.match(r'\d+d\d|', var_dmg), "var_dmg is not in the right format. example: 3d8"
        self.to_hit = to_hit

        # calculate expected damage from var_dmg
        # example 3d8 = 13.5
        times, dice = var_dmg.split('d')
        self.expected_var_dmg = int(times) * (int(dice)+1)/2 # we need to store this separately for crits
        self.dmg = con_dmg + self.expected_var_dmg

        self.atk_string = f'+{to_hit} {var_dmg}+{con_dmg}'

    def __str__(self):
        return f'Attack [{self.atk_string}]'

    @classmethod
    def from_string(cls, atk_string: str):
        """
        Accepted patterns:
        +10 2d8
        +10 2d8+4
        -10 2d8+4
        -10 2d8-2
        +10 2d8-2

        :param atk_string: '+hitchance var_dmg+con_dmg' for example '+11 3d8+3'
        :return: an Attack object
        """
        pattern = re.compile(r'^([+-])(\d+) (\d+d\d+)(([+-])(\d+))?$')
        atk_string = atk_string.strip()
        if not pattern.match(atk_string):
            logging.critical("Not a valid pattern: %s", atk_string)
            raise ValueError('Can\'t build attack from string [%s]' % atk_string)

        tmp = pattern.findall(atk_string)[0]
        to_hit = int(tmp[1])
        if tmp[0] == '-':
            to_hit *= -1
        var_dmg = tmp[2]
        if tmp[4] and tmp[5]:
            con_dmg = int(tmp[5])
            if tmp[4] == '-':
                con_dmg *= -1
        else:
            con_dmg = 0
        logging.debug(f'parsed {atk_string} to {to_hit} {var_dmg} + {con_dmg}')

        return cls(to_hit, var_dmg, con_dmg)

    def expected_damage(self, ac, crit_chance=0.05, crit_modifier=2, advantage=False, round_=True):
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

        chance_to_hit = (21 - (ac - self.to_hit))/20
        if chance_to_hit > 0.95:
            chance_to_hit = 0.95
        if chance_to_hit < 0.05:
            chance_to_hit = 0.05

        if advantage:
            chance_to_hit = 1 - (1-chance_to_hit)**2
            crit_chance = 2*crit_chance

        expected_dmg = chance_to_hit * self.dmg
        expected_dmg_w_crit = expected_dmg + self.expected_var_dmg*crit_chance*crit_modifier

        if round_:
            return round(expected_dmg_w_crit, 2)
        else:
            return expected_dmg_w_crit

    def var_dmg(self, times, dices, reroll_ones=False):
        if reroll_ones:
            dont_reroll = ((dices-1)/dices) * ((2+dices)/2)
            reroll = (1/dices) * ((1+dices)/2)
            expected_dmg = reroll + dont_reroll
        else:
            expected_dmg = (1+dices)/2

        return times * expected_dmg


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


if __name__ == '__main__':
    # simulate lvl 11 fighter
    atk1 = Attack.from_string('+11 2d6+5')
    atk2 = Attack.from_string('+6 2d6+15')

    c = Combat()
    c.find_breakpoint(atk1, atk2)

    # simulate lvl 3 sorcerer
    atk1 = Attack.from_string('+100 3d4+1')
    atk2 = Attack.from_string('+6 3d8+0')
    print('')
    c.find_breakpoint(atk1, atk2)

    # compare ranged with gfb battle smith
    atk1 = Attack.from_string('+10 1d8+8')
    atk2 = Attack.from_string('+5 1d8+18')

    gfb_attack = Attack.from_string('+11 4d8+7')

    print(f'expected dmg for bsmith wo ss: {atk1.expected_damage(ac=14)*2}')
    print(f'expected dmg for bsmith w ss:  {atk2.expected_damage(ac=14)*2}')
    print(f'expected dmg for bsmith w gfb: {gfb_attack.expected_damage(ac=17)}')

    c.find_breakpoint(atk1, atk2, advantage=False)
    print()

    cbe_wo_ss = Attack.from_string('+10 1d6+4')
    cbe_w_ss = Attack.from_string('+5 1d6+14')

    # use better weapon
    cbe_wo_ss = Attack.from_string('+11 1d6+5')
    cbe_w_ss = Attack.from_string('+6 1d6+15')

    lb_wo_ss = Attack.from_string('+12 1d8+8')
    lb_w_ss = Attack.from_string('+7 1d8+18')

    attacks = {
        'Crossbow expert without sharpshooter:': cbe_wo_ss,
        'Crossbow expert with sharpshooter:   ': cbe_w_ss,
        'Longbow user without sharphooter:    ': lb_wo_ss,
        'Longbow user with sharphooster:      ': lb_w_ss,
    }
    for ac in [13, 15, 17, 19]:
        for atk in attacks:
            edmg = attacks[atk].expected_damage(ac=ac)
            if 'Crossbow' in atk:
                edmg *= 3
            else:
                # without crossbow we use the bonus action to give advantage
                edmg += attacks[atk].expected_damage(ac=ac, advantage=True)

            print(f'expected dmg against ac {ac} for {atk}', round(edmg, 2))
        print()



