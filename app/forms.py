from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Regexp, ValidationError
import lib

import lark


class SubAttackEntryForm(FlaskForm):
    attack = StringField()
    advantage = BooleanField(label='advantage')

    def validate_attack(self, field):
        try:
            lib.Attack.from_string(field.data)
        except lark.exceptions.UnexpectedCharacters as larkerror:
            raise ValidationError(str(larkerror))
        except lark.exceptions.UnexpectedEOF as larkerror:
            raise ValidationError(str(larkerror))


class AttackEntryForm(FlaskForm):
    sub_attacks = FieldList(FormField(SubAttackEntryForm), min_entries=1)
    add_subattack = SubmitField('+')
    remove_subattack = SubmitField('-')


class AttackForm(FlaskForm):
    """A form for one or more attacks"""
    attacks = FieldList(FormField(AttackEntryForm), min_entries=1)
    attack_submit = SubmitField('Attack')


class AddForms(FlaskForm):
    add_submit = SubmitField('Add Attack')
    remove_submit = SubmitField('Remove Attack')
