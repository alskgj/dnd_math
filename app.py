from flask import Flask, render_template
import os

import json
import plotly

from lib import Attack
from forms import AttackForm

import typing

app = Flask(__name__)
app.debug = True

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


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
def buttons():
    form = AttackForm()
    if not form.dmg_string1.errors and not form.dmg_string2.errors and form.dmg_string1.data:
        atk1 = Attack.from_string(form.dmg_string1.data)
        if form.dmg_string2.data:
            atk2 = Attack.from_string(form.dmg_string2.data)
            ids, graphjson = make_graphjson([atk1, atk2])
        else:
            ids, graphjson = make_graphjson([atk1])

        return render_template(
            'index.html',
            form=form,
            ids=ids,
            graphJSON=graphjson)

    return render_template('index.html', form=form)


@app.route('/poc')
def poc():

    atk1 = Attack.from_string('+2 1d8+14')
    atk2 = Attack.from_string('+8 1d8+5')

    acrange = range(24, 8, -1)

    x = list(acrange)

    y1 = [atk1.expected_damage(i) for i in x]
    y2 = [atk2.expected_damage(i) for i in x]

    atk3 = Attack.from_string('+7 1d8+18')
    atk4 = Attack.from_string('+13 1d8+9')

    y3 = [atk3.expected_damage(i) for i in x]
    y4 = [atk4.expected_damage(i) for i in x]

    # with advantage
    y5 = [atk3.expected_damage(i, advantage=True) for i in x]
    y6 = [atk4.expected_damage(i, advantage=True) for i in x]



    graphs = [
        {
            'data': [{'x': x, 'y': y1, 'type': 'scatter', 'name': '+3 int, sharpshooter'},
                     {'x': x, 'y': y2, 'type': 'scatter', 'name': '+4 int'}],
            'layout': {'title': 'lvl 5'}
        },
        {
            'data': [{'x': x, 'y': y3, 'type': 'scatter', 'name': '+4 int, sharpshooter'},
                     {'x': x, 'y': y4, 'type': 'scatter', 'name': '+5 int'},
                     {'x': x, 'y': y5, 'type': 'scatter', 'name': '+4 int, sharpshooter, advantage'},
                     {'x': x, 'y': y6, 'type': 'scatter', 'name': '+5 int, advantage'}],
            'layout': {'title': 'lvl 11'}
        }
    ]

    ids = [f'graph-{i}' for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)


    return render_template(
        'poc.html',
        ids=ids,
        graphJSON=graphJSON)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9999, debug=False)
