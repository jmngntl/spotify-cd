import collections
import logging
import secrets
import httpx
import webbrowser

from datetime import datetime, timedelta
from django.conf import settings
from authlib.integrations.httpx_client import OAuth2Client
from requests.auth import HTTPBasicAuth

# configure logging for this module
logger = logging.getLogger('apiLogger')

class SpotifyConnection():
    def __init__(self):
        self.auth_url = 'https://accounts.spotify.com/authorize'
        self.token_url = 'https://accounts.spotify.com/api/token'
        self.redirect_uri = 'https://127.0.0.1:3000/callback'
        self.refresh_token_url = ''
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
        self.auth_popup = self.login()
        self.client = None

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
        # TODO: supress stdout when calling property
        if self._token is None:
            self._token = self.token_attrs.access_token
        return self._token

    def get_token_attrs(self, token_data):
        """
        Convert token data dict to namedtuple for dot notation access
        """
        return collections.namedtuple('TokenAttributes', token_data.keys())(**token_data)

    def initialize_client(self):
        """
        Set up OAuth2 clients with required Spotify API authentication parameters.
        """
        spotify_client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            token_placement='header'
        )
        return spotify_client
    
    # def set_oauth2_client(self):
    #     spotify_client = OAuth2Client(
    #         client_id=self.client_id,
    #         client_secret=self.client_secret,
    #         redirect_uri=self.redirect_uri,
    #         scope=self.scope,
    #         token=self.token
    #     )
    #     return spotify_client

    def login(self):
        """
        Authorize access to user spotify data using OAuth2.
        """
        spotify_client = self.initialize_client()
        self.client = spotify_client
        try:
            # Authorize access to user data
            auth_resp, auth_state = spotify_client.create_authorization_url(
                url=self.auth_url,
                code_verifier=self.code_verifier  # use PKCE
            )

            redirect_request = httpx.Request('GET', auth_resp)
            redirect_resp = spotify_client.send(redirect_request)
            if redirect_resp.status_code == 303:
                redirect_location = redirect_resp.headers['location']
                redirect_req = httpx.Request('GET', redirect_location, headers={'Content-Type': 'application/json'})
                oauth2_resp = spotify_client.send(redirect_req)
                if oauth2_resp.status_code == httpx.codes.OK:
                    oauth2_popup = oauth2_resp.text
                    return oauth2_popup
            else:
                raise Exception(f'Error during OAuth2 authorization: {redirect_resp.status_code} - {redirect_resp.text}')
            # print(user_auth_url)
            # auth_resp = input(f'Paste the redirect uri after authorizationg here: {user_auth_url}')
            # TODO: connect to frontend here from user_auth_url, send response attrs back to fetch token
            # Fetch the access token
            # token_data = spotify_client.fetch_token(
            #     url=self.token_url,
            #     auth=self.auth_info,
            #     authorization_response=user_auth_url,  # update auth resp here after frontend connection
            #     state=auth_state,
            #     # grant_type='authorization_code'
            # )
            # current_time = datetime.now()
            # expiration_time = current_time + timedelta(seconds=token_data.get('expires_in'))
            # if current_time < expiration_time:
            #     token_data['is_expired'] = False
            # if token_data:
                # logger.info(f'Token data fetched successfully: {token_data}')
            # self.token_attrs = self.get_token_attrs(token_data)
            # spotify_client.token = self.token_attrs.access_token
        #     return spotify_client
        except Exception as e:
            logger.error(f'Error during login: {e}')
            raise e
        
    def get(self, url: str, **kwargs):
        self.headers.update({'Authorization': f'Bearer {self.token}'})
        logger.debug(f'GET - {url}')
        try:
            request = httpx.Request('GET', url, **kwargs, headers=self.headers)
            response = self.client.send(request)
            if response.status_code == httpx.codes.OK:
                return response.json()
            else:
                logger.error(f'Error fetching data from {url}: {response.status_code} - {response.text}')
                return response
        except httpx.HTTPError as e:
            logger.error(f'Invalid HTTP response: {e}')
            raise e
    
    # def refresh_token(self):
