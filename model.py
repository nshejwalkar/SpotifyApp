import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import os

load_dotenv()

bigdf = pd.read_csv('./data/final100.csv')
bigdf.drop(columns=['Unnamed: 0'], inplace=True)

cid = os.getenv('client_ID')
secret = os.getenv('client_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


def retrieve_uris(playlist_link):
   if playlist_link is None: return None

   playlist_URI = playlist_link.split('/')[-1].split('?')[0] # extracts the URI from the link
   
   track_uris = []
   try: 
      for track in sp.playlist_tracks(playlist_URI)['items']:
         track_uris.append(track['track']['uri'].split(':')[-1])
   except spotipy.exceptions.SpotifyException:
      return None

   return track_uris


def checkifany(songs):
   if songs is None: return 1

   bool_mask = bigdf['id'].isin(songs) # returns boolean mask
   if bool_mask.any() == False: return 2
   return 3

def generate_playlist_vector(playlist_uris, spotify_feature_df=bigdf):
   feature_set_playlist = spotify_feature_df[spotify_feature_df['id'].isin(playlist_uris)]
   feature_set_notplaylist = spotify_feature_df[~spotify_feature_df['id'].isin(playlist_uris)]
   final_feature_set_playlist = feature_set_playlist.drop(columns='id')

   return final_feature_set_playlist, feature_set_notplaylist # two dfs

def generate_recommendations(playlist_vector, notplay_df, number):
   temp = notplay_df.copy()

   X = notplay_df.drop(columns='id').values
   Y = playlist_vector.values#.reshape(1,-1)
   print(X.shape, Y.shape)
   
   temp['similarity'] = cosine_similarity(X, Y)[:,0]
   finalrecs = temp.sort_values('similarity', ascending=False).head(number)

   return finalrecs # is a df

def return_links(reco_uris):
   links = []
   for num, uri in enumerate(reco_uris):
      output = ''      
      arts = [artist['name'] for artist in sp.track(uri)['artists']]

      output+=f'{num+1}. '
      for art in arts:
         output+=f'{art}, '
      output = output[:-2] + ' - '
      output+=sp.track(uri)['name']

      uri = 'https://open.spotify.com/track/' + uri

      links.append((output, uri))

   return links

def do_everything(songuris, number):
   play, notplay = generate_playlist_vector(songuris)
   recouris = generate_recommendations(play, notplay, number)['id']
   final = return_links(recouris)

   return final
