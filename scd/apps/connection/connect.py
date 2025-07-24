import logging
import secrets

from django.conf import settings
from authlib.integrations.httpx_client import OAuth2Client
from requests.auth import HTTPBasicAuth

# configure logging for this module
logger = logging.getLogger(__name__)

class SpotifyConnection():
    def __init__(self):
        self.auth_url = 'https://accounts.spotify.com/authorize'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.redirect_uri = 'https://127.0.0.1:3000/callback'
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.pkce_token = settings.PCKE_TOKEN
        self.scope = [
            "user-read-email",
            "playlist-read-collaborative"
        ]
        self.token = self.login()
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.auth_info = HTTPBasicAuth(self.client_id, self.client_secret)
        self.code_verifier = self.generate_code_verifier()


    @staticmethod
    def generate_code_verifier():
        """Generate a secure code verifier for PKCE."""
        return secrets.token_urlsafe(64)


    @property
    def login(self):
        access_token = None

        spotify_client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )

        # authorize access to user data
        auth_resp, auth_state = spotify_client.create_authorization_url(
            url=self.auth_url,
            code_verifier=self.code_verifier # use PKCE
        )

        # generate access token
        access_token = spotify_client.fetch_token(
            url=self.token_url,
            auth=self.auth_info,
            headers=self.headers
        )
        # TODO: how to securely store access token so it is not available to external users?
        # TODO: create github workflow that updates readme with 3rd party libraries (repos/official websites) used in project
        if access_token:
            self.token = access_token
            logger.debug("Successfully logged in to Spotify.")
        return self.token # token obj, actual token stored in access_token['access_token'] or self.token['access_token']