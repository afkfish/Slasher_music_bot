from urllib.parse import urlencode

import requests
import base64
import json


class SpotifyApi:
    url = 'https://accounts.spotify.com/api/token'
    headers = {}
    data = {}
    with open("secrets.json", "r") as f:
        client = json.load(f)
    client_id = client["spotify"]["client_id"]
    client_secret = client["spotify"]["client_secret"]
    message = base64.b64encode(f"{client_id}:{client_secret}".encode())
    headers['Authorization'] = f"Basic {message.decode()}"
    data['grant_type'] = "client_credentials"

    def get_by_id(self, trackid):
        r = requests.post(self.url, headers=self.headers, data=self.data)
        token = r.json()['access_token']

        trackurl = f"https://api.spotify.com/v1/tracks/{trackid}"
        headers = {
            "Authorization": "Bearer " + token
        }

        res = requests.get(url=trackurl, headers=headers)
        return res.json()

    def get_by_name(self, q, type, limit):
        r = requests.post(self.url, headers=self.headers, data=self.data)
        token = r.json()['access_token']

        link = {
            "q": q,
            "type": type,
            "limit": limit
        }
        headers = {
            "Authorization": "Bearer " + token
        }

        res = requests.get(url="https://api.spotify.com/v1/search?" + urlencode(link), headers=headers)
        return res.json()
