from flask import Flask, render_template, request, redirect, url_for
import os

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


def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("werkzeug").setLevel(logging.WARNING)


def make_graphjson(atks: typing.List[Attack], name=None):
    ac_range = range(24, 8, -1)
    x = list(ac_range)

    data = list()
    for atk in atks:
        name = atk.atk_string
        y = [atk.expected_damage(i) for i in x]
        data.append({'x': x, 'y': y, 'type': 'scatter', 'name': name})

    graphs = [
        {
            'data': data,
            'layout': {'title': 'calculation'}
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
        atks = []
        for entry in attackform.attacks:
            try:
                atks.append(Attack.from_string(entry.data['attack']))
            except ValueError:
                pass

        ids, graphjson = make_graphjson(atks)

        return render_template('m.html', form=attackform, adder=adderform, ids=ids, graphJSON=graphjson)

    return render_template('m.html', form=attackform, adder=adderform)


if __name__ == '__main__':
    setup_logging()
    app.run(host='0.0.0.0', port=80, debug=False)
