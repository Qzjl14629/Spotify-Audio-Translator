import os
import requests
from script import CLIENT_ID, REDIRECT_URI



def spotify_command(command, access_token):
    auth = {"Authorization": f"Bearer {access_token}"}
    response
    command = command.lower()
    if (command == " play."): #there are more states to this
        print("in play")
        response = requests.put(
            "https://api.spotify.com/v1/me/player/play",
            headers = auth
        )
        # print(response.text)
    elif (command == "pause"):
        response = requests.put(
            "https://api.spotify.com/v1/me/player/pause",
            headers = auth
        )
    elif (command == "repeat song"):
        response = requests.put(
            'https://api.spotify.com/v1/me/player/repeat?state=track',
            headers = auth
        )
    elif (command == "repeat playlist"):
        response = requests.put(
            'https://api.spotify.com/v1/me/player/repeat?state=context',
            headers = auth
        )
    elif (command == "repeat off"):
        response = requests.put(
            'https://api.spotify.com/v1/me/player/repeat?state=off',
            headers=auth
        )
    elif (command == "skip"):
        response = requests.post(
            "https://api.spotify.com/v1/me/player/next",
            header = auth
        )
    elif (command == "previous"):
        response = requests.post(
            "https://api.spotify.com/v1/me/player/previous",
            header = auth
        )
    elif (command == "shuffle on"):
        response = requests.put(
            'https://api.spotify.com/v1/me/player/shuffle?state=true',
            header = auth
        )
    elif (command == "shuffle off"):
        response = requests.put(
            'https://api.spotify.com/v1/me/player/shuffle?state=false',
            header=auth
        )


    #playlist-modify-private
    elif (command == ""):
        next
        

    print(response)