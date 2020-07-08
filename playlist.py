import requests
import webbrowser
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

results = []
count = 0

# The urls for the joyturk last played songs
URLs = ["https://onlineradiobox.com/tr/joyturk/playlist/?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/1?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/2?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/3?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/4?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/5?cs=tr.joyturk",
        "https://onlineradiobox.com/tr/joyturk/playlist/6?cs=tr.joyturk"]

for URL in URLs:
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')
    soup = soup.find('section', class_='playlist')
    soup = soup.find('table', class_='tablelist-schedule')
    songs = []

    # Get paths of all the songs
    for el in soup.find_all('a', attrs={'class': 'ajax', 'href': True}):
        songs.append(el['href'])

    for path in songs:
    	# Get the youtube video ids of the songs
        URL = "https://onlineradiobox.com" + path
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        elem = soup.find('iframe', src=True)

        if elem != None and elem != [None] and elem['src'] != None:
            link = elem['src']
            videoId = link.split('embed/')[1]

            # Check uniqueness
            if videoId not in results:
                results.append(videoId)

                # Request to add the song to a playlist
                request = youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                        "playlistId": "PLLp9ibSJS0B8C-MbpHXjrjc7s6rlyZFEe",
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": videoId
                        }
                        }
                    }
                )
                count += 1
                
                # Send request
                try:
                    response = request.execute()
                    print(str(count) + ' - ' + videoId)
                except Exception as e:     
                    print('Hata:' + str(e) + " - " + str(count) + ' - ' + videoId)
