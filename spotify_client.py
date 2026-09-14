import requests
import time

#used to return useful error messages rather than generic raise for status ones
class SpotifyAPIError(Exception):
    def __init__(self, status_code, message, reason=None):
        self.status_code = status_code
        self.message = message
        self.reason = reason
        super().__init__(f"Spotify API error {status_code}: {message}")


#every request calls this one function, which will be the one to make the request to spotify api
#handles retries for certain errors
#also makes it easier to handling errors and makes code cleaner
def make_request(method, url, max_retries=3, **kwargs):
    attempt = 0
    

    while True:
        try:
            response = requests.request(method, url, **kwargs)


        except requests.exceptions.RequestException as e:
            attempt+=1
            if attempt > max_retries:
                raise

            else:
                wait = min(2 ** attempt,30)
                time.sleep(wait)
                continue

        if response.status_code == 429:
            attempt +=1
            if attempt > max_retries:
                raise SpotifyAPIError(429, "Rate limited by Spotify")

            wait = int(response.headers.get("Retry-After", 2 ** attempt))
            time.sleep(wait)
            continue

        if 500 <= response.status_code < 600:
            attempt +=1
            if attempt > max_retries:
                message , reason = get_error_message(response)
                raise SpotifyAPIError(response.status_code, message, reason)

            wait = min(2**attempt, 30)
            time.sleep(wait)
            continue

        if response.status_code >= 400:
            message , reason = get_error_message(response)
            raise SpotifyAPIError(response.status_code, message, reason)
        
        return response


#takes in response
#returns message and reason
def get_error_message(res):
    try:
        body = res.json()

    except ValueError:
        return res.text or f"HTTP {res.status_code}", None
    if isinstance(body.get("error"), dict):

        err = body["error"]
        return err.get("message", res.text), err.get("reason")
 
    if "error_description" in body:
        return body["error_description"], body.get("error")
 
    return str(body), None