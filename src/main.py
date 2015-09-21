from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
import os
import stravalib
import numpy as np

#for plotting
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import random
import StringIO
from flask import Flask, make_response

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
        self.data_retrieved=False

        self.athlete_ = self.client_.get_athlete()
        print("For {id}, I now have an access token {token}".format(id=self.athlete_.id, token=self.access_token_))

        # Activities can have many streams, you can request n desired stream types
        types = ['time', 'distance', 'velocity_smooth', 'grade_smooth', 'cadence', 'heartrate' ]
        types = ['time', 'distance', 'velocity_smooth', 'grade_smooth']
        activities=self.client_.get_activities(limit=2)
        #activities=self.client_.get_activities()

        n_act=len(list(activities))
        print "Found " + str(n_act) + " activities."
        i=0
        for act in list(activities):
            i=i+1
            print "Retrieving activity " + str(i) + " of "  + str(n_act)
            streams = self.client_.get_activity_streams(act.id, types=types, resolution='low')
            # #  Result is a dictionary object.  The dict's key are the stream type.
            if 'time' in streams.keys():
                self.time.extend(streams['time'].data)
            if 'distance' in streams.keys():
                self.distance.extend(streams['distance'].data)
            if 'velocity_smooth' in streams.keys():
                self.velocity.extend(streams['velocity_smooth'].data)
            if 'grade_smooth' in streams.keys():
                self.grade.extend(streams['grade_smooth'].data)

        print "Saving data to numpy array"
        #check if data has the same lenght
        if (len(self.time) ==  len(self.distance) == len(self.velocity) == len(self.grade)):
            self.data=np.column_stack((self.time,self.distance,self.velocity,self.grade))
            print "The final data size is " + str(self.data.shape)
            print "Saving to data to file."
            np.savetxt("strava.txt", self.data, delimiter=" ")
            self.data_retrieved=True
            print "Done"
        else:
            print "data length differs for different streams"
            print "length time " + str(len(self.time))
            print "length distance " + str(len(self.distance))
            print "length velocity " + str(len(self.velocity))
            print "length grade " + str(len(self.grade))
            self.data_retrieved=False
        return "done"

    def plotData(self):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot(self.grade, self.velocity,'bo')
        axis.set_ylabel('Velocity')
        axis.set_xlabel('Grade')
        axis.set_xlim([-20,20])
        canvas = FigureCanvas(fig)
        output = StringIO.StringIO()
        canvas.print_png(output)
        return output.getvalue()

exporter=StravaExporter()
app = Flask(__name__)

@app.route("/")
def authentification():
    return redirect(exporter.authorization_url_)

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
    return redirect(url_for('.plot'))

@app.route('/plot')
def plot():
    response = make_response(exporter.plotData())
    response.mimetype = 'image/png'
    return response

if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    os.environ['DEBUG'] = "1"

    app.secret_key = os.urandom(24)
    app.run(debug=True)