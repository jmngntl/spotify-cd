import requests
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

import json
import os

class playlists():

    def __init__(self):
        self.AUTH_URL = 'https://accounts.spotify.com/authorize'
        self.TOKEN_URL = 'https://accounts.spotify.com/api/token'
        self.REDIRECT_URI = 'https://127.0.0.1:3000/callback'
        self.CLIENT_ID = os.environ.get('CLIENT_ID')
        self.CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
        self.SCOPE = [
            "user-read-email",
            "playlist-read-collaborative"
        ]
        self.TOKEN = None
        self.HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.AUTH_INFO = HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET)
        self.session = self.login()
        self.PLAYLISTS = self.get_playlists(self.session)
        self.TRACK_LIST = self.get_tracks(self.session, self.PLAYLISTS[0][2]) #self.PLAYLISTS is a 2d array, modify first value to correspond to playlist

    def login(self):
        spotify = OAuth2Session(self.CLIENT_ID, scope = self.SCOPE, redirect_uri = self.REDIRECT_URI)
        authorization_url, state = spotify.authorization_url(self.AUTH_URL)
        print(authorization_url)
        code = input()
        self.TOKEN = spotify.fetch_token(self.TOKEN_URL, auth = self.AUTH_INFO, authorization_response = code, state = state)
        return spotify

    def get_playlists(self, spotify):
        count = 0
        return_data = {}
        user = spotify.get('https://api.spotify.com/v1/me')
        user_json = json.loads(user.content)
        USER_ID = user_json['id']
        playlists = spotify.get(f'https://api.spotify.com/v1/users/{USER_ID}/playlists')
        parsed = json.loads(playlists.content)
        for i in parsed.get('items'):
            if i.get('external_urls') and i['owner']['id'] == USER_ID:
                return_data[count] = (i['name'], i['id'], i['tracks']['href'])
                count+=1

        return return_data

    def get_tracks(self, spotify, playlist):
        return_data = []
        first_track_list = spotify.get(playlist)
        tracks_json = json.loads(first_track_list.content)
        for i in tracks_json.get('items'):
            if i.get('track'):
                artists = i['track']['artists']
                artists_names = [a['name'] for a in artists]
                names = ", ".join(artists_names)
                track_name = i['track']['name']
                return_data.append(f"{track_name} by {names}")

        return return_data
