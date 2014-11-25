import json
import requests

from datetime import datetime
from flask import request, render_template, jsonify, redirect, url_for, \
                  Response
from flask.ext.login import login_user, logout_user, login_required, \
                            current_user
from requests_oauthlib import OAuth2Session

from . import app, db, login_manager, redis_db, socketio
from .forms import LoginForm
from .models import User, Developer, Follower, Service, DayInput
from .tasks import github_follower_count, add_or_replace_follower_count, \
                   add_or_replace_day_tracker, find_day_input, \
                   set_day_tracker, find_today_input
from .config import GOOGLE_CLIENT_SID, GOOGLE_CLIENT_SECRET, \
                    GOOGLE_REDIRECT_URL


authorization_base_url = "https://accounts.google.com/o/oauth2/auth"
token_url = "https://accounts.google.com/o/oauth2/token"
scope = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
]



@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.route('/', methods=['GET'])
def public_view():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return redirect(url_for('sign_in'))


@app.route('/sign-in/', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main'))
    return render_template('public/sign_in.html', form=form, no_nav=True)


@app.route('/sign-out/')
@login_required
def sign_out():
    logout_user()
    return redirect(url_for('public_view'))



@app.route('/app/', methods=['GET'])
@login_required
def main():
    gh = Service.query.filter_by(name='GitHub').first()
    gh_followers = Follower.query.filter_by(service=gh.id).order_by( \
        Follower.timestamped.desc()).first()
    google = Service.query.filter_by(name='Google').first()
    gmail_emails = Follower.query.filter_by(service=google.id).order_by( \
        Follower.timestamped.desc()).first()
    return render_template('app/main.html', github_followers=gh_followers,
                           gmail_emails=gmail_emails, today=datetime.now())


@app.route('/app/input/', methods=['GET', 'POST'])
def input_today():
    day_tracker = add_or_replace_day_tracker(datetime.now().year, 
                                        datetime.now().month, 
                                        datetime.now().day)
    return render_template('app/input.html', today=datetime.now(), 
                           year=datetime.now().year, day_tracker=day_tracker,
                           month=datetime.now().month, day=datetime.now().day)


@app.route('/app/day/<int:year>/<int:month>/<int:day>/', 
           methods=['GET'])
@login_required
def day(year, month, day):
    find_date = datetime(year=year, month=month, day=day)
    di = find_day_input(year, month, day)
    if not di:
        di = DayInput(find_date)
    return render_template('app/day.html', year=year, month=month, day=day,
                           today=datetime.now(), di=di)


@app.route('/app/day/toggle/<int:year>/<int:month>/<int:day>/<tracker>/', 
           methods=['GET'])
@login_required
def day_toggle(year, month, day, tracker):
    set_day_tracker(year, month, day, tracker)
    return Response('OK', 200)


@app.route('/app/authorize-apis/', methods=['GET'])
def authorize_apis():
    google = OAuth2Session(GOOGLE_CLIENT_SID, scope=scope,
        redirect_uri=GOOGLE_REDIRECT_URL)
    authorization_url, state = google.authorization_url(authorization_base_url,
        access_type="offline", approval_prompt="force")
    return render_template('app/authorize.html', google_url=authorization_url,
                           today=datetime.now())


@app.route('/oauth2callback', methods=['GET'])
def oauth2callback_google():
    google = OAuth2Session(GOOGLE_CLIENT_SID, scope=scope,
                           redirect_uri=GOOGLE_REDIRECT_URL)
    response = google.fetch_token(token_url, 
                                  client_secret=GOOGLE_CLIENT_SECRET,
                                  authorization_response=request.url)
    token = response['access_token']
    user = User.query.get(current_user.id)
    user.google_access_token = token
    db.session.merge(user)
    db.session.commit()
    return redirect(url_for('gmail_email_count'))


@app.route('/app/gmail/emails', methods=['GET'])
def gmail_email_count():
    r = OAuth2Session(r'%s' % GOOGLE_CLIENT_SID, 
                      token={'access_token': current_user.google_access_token,
                             'token_type': 'Bearer'})
    response = r.get('https://www.googleapis.com/gmail/v1/users/' + \
                     '%s/profile?key=%s' % (current_user.email, 
                                            GOOGLE_CLIENT_SID))
    if response.status_code == requests.codes['OK']:
        add_or_replace_follower_count(Service.query.filter( \
            Service.name=='Google')[0],
            json.loads(response.content)['messagesTotal'])
        return redirect(url_for('main'))
    else:
        return redirect(url_for('authorize_apis'))


@app.route('/refresh/github/', methods=['GET'])
def refresh_github():
    # github_follower_count.apply_async(args=['makaimc'])
    github_follower_count('makaimc')
    return redirect(url_for('main'))


