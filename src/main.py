#!/usr/bin/env python

from stravalib import Client

class Predictor:

    client_id_="juergenmhess@gmail.com"
    def __init__(self):
        self.data_ = []
        self.strava_client_=Client()
        self.url_ = self.strava_client_.authorization_url(client_id=self.client_id_,
                               redirect_uri='http://127.0.0.1:5000/authorization')

if __name__ == "__main__":
    pred=Predictor()

