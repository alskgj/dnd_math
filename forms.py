from flask_wtf import FlaskForm
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class AttackForm(FlaskForm):
    """Contact form."""
    dmg_string1 = StringField(
        label='Attack one',
        validators=[DataRequired(), Regexp(regex=r'\+\d+ \d+d\d+\+\d+', message='Not in the form +4 1d8+2')]
    )
    dmg_string2 = StringField(
        label='Attack two',
        validators=[Regexp(regex=r'\+\d+ \d+d\d+\+\d+', message='Not in the form +4 1d8+2')]
    )
    submit = SubmitField('Submit')
