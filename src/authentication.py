import os
import urllib.parse
from typing import Dict, List, Optional
import sys

# Add path for helpers
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'helpers')))
from http_client import HTTPClient

def refresh_access_token(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    refresh_token: Optional[str] = None
) -> str:
    """
    Refreshes the OAuth 2.0 access token using a refresh token.
    Defaults to environment variables if not provided.
    """
    client_id = client_id or os.getenv("GTM_CLIENT_ID")
    client_secret = client_secret or os.getenv("GTM_CLIENT_SECRET")
    refresh_token = refresh_token or os.getenv("GTM_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing OAuth credentials. Provide them as arguments or set environment variables.")

    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    
    response = HTTPClient.post(url, data=payload)
    response.raise_for_status()
    
    token_data = response.json()
    return token_data.get("access_token")

def get_authorization_url(
    client_id: Optional[str] = None,
    redirect_uri: str = "http://localhost:8000",
    scopes: Optional[List[str]] = None
) -> str:
    """
    Generates the authorization URL for user consent.
    """
    client_id = client_id or os.getenv("GTM_CLIENT_ID")
    if not client_id:
        raise ValueError("Missing GTM_CLIENT_ID environment variable or argument.")

    if scopes is None:
        scopes = [
            "https://www.googleapis.com/auth/tagmanager.readonly",
            "https://www.googleapis.com/auth/tagmanager.edit.containers",
            "https://www.googleapis.com/auth/tagmanager.edit.containerversions",
            "https://www.googleapis.com/auth/tagmanager.delete.containers"
        ]

    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{base_url}?{query_string}"

def exchange_code_for_tokens(
    code: str,
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: str = "urn:ietf:wg:oauth:2.0:oob"
) -> Dict:
    """
    Exchanges the authorization code for access and refresh tokens.
    """
    client_id = client_id or os.getenv("GTM_CLIENT_ID")
    client_secret = client_secret or os.getenv("GTM_CLIENT_SECRET")

    if not all([client_id, client_secret]):
        raise ValueError("Missing OAuth credentials. Provide them as arguments or set environment variables.")

    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "code": code,
        "grant_type": "authorization_code",
    }
    
    response = HTTPClient.post(url, data=payload)
    response.raise_for_status()
    
    return response.json()
