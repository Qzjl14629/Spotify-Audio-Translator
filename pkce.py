import hashlib, base64, secrets, json, time, webbrowser, requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, urlencode

def generate_pkce_pair():
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode("utf-8").rstrip("=")
    challenge = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(challenge).decode("utf-8").rstrip("=")
    return verifier, challenge