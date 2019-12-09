from flask import Flask, render_template, request, redirect, url_for
import os
from flask_wtf import FlaskForm
import json
import plotly

from lib import Attack
from forms import AttackForm2, AddForms

import typing
import logging

app = Flask(__name__)
app.debug = True

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['attacks'] = [{'attack': '+10 2d8+4'}]


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


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def make_graphjson(atks: typing.List[UserInput], name=None):
    ac_range = range(34, 2, -1)
    x = list(ac_range)

    data = list()
    for atk in atks:
        name = atk.attack.atk_string + atk.advantage*" (advantage)"

        y = [atk.attack.expected_damage(i, advantage=atk.advantage) for i in x]
        data.append({'x': x, 'y': y, 'type': 'scatter', 'name': name})

    graphs = [
        {
            'data': data,
            'layout': {
                'title': 'Expected damage depending on enemy AC',
                'xaxis': {'title': 'Enemy Armor Class'},
                'yaxis': {'title': 'Expected damage'}
            }
        },
    ]

    ids = [f'graph-{i}' for i, _ in enumerate(graphs)]


    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphjson= json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return ids, graphjson


@app.route('/', methods=('GET', 'POST'))
def index():
    attackform = AttackForm2(attacks=app.config["attacks"])
    adderform = AddForms()

    # add or remove buttons
    if adderform.validate_on_submit() and adderform.add_submit.data:
        app.config['attacks'].append({'attack': f'+10 2d8+{len(app.config["attacks"])}'})
        return redirect(url_for('index'))
    if adderform.validate_on_submit() and adderform.remove_submit.data:
        if len(app.config['attacks']) > 1:
            app.config['attacks'] = app.config['attacks'][:-1]
        return redirect(url_for('index'))

    # generate graph
    if attackform.validate_on_submit() and attackform.attack_submit.data:
        form_data = []
        for entry in attackform.attacks:
            ui = UserInput(entry)
            if ui.valid:
                form_data.append(ui)

        ids, graphjson = make_graphjson(form_data)

        return render_template('m.html', form=attackform, adder=adderform, ids=ids, graphJSON=graphjson)

    return render_template('m.html', form=attackform, adder=adderform)


if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=8000, debug=False)
