import requests
from requests_oauthlib import OAuth2Session
from requests.auth import HTTPBasicAuth

import json
import os

class SpotifyApi():

    def user_profile(self, oauth_session):
        """
        Get and return the user profile based on an already created oauth session
        """
        user_endpoint = "https://api.spotify.com/v1/me"
        user = oauth_session.get(user_endpoint)
        return user

    def user_playlists(self, oauth_session, user_id, limit):
        """
        Get and return the users playlists based on an already created oauth session, and the user ID 
        parsed from the response given in user_profile()
        """
        playlists_endpoint
        if limit <= 0:
            playlists_endpoint = "https://api.spotify.com/v1/users/{user_id}/playlists"
        else:
            playlists_endpoint = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit={limit}"
        playlists = oauth_session.get(playlists_endpoint)
        return playlists