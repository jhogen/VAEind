#!/usr/bin/env python
# coding: utf-8

# In[88]:


import plotly.graph_objects as pgo
import plotly.express as px
import streamlit as st
import pandas as pd
import numpy as np
import spotipy
import folium
from streamlit_folium import folium_static
import plotly.graph_objects as go
sp = spotipy.Spotify()
import seaborn as sns
import matplotlib.pyplot as plt

from spotipy.oauth2 import SpotifyClientCredentials 

import json
from pandas.io.json import json_normalize
import pandas as pd


# In[36]:


#De titel van de streamlit pagina's
st.set_page_config(page_title="VA-Eindopdracht", page_icon="♫", layout = "wide", initial_sidebar_state="expanded")


# In[ ]:


#Titel van elke pagina aanmaken.
st.title('Visual Analytics - Spotify Dashboard')


# In[ ]:


#Het toevoegen van een sidebar.
st.sidebar.title('Navigatie')


# In[2]:


#Authenticatiie van de API zonder gebruiker.
client_credentials_manager = SpotifyClientCredentials(client_id='ee5d014280cf4dad8350e8a0b35608b0', client_secret="f3556b9ac996464a84e686586c3e9642")
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)


# In[3]:


#De playlist die opgehaald wordt, de URI van de playlist en de URI van de nummers.
playlist_link = "https://open.spotify.com/playlist/5PUG3hOhmfA5QNkqVMxbiC"
playlist_URI = playlist_link.split("/")[-1].split("?")[0]
track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_URI)["items"]]


# In[4]:


#Het weergeven van de data en de kolommen, alle variabelen aanmaken 
data = {'track_uri': [],
        'track_name': [],
        'artist_uri': [],
        'artist_info': [],
        'artist_name': [],
        'artist_pop': [],
        'artist_genres': [],
        'album': [],
        'track_pop': [],
       }
for track in sp.playlist_tracks(playlist_URI)["items"]:
    #URI
    track_uri = track["track"]["uri"]
    
    #Track name
    track_name = track["track"]["name"]
    
    #Main Artist
    artist_uri = track["track"]["artists"][0]["uri"]
    artist_info = sp.artist(artist_uri)
    
    #Name, popularity, genre
    artist_name = track["track"]["artists"][0]["name"]
    artist_pop = artist_info["popularity"]
    artist_genres = artist_info["genres"]
    
    #Album
    album = track["track"]["album"]["name"]
    
    #Popularity of the track
    track_pop = track["track"]["popularity"]
    
    data['track_uri'].append(track_uri)
    data['track_name'].append(track_name)
    data['artist_uri'].append(artist_uri)
    data['artist_info'].append(artist_info)
    data['artist_name'].append(artist_name)
    data['artist_pop'].append(artist_pop)
    data['artist_genres'].append(artist_genres)
    data['album'].append(album)
    data['track_pop'].append(track_pop)
    
    
df = pd.DataFrame.from_dict(data)


# In[51]:


#df.head()


# In[6]:


#df.to_excel(r'spotifydata.xlsx', index = False)


# In[83]:


df2 = pd.read_excel(r"spotifydata.xlsx")


# In[67]:


df2.head(10)


# In[9]:


countries_json = json.load(open('world-countries.json', 'r'))


# In[79]:


print(countries_json['features'][165])


# In[121]:


#Hier zijn de top 10 nummers op basis van populariteit te zien.
#De verdeling is nu rechtsscheef, maar er zit geen verloop in onze data, elk van de 25 nummers staan los van elkaar.
topTen = df.sort_values(by='track_pop', ascending=False).iloc[:10]
fig2 = px.bar(topTen, x="track_name",
              y="track_pop",
              color="track_pop",
              text="track_name",
              labels={'track_pop':'Populariteit van nummer (0-100)', 'track_name':'Naam van het nummer'},
              title="Top 10 populairste nummers van de playlist",
              width=850,
              height=850)

fig2.update_layout(yaxis={'categoryorder':'category ascending'})


# In[86]:


#Op de kaart is te zien hoe populair het populairste nummer van de artiest in zijn of haar eigen land is.
m = folium.Map([30 , 0],tiles="http://tile.stamen.com/watercolor/{z}/{x}/{y}.jpg", attr="Stamen Watercolor",
                        zoom_start=2,
                        width="%100",
                        height="%100")
folium.Choropleth(
    geo_data=countries_json,
    data=df2,
    columns=['country', 'artist_pop'],   
    legend_name='Populariteit van het populairste nummer in geboorteland van artiest',
    key_on='properties.name',
    fill_color="YlGn",
    fill_opacity=0.75,
    line_opacity=1,
    ).add_to(m)


# In[123]:


