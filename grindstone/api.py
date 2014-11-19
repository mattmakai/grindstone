from flask import request, jsonify, redirect, url_for, Response
from flask.ext.login import login_required, current_user

from . import app, db, login_manager, redis_db, socketio


@app.route('/api/drinks/<time_period>/', methods=['GET'])
@login_required
def drinks_data(time_period):
    return Response(json.dumps([{"date": "2014-09-06", "drinks": 0},
                                {"date": "2014-09-07", "drinks": 2}]), 
            mimetype='application/json')

