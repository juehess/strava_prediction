#!/usr/bin/env python

from stravalib import Client
import webbrowser
import requests
class Predictor:

    client_id_=8127
    def __init__(self):
        self.data_ = []
        self.strava_client_=Client()
        self.url_ = self.strava_client_.authorization_url(client_id=self.client_id_,
                               redirect_uri='http://127.0.0.1:5000/authorization',scope='write',)
        #webbrowser.open_new_tab(self.url_)
        r = requests.get(self.url_)
if __name__ == "__main__":
    pred=Predictor()


