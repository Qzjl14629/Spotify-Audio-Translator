import json
import time
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
import os
# from dotenv import load_dotenv

from callback import login_url, CallbackHandler, authResponse, code_for_token
from spotify_client import make_request
from config import CLIENT_ID, REDIRECT_URI

cache_file = "tokens.json"

#searches for the cache file to retreive access and refresh token
def load_tokens():
    try: 
        with open(cache_file, "r")  as file:
            return json.load(file)
    except FileNotFoundError:
        return None


def is_expried(tokendata):
    expiry_time = tokendata["access_obtained_on"] + tokendata["expires_in"]
    return time.time() > expiry_time


#tries to get the access token
#if no valid access token, first checks for a refresh token
#if the refresh token is invalid or doesnt exist, get the tokens through a callback
def get_access_token():
    tokens = load_tokens()

    #first, check if the access token has expired
    if tokens and not (is_expried(tokens)):
        return tokens["access_token"]

    #check if a refresh token exists and is valid
    #refresh lasts 6 months at most
    #needs to be in a try block in case refresh has expired
    elif tokens and ("refresh_token" in tokens):
        try:
            data = refresh(tokens["refresh_token"])
            store_tokens(data)
            return data["access_token"]
        except requests.HTTPError:
            pass

    #else, login in through spotify to retreive new access and refresh tokens
    
    verifier, state, url = login_url()
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    webbrowser.open(url)
    server.timeout = 30 #in seconds
    server.handle_request()

    if authResponse.get('code') is None:
        raise TimeoutError("No reponse from spotify login")

    if state != authResponse["state"]:
        raise Exception("State mismatch")

    #with code from spotify, exchange for tokens from spotify
    res = code_for_token(authResponse["code"], verifier)
    store_tokens(res)
    return res["access_token"]



#obtains a new access token using the refresh token
def refresh(refresh_token):
    url = "https://accounts.spotify.com/api/token"
    # response = requests.post(
    #     url,
    #     data = {
    #         "grant_type": "refresh_token",
    #         "refresh_token": refresh_token,
    #         "client_id": CLIENT_ID
    #     }
    #     )
    # response.raise_for_status()
    response = make_request(
        "POST",
        url,
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID
        }
    )
    data = response.json()
    if "refresh_token" not in data: #refresh_token are only sometimes part of the response
        data["refresh_token"] = refresh_token #will pass in data to overwrite the current json file
    return data


#store tokens, along with time of when they were stored (just useful for access)
def store_tokens(tokendata):
    tokendata["access_obtained_on"] = time.time()
    with open(cache_file, "w") as f:
        json.dump(tokendata, f)

