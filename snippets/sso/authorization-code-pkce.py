import base64
import random
import requests
import secrets
import string
import urllib
import hashlib

client_id = "your_client_id"
# Note: we do not use the client secret in this flow


def generate_code_challenge():
    """
    Generates a code challenge for PKCE.

    :returns: A tuple containing the code verifier and code challenge
    """
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32))
    sha256 = hashlib.sha256()
    sha256.update(code_verifier)
    code_challenge = base64.urlsafe_b64encode(sha256.digest()).decode().rstrip("=")
    return (code_verifier, code_challenge)


def request_token(authorization_code, code_verifier):
    """
    Takes an authorization code and code verifier and exchanges it for an access token and refresh token.

    :param str authorization_code: The authorization code received from the SSO
    :param str code_verifier: The code verifier used to generate the code challenge, as generated by `generate_code_challenge`
    :returns: A dictionary containing the access token and refresh token
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "client_id": client_id,
        "code_verifier": code_verifier,
    }
    response = requests.post(
        "https://login.eveonline.com/v2/oauth/token", headers=headers, data=payload
    )
    response.raise_for_status()

    return response.json()


def redirect_to_sso(scopes, redirect_uri, challenge):
    """
    Generates a URL to redirect the user to the SSO for authentication.

    :param list[str] scopes: A list of scopes that the application is requesting access to
    :param str redirect_uri: The URL where the user will be redirected back to after the authorization flow is complete
    :param str challenge: A challenge as generated by `generate_code_challenge`
    :returns: A tuple containing the URL and the state parameter that was used
    """
    state = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    query_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(scopes),
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    query_string = urllib.parse.urlencode(query_params)
    return (f"https://login.eveonline.com/v2/oauth/authorize?{query_string}", state)
