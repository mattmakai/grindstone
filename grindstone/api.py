import json
from datetime import datetime

from flask import request, jsonify, redirect, url_for, Response
from flask.ext.login import login_required, current_user

from .models import DayInput
from .tasks import add_drinks_to_tracker
from . import app, db, login_manager, redis_db, socketio


@app.route('/api/drinks/<time_period>/', methods=['GET'])
@login_required
def drinks_data(time_period):
    year, month, day = datetime.now().year, datetime.now().month, \
                       datetime.now().day
    a_year_ago = datetime(year=year-1, month=month, day=day)
    day_inputs = DayInput.query.filter(DayInput.timestamped>a_year_ago). \
                                       order_by(DayInput.timestamped.desc())
    day_inputs_json = []
    for di in day_inputs:
        day_inputs_json = di.to_json()
    return Response(json.dumps([{"date": "2014-09-06", "drinks": 0},
                                {"date": "2014-09-07", "drinks": 2}]), 
            mimetype='application/json')


@app.route('/api/drinks/<int:year>/<int:month>/<int:day>/decr/', 
           methods=['POST'])
@login_required
def decr_drinks(year, month, day):
    drinks = add_drinks_to_tracker(year, month, day, -1)
    return jsonify({'drinks': drinks})


@app.route('/api/drinks/<int:year>/<int:month>/<int:day>/incr/', 
           methods=['POST'])
@login_required
def incr_drinks(year, month, day):
    drinks = add_drinks_to_tracker(year, month, day, 1)
    return jsonify({'drinks': drinks})
