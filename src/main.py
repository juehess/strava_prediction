from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import stravalib


class StravaExporter:



    def __init__(self):
        self.client_=stravalib.Client()
        self.authorization_base_url = 'https://www.strava.com/oauth/authorize'
        self.client_id_=8127
        self.client_secret_='3d869b3147715c66710c6028d06cb91976b6e103'
        self.redirect_uri_='http://127.0.0.1:5000/authorization'
        self.authorization_url_ = self.client_.authorization_url(client_id=self.client_id_,
                               redirect_uri=self.redirect_uri_,scope='write',approval_prompt='auto')

    def getToken(self, code):
        self.access_token_ = self.client_.exchange_code_for_token(client_id=self.client_id_, client_secret=self.client_secret_, code=code)
        return self.access_token_

    def retrieveData(self):
        self.time=[]
        self.distance=[]
        self.velocity=[]
        self.grade=[]

        self.athlete_ = self.client_.get_athlete()
        print("For {id}, I now have an access token {token}".format(id=self.athlete_.id, token=self.access_token_))

        # Activities can have many streams, you can request n desired stream types
        types = ['time', 'distance', 'velocity_smooth', 'grade_smooth', 'cadence', 'heartrate' ]
        types = ['time', 'distance', 'velocity_smooth', 'grade_smooth']
        activities=self.client_.get_activities(limit=2)

        for act in list(activities):
            streams = self.client_.get_activity_streams(act.id, types=types, resolution='low')
            print act.id
            # #  Result is a dictionary object.  The dict's key are the stream type.
            if 'time' in streams.keys():
                self.time.extend(streams['time'].data)
            if 'distance' in streams.keys():
                self.distance.append(streams['distance'].data)
            if 'velocity_smooth' in streams.keys():
                self.velocity.append(streams['velocity_smooth'].data)
            if 'grade_smooth' in streams.keys():
                self.grade.append(streams['grade_smooth'].data)
            print self.time
            print streams['time'].data
            # print len(self.distance)
            # print len(self.velocity)
            # print len(self.grade)
        return "done"

exporter=StravaExporter()
app = Flask(__name__)

@app.route("/")
def authentification():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. Github)
    using an URL with a few key OAuth parameters.
    """
    # strava = OAuth2Session(client_id_, redirect_uri=redirect_uri_)
    # authorization_url, state = strava.authorization_url(authorization_base_url)
    # print 'Please go here and authorize,'
    # print authorization_url
    # print authorization_url_
    # print state
    #
    # # State is used to prevent CSRF, keep this for later.
    # session['oauth_state'] = state
    return redirect(exporter.authorization_url_)


# Step 2: User authorization, this happens on the provider.

@app.route("/authorization", methods=["GET"])
def callback():

    # Extract the code from your webapp response
    code = request.args.get('code')
    access_token = exporter.getToken(code)
    session['oauth_token'] = access_token
    return redirect(url_for('.profile'))


@app.route("/profile", methods=["GET"])
def profile():
    """Fetching a protected resource using an OAuth 2 token.
    """
    exporter.retrieveData()
    return "done"

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)