import json

from flask import request, jsonify, redirect, url_for, Response
from flask.ext.login import login_required, current_user

from .tasks import add_drinks_to_tracker
from . import app, db, login_manager, redis_db, socketio


@app.route('/api/drinks/<time_period>/', methods=['GET'])
@login_required
def drinks_data(time_period):
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
