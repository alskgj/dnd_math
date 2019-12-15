from flask import Flask, render_template, session, redirect, url_for, request
import os
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
import json
import plotly

from lib import Attack
from forms import AttackForm, AddForms
import binascii
import typing
import logging
from lib import form_encode, form_decode

app = Flask(__name__)
app.debug = True

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# TODO - remove UserInput class
# TODO - replace the 'placeholde' name with something better
# TODO - write syntax section


class UserInput:
    def __init__(self, form: FlaskForm):
        """Takes a form and extracts the information"""
        data = form.data

        try:
            self.attack = Attack.from_string(data['attack'])
        except ValueError:
            self.valid = False
        else:
            self.valid = True

        self.advantage = data['advantage']

    def __repr__(self):
        return f'{self.attack} advantage: {self.advantage}'


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("werkzeug").setLevel(logging.INFO)


def make_graphjson(atks: typing.List[typing.List[UserInput]]):
    ac_range = list(range(34, 2, -1))

    data = list()
    for atk in atks:

        total_dmg = [0 for _ in ac_range]
        for sub_attack in atk:
            for i, ac in enumerate(ac_range):
                total_dmg[i] += sub_attack.attack.expected_damage(ac, advantage=sub_attack.attack.advantage)
        name = 'placeholder'

        data.append({'x': ac_range, 'y': total_dmg, 'type': 'scatter', 'name': name})

    maxy = 0
    for element in data:
        for dmg in element['y']:
            if dmg > maxy:
                maxy = int(dmg)+1

    graphs = [
        {
            'data': data,
            'layout': {
                'height': 600,
                'title': 'Expected damage depending on enemy AC',
                'xaxis': {'title': 'Enemy Armor Class', 'range': [5, 25]},
                'yaxis': {'title': 'Expected damage', 'range': [0, maxy]}
            }
        },
    ]

    ids = [f'graph-{i}' for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphjson= json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return ids, graphjson


@app.route('/short/<arg>', methods=('GET', 'POST'))
def short(arg):
    new_attacks = []
    try:
        ui = form_decode(arg)
    except binascii.Error:
        return redirect("/")

    # ensure we only take valid keys
    for attack in ui[:5]:
        new_subattacks = []
        for sub_attack in attack['sub_attacks'][:5]:
            new_subattacks.append({'attack': sub_attack['attack']})
        new_attacks.append({'sub_attacks': new_subattacks})

    return render_template('index.html', form=AttackForm(attacks=new_attacks))


@app.route('/', methods=('GET', 'POST'))
def index():
    if 'atks' not in session:
        session['atks'] = [
            {'sub_attacks':
                [{'attack': '3d4+1'},
                 {'attack': '+4 3d8'},
                 {'attack': '+1 3d8'},
                 ],
             },
            {'sub_attacks':
                [{'attack': '+8 1d8+5'}],
             }
        ]
    attackform = AttackForm(attacks=session["atks"])

    if attackform.validate_on_submit() and attackform.attack_submit.data:

        form_data = []
        for entry in attackform.attacks:
            current = []
            for attack in entry.sub_attacks:
                ui = UserInput(attack)
                if ui.valid:
                    current.append(ui)
                    logging.info("got %s", ui.attack)
            form_data.append(current)
        ids, graphjson = make_graphjson(form_data)
        return render_template('index.html', form=attackform, ids=ids, graphJSON=graphjson,
                               sharelink=form_encode(attackform.attacks.data))

    return render_template('index.html', form=attackform)


if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=8000, debug=False)
