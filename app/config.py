"""
    config.py
    =========

    Get your config from here
"""


class Config:
    ATTACK_SYNTAX_PATH = "attack.bnf"

    def __init__(self):
        pass

    @property
    def attack_syntax(self):
        """Returns the attack syntax in lark format"""
        with open(self.ATTACK_SYNTAX_PATH) as fo:
            data = fo.read()
        return data

