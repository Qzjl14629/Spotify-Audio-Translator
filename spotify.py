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
    command = (command.strip().lower().rstrip(".")).replace(",","")
    print(f"command stripped:{command}")
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
        play_method, play_url = static_commands.get("play")
    
        type = "track" #default to track if user says "play {name}"
        after_play = command[len("play "):]
        search_by = after_play

        #and further differentiate by artist, album, track, and playlist (for this probably just do personal or just the liked songs), 
        # or instead just have these 4 be the keywords rather than play, if not, just assume track type
        for t in ("track ", "album ", "artist ", "playlist "):
            if after_play.startswith(t):
                type = t.strip()
                search_by = search_by[len(t):]
                break
        print(search_by)
        if (type == "artist" or type == "playlist"): #apparently having the scope in q as well for artist makes it less accurate
            data = {"market": "US", "type": type, "limit": 1, "offset": 0, "q": f"{search_by}"}
        else:
            data = {"market": "US", "type": type, "limit": 1, "offset": 0, "q": f"{type}:{search_by}"}
        
        search_url = f"https://api.spotify.com/v1/search"
        
        try:            
            res = make_request("GET", search_url, headers = auth, params = data) 

            items = res.json()[f"{type}s"]["items"]
            
            if items == [None] or items == []:
                print('not found')
                return
            get_search = items[0]["uri"]

            print(get_search)

            if type == 'track':
                play_param = {"uris": [get_search]}
            else:
                play_param = {"context_uri": get_search}
            # data["uris"] = [uri]

            #get search contains the uri for the song, so that can be used as the search param
            response = make_request(play_method, play_url,headers = auth,json = play_param)
            
        except SpotifyAPIError as s:
            print(f"Status Error {s.status_code}: {s.message}")


#bottom 2 need to be tested
    if (command == ("playlist like")): #liked songs
        play_method, play_url = static_commands.get("play")

        saved_url = "https://api.spotify.com/v1/me/tracks"

        try:
            res = make_request("GET", saved_url, headers = auth, params = {'limit': 50})
        except SpotifyAPIError as s:
            return

        data = res.json()

        uris = [item["track"]['uri'] for item in data['items']]

        try:
            make_request(play_method, play_url, headers = auth, json = {"uris": uris})
        except SpotifyAPIError as s:
            print(s)
            return

    #ok this one will juat be for playlists i own or follow ig
    if (command.startswith("playlist ")):
        playlist_name = command[len("playlist "):]

        url = "https://api.spotify.com/v1/me/playlists" #for playlists a user follows (owning automatically means following)
        my_playlists = []
        params = {'limit': 50}

        while url:
            try:
                res = make_request("GET", url, headers = auth, params = params)
            except SpotifyAPIError as s:
                print(s)
                break #possible that some playlists were alr retreived so break instead of return
            data = res.json()
            my_playlists.extend(data["items"])
            url = data.get("next")
            params = None

        playlisturi = None
        for p in my_playlists:
            if playlist_name == p["name"].lower().replace("-", ""):
                playlisturi = p['uri']

        if playlisturi is None:
            print("playlist not found")
            return

        play_method, play_url = static_commands.get("play")

        try:
            res = make_request(play_method, play_url, headers = auth, json = {'context_uri': playlisturi})
        except SpotifyAPIError as s:
            print(s)
            return

        
    



    