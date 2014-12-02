import json
from datetime import datetime

import arrow
from flask import request, jsonify, redirect, url_for, Response
from flask.ext.login import login_required, current_user

from .models import DayTrack, Service
from .tasks import add_drinks_to_tracker
from . import app, db, login_manager, redis_db, socketio


@app.route('/api/', methods=['GET'])
def list_endpoints():
    routes = {'daytrackers_url': url_for('list_daytrackers', _external=True),
              'services_url': url_for('list_services', _external=True)}
    return Response(json.dumps(routes), mimetype="application/json")


@app.route('/api/daytracks/', methods=['GET'])
@login_required
def list_daytrackers():
    daytracks_json = []
    for d in DayTrack.query.all():
        daytracks_json.append({'url': d.permalink})
    return Response(json.dumps(daytracks_json), mimetype="application/json")


@app.route('/api/daytrack/<int:id>/', methods=['GET'])
@login_required
def get_daytrack(id):
    return jsonify(DayTrack.query.get_or_404(id).to_json())


@app.route('/api/services/', methods=['GET'])
def list_services():
    services_json = []
    for s in Service.query.all():
        services_json.append({'url': s.permalink})
    return Response(json.dumps(services_json), mimetype="application/json")


@app.route('/api/service/<int:id>/', methods=['GET'])
@login_required
def get_service(id):
    return jsonify(Service.query.get_or_404(id).to_json())



@app.route('/api/drinks/', methods=['GET'])
@login_required
def list_drinks():
    """
        Returns a JSON list with all drinks per day in the last year.
    """
    year_ago = arrow.now(years=-1)
    return list_drinks_since_date(year_ago.year, year_ago.month, year_ago.day)


@app.route('/api/drinks/<int:year>/<int:month>/<int:day>/', methods=['GET'])
@login_required
def list_drinks_since_date(year, month, day):
    year_ago = arrow.Arrow(year, month, day)
    day_inputs = DayTrack.query.filter(DayTrack.timestamped>year_ago). \
                                       order_by(DayTrack.timestamped.desc())
    day_inputs_json = []
    for di in day_inputs:
        day_inputs_json = di.to_json()
    return Response(json.dumps(day_inputs_json, mimetype="application/json"))
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
