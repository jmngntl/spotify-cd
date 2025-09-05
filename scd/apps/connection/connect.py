import collections
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
        self.redirect_uri = 'http://127.0.0.1:3000/callback'
        self.client_id = settings.CLIENT_ID
        self.client_secret = settings.CLIENT_SECRET
        self.scope = [
            "user-read-email",
            "playlist-read-collaborative"
        ]
        self._token = None
        self.token_attrs = None
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.auth_info = HTTPBasicAuth(self.client_id, self.client_secret)
        self.code_verifier = self.generate_code_verifier()
        self.login()

        self.user_token = None

    @staticmethod
    def generate_code_verifier():
        """Generate a secure code verifier for PKCE."""
        return secrets.token_urlsafe(64)

    @property
    def token(self):
        """
        Property to dynamically fetch token upon class initialization. Retrieve token by calling <class_inst>.token.
        """
        # TODO: in view where API is called and token is used use whlie condition to check if token has expired -- while response.status_code == httpx.codes.OK .. look into .elapsed attr from httpx docs could set OR condition in while to check if .elapsed < token keep alive time, if not refersh token
        # TODO: look into Spotify API docs for expires_at in access token response.. is this in UTC? 
        if self._token is None:
            self._token = self.token_attrs.access_token
        return self._token

    def get_token_attrs(self, token_data):
        """
        Convert token data dict to namedtuple for dot notation access
        """
        return collections.namedtuple('TokenAttributes', token_data.keys())(**token_data)

    def set_ouath2_client(self):
        """
        Set up OAuth2 clients with required Spotify API authentication parameters.
        """
        spotify_client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
        )
        return spotify_client

    def login(self):
        """
        Authorize access to user spotify data using OAuth2.
        """
        spotify_client = self.set_ouath2_client()
        print(f"Auth CLient: {spotify_client}")
        try:
            # Authorize access to user data
            auth_resp, auth_state = spotify_client.create_authorization_url(
                url=self.auth_url,
                code_verifier=self.code_verifier  # use PKCE
            )
            logger.info(f'Authorization URL: {auth_resp}')
            logger.info('Please complete the authorization in your browser.')
            print(f'Authorization URL: {auth_resp}')

            # Fetch the access token
            token_data = spotify_client.fetch_token(
                url=self.token_url,
                auth=self.auth_info,
                headers=self.headers
            )
            logger.info(f'Token data fetched successfully: {token_data}')
            self.token_attrs = self.get_token_attrs(token_data)
            return self.token_attrs
        except Exception as e:
            logger.error(f'Error during login: {e}')
            raise e

    async def user_login(self):
        """
        The login above only works for api endpoints that do not need any user data. See the following:
        https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow
        This function makes the user login and provide a code
        """

        """
        Need a way to get the code autoamtically, sorta back to where we were before we started on the Django app.
        But once the frontend is ready, we might be able to have it call functions here, and eventually this function, to get the token
        """

        try:
            spotify_client = OAuth2Client(
                response_type="code",
                client_id=self.client_id,
                redirect_uri=self.redirect_uri,
                scope=self.scope,
            )
            # Authorize access to user data
            auth_resp, auth_state = spotify_client.create_authorization_url(
                url=self.auth_url,
                code_verifier=self.code_verifier  # use PKCE
            )
            print(f"Auth response: {auth_resp}")
            user_auth_token = await input(f"Please go to {auth_resp}, login, then enter the code here:\n")
            print(f"User entered: {user_auth_token}")
            return user_auth_token
        except Exception as e:
            logger.error(f'Error during login: {e}')
            raise e