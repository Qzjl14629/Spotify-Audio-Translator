import os
import requests
from spotify_client import make_request, SpotifyAPIError

#all the commands that wont have states changed, can just use if statements for the ones that require states
static_commands = {
    "play": ("PUT", "https://api.spotify.com/v1/me/player/play"),
    "pause": ("PUT", "https://api.spotify.com/v1/me/player/pause"),
    "repeat song": ("PUT", "https://api.spotify.com/v1/me/player/repeat?state=track"),
    "repeat playlist": ("PUT", "https://api.spotify.com/v1/me/player/repeat?state=context"),
    "repeat off": ("PUT", "https://api.spotify.com/v1/me/player/repeat?state=off"),
    "skip": ("POST", "https://api.spotify.com/v1/me/player/next"),
    "previous": ("POST", "https://api.spotify.com/v1/me/player/previous"),
    "shuffle on": ("PUT", "https://api.spotify.com/v1/me/player/shuffle?state=true"),
    "shuffle off": ("PUT", "https://api.spotify.com/v1/me/player/shuffle?state=false"),

    

}
'''
other commands:
play {song}
play {song} by {artist}
play {album}
like (adds to just liked song, not gonna deal with playlists)
library (plays liked songs, easier to say)

'''

def spotify_command(command, access_token):
    auth = {"Authorization": f"Bearer {access_token}"}
    message = ""
    command = command = command.strip().lower().rstrip(".")

    if command == "":
        return "Nothing picked up"

    if (command in static_commands):
        method, url = static_commands.get(command)
        try:
            response = make_request(method, url, headers = auth)
            return (f"{command} command succeeded")
        except SpotifyAPIError as s:
            print(f"Status Error {s.status_code}: {s.message}")
            return

    if (command == "like"):
        #get current song
        try:
            response = make_request(
                "GET", "https://api.spotify.com/v1/me/player/currently-playing",
                headers = auth,
            )
        except SpotifyAPIError as s:
            print(s)
            return


        if response.status_code == 204 or not response.content:
            print("nothing playing")
            return

        data = response.json()
        item = data.get("item")
        if item is None:
            return
        current_song = item["uri"]

        #add song to liked songs
        try:
            like_song_res = make_request(
                "PUT", "https://api.spotify.com/v1/me/library",
                headers = auth,
                params = {"uris": current_song}
            )
        except SpotifyAPIError as s:
            print(s)
            return
        
        print("added to liked songs")


#ok this shit buggy as fuck lmao
    if (command.startswith("play ")):
        print("in play ## by @@")
        #and further differentiate by artist, album, track, and playlist (for this probably just do personal or just the liked songs), or instead just have these 4 be the keywords rather than play 
        method, play_url = static_commands.get("play")
        type = "track"
        search_by = command[len("play "):]
        search_url = f"https://api.spotify.com/v1/search?q={search_by}&type={type}&limit=1&offset=0&include_external=audio"
        data = {}

        try:
            #buggy with slightly unknown songs, do something later about {song} by {artist} later
            res = make_request("GET", search_url, headers = auth) #search first for the uri (contexturi is for albums, albums, playlists), which will then be passed into play
            get_search = res.json()[f"{type}s"]["items"][0]["uri"]
            print(get_search)
            # data["uris"] = [uri]

            #get search contains the uri for the song, so that can be used as the search param

            
        except SpotifyAPIError as s:
            print(f"Status Error {s.status_code}: {s.message}")


    




    #playlist-modify-private
    #want one for add to queue too, plus one to add to liked songs
    if (command.startswith("add ")):
        next
    if (command.startswith("like")):
        next
        

    