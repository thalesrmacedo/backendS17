import os
import json
from flask import Flask, redirect, request, session, url_for, render_template
from requests_oauthlib import OAuth2Session

# Permitir transporte inseguro para desenvolvimento local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

with open('client_secret.json') as f:
    creds = json.load(f)['web']

CLIENT_ID = creds['client_id']
CLIENT_SECRET = creds['client_secret']
REDIRECT_URI = creds['redirect_uris'][0]
AUTH_URI = creds['auth_uri']
TOKEN_URI = creds['token_uri']
SCOPE = ['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

app = Flask(__name__, template_folder='templates')
app.secret_key = os.urandom(24)

@app.route('/')
def home():
    if 'profile' in session:
        profile = session['profile']
        return render_template('home.html', profile=profile)
    return '<a href="/login">Login com Google</a>'

@app.route('/login')
def login():
    google = OAuth2Session(CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
    authorization_url, state = google.authorization_url(AUTH_URI, access_type="offline", prompt="select_account")
    session['oauth_state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    google = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, state=session['oauth_state'])
    token = google.fetch_token(TOKEN_URI, client_secret=CLIENT_SECRET, authorization_response=request.url)
    session['oauth_token'] = token
    userinfo = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
    session['profile'] = userinfo
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
