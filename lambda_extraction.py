import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import boto3
from datetime import datetime

def lambda_handler(event, context):
    client_id = os.environ.get('client_id')
    client_secret = os.environ.get('client_secret')
    
    # Setting up the credentials for authentication
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

    # To interact with the spotify API
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    
    # This is the link to get top 50 global spotify songs
    spotify_playlist = 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF'

    # We want to get the endpoint of the link
    playlist_URI = spotify_playlist.split("/")[4]
    
    data = sp.playlist_tracks(playlist_URI)
    
    client = boto3.client('s3')
    
    filename = "spotify_raw_" + str(datetime.now()) + ".json"
    
    client.put_object(
        Bucket="spotify-etl-project-iman",
        Key="bronze_layer/to_processed/" + filename,
        Body=json.dumps(data)
    )

    glue = boto3.client("glue")
    gluejobname = "spotify_transformation_job"

    try:
        runId = glue.start_job_run(JobName = gluejobname)
        status = glue.get_job_run(JobName = gluejobname, RunId = runId['JobRunId'])
        print("Job Status: ", status['JobRun']['JobRunState'])
    except Exception as e:
        print(e)