#Hier geven we de populariteit per track weer in verhouding met de populariteit van de artiesten.
#De trendline geeft de correlatie weer tussen de twee variabelen. Zoals te zien maakt het niet veel uit of een artiest populair is om een hit te scoren. 
#Outliers Love The Way You Lie & Niña Bonita
fig = px.scatter(df2, x="artist_pop",
                 y="track_pop",
                 trendline="ols",
                 color="track_name",
                 trendline_scope="overall",
                 labels={'track_pop':'Populariteit van nummer', 'artist_pop':'Populariteit van de artiest'},
                 title="Verhouding tussen de populariteit van de artiest en de populariteit van het nummer",
                 width=1200,
                 height=850,
                )


# In[103]:


#Het aanmaken van de tabel die alle nummers, albums en de populariteit van de nummers van een artiest laat zien.
table_df = df2[["artist_name", "track_name", "album", "track_pop"]].copy()

fig3 = pgo.Figure(pgo.Table(header={"values": ["artist_name", "track_name", "album","track_pop"], "fill": dict(color='grey')}, cells={"values": [["artist_name", "track_name", "album", "track_pop"]], "fill": dict(color='black')}))


fig3.update_layout(
    updatemenus=[
        {
            "buttons": [
                {
                    "label": country,
                    "method": "update",
                    "args": [
                        {
                            "cells": {
                                "fill": dict(color='black'), "values":  table_df.loc[df2["country"].eq(country)].T.values
                            }
                        }
                    ],
                }
                for country in df2["country"].unique().tolist()
            ]
        }
    ]
)


# In[87]:


#De gehele opbouw van de streamlit app!:
pages = st.sidebar.radio('paginas',options=['Home', 'Dataset', 'Histogram', 'Spreidingsdiagram', 'Kaart', 'Tabel'], label_visibility='hidden')

if pages == 'Home':
    st.subheader("Visual Analytics Eindopdracht - Spotify API")
    st.markdown("Data Science 2022 - HvA - Osman, Floris & Jakob")
    
elif pages == 'Dataset':
    st.markdown("Hieronder de weergave van de Spotify API die wij hebben gebruikt:")
    
    st.subheader('Spotify Dataset')
    st.markdown("De rauwe opgehaalde data rechtstreeks vanuit de url van de door ons gebruikte Spotify playlist.")
    st.dataframe(data=df, use_container_width=False)
    
    st.subheader('Nu met toegevoegde geografische informatie')
    st.markdown("Hier een overzicht van wat het .xslx bestand met de toegevoegde geografische informatie van de Spotify data laat zien.")
    st.dataframe(data=df2, use_container_width=False)
    
elif pages == 'Histogram':
        st.subheader('Histogram van de top 10 meest populaire nummers uit de playlist')
        st.markdown("Bekijk hier een histogram van de meest populaire nummers en hoe deze nummers heten.")
        st.markdown("De verdeling is nu rechtsscheef, maar er zit geen verloop in onze data, elk van de 25 nummers staan los van elkaar. Dus er is geen echte verdeling.")
        st.plotly_chart(fig2)
        
elif pages == 'Spreidingsdiagram':
        st.subheader('Verhouding tussen de populariteit van de artiest en de populariteit van het nummer, met de focus op het nummer')
        st.markdown("In de spreidingsdiagram valt het op dat de artiest niet ongelofelijk populair hoeft te zijn om een hit te scoren. Een uitzondering is het nummer 'Love The Way You Lie' van Eminem. De zichtbare trendline geeft de correlatie weer tussen de populariteit van de artiest en van het nummer. Outliers zouden 'Love The Way You Lie' & 'Niña Bonita'zijn. ")
        st.plotly_chart(fig)
        
elif pages == 'Kaart':
        st.subheader('De score van het meest populaire nummer in het land van afkomst van de artiesten')
        st.markdown("De Spotify API-dataset is gebruikt met drie nieuwe kolommen waar het land van afkomst per artiest in staat.")
        st.markdown("Het valt op dat Shakira, wie erg populair is, met haar nummer 'Waka Waka' erg laag scoort op de huidige populariteitslijst. Het nummer is ook al weer 12 jaar oud...")
        st.markdown("Ook is te zien dat landen met minder artiesten, zoals Australië en Venezuela, een minder hoge populariteitsscore hebben. Dit is een logisch verband omdat bijvoorbeeld de Verenigde Staten veel meer artiesten heeft en dus een grotere kans heeft dat er één erg populair is.")
        folium_static(m)
        
elif pages == 'Tabel':
        st.subheader('Bekijk alle informatie over je favoriete nummers, artiesten en albums uit de playlist, per land!')
        st.markdown("Klik op een land binnen de dropdown om een selectie te maken")
        st.plotly_chart(fig3)

