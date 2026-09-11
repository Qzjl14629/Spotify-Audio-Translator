from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
# from script import authResponse
import os
from dotenv import load_dotenv
import secrets
import webbrowser
from urllib.parse import urlencode
import requests

from pkce import generate_pkce_pair

from script import CLIENT_ID, REDIRECT_URI, SCOPES

authResponse = {}

#object to pass into the http server
class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("raw callback path", self.path)
        #breaks the callback path down into a dictionary
        splitPath = urlparse(self.path)
        getQuery = splitPath.query
        query = parse_qs(getQuery)

        authResponse["code"] = query.get("code", [None])[0]
        authResponse["state"] = query.get("state", [None])[0]

        #letting browser know request was successful
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write(b"Login successful. Close this tab.")

    def log_message(self, format, *args):
        pass




#redirects u to login to ur spotify account
def login_url():
    print("is success?")
    verifier, challenge = generate_pkce_pair()
    state = secrets.token_urlsafe(16)

    query = {
        "client_id": CLIENT_ID,
        "response_type": 'code',
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": SCOPES,
        #"show_dialog": False,
        "code_challenge_method": "S256",
        "code_challenge": challenge
    }
    url = "https://accounts.spotify.com/authorize?" + urlencode(query)
    # webbrowser.open(url)
    return verifier, state, url



def code_for_token(code, verifier):
    url= 'https://accounts.spotify.com/api/token'

    response = requests.post(
        url,
        data = {
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "grant_type": 'authorization_code',
            "client_id": CLIENT_ID,
            "code_verifier": verifier
        }
    )

    response.raise_for_status()
    return response.json()