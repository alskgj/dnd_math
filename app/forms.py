from flask_wtf import FlaskForm

from wtforms import StringField, SubmitField, FieldList, FormField, BooleanField
from wtforms.validators import DataRequired, Regexp, ValidationError
import lib

import lark


class AttackEntryForm(FlaskForm):
    attack = StringField()
    advantage = BooleanField(label='advantage')

    def validate_attack(form, field):
        try:
            lib.Attack.from_string(field.data)
        except lark.exceptions.UnexpectedCharacters as larkerror:
            raise ValidationError(str(larkerror))
        except lark.exceptions.UnexpectedEOF as larkerror:
            raise ValidationError(str(larkerror))


class AttackForm2(FlaskForm):
    """A form for one or more attacks"""
    attacks = FieldList(FormField(AttackEntryForm), min_entries=1)
    attack_submit = SubmitField('Attack')


class AddForms(FlaskForm):
    add_submit = SubmitField('Add Attack')
    remove_submit = SubmitField('Remove Attack')
