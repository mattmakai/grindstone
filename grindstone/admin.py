from flask import request, render_template, jsonify

from . import app, db, redis_db, socketio
from .models import Follower, Service


@app.route('/admin/', methods=['GET'])
def admin():
    return render_template('admin/admin_panel.html')
