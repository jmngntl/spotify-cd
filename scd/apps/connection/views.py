import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from apps.connection.connect import SpotifyConnection

logger = logging.getLogger(__name__)

# Create your views here.
def callback(request):
    return render(request, '')


def authenticate(request):
    logger.debug("Starting auth process")
    session = SpotifyConnection()
    session_client = session.client
    oauth = session.auth_popup
    
    context = {
        'oauth_html': oauth
    }
    return render(request, 'connect.html', context)