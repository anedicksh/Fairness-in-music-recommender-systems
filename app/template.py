import streamlit as st
from random import random
import json
import datetime
import pandas as pd
import csv
import subprocess
import RS

# save the activities as a file
def save_activities():
  with open('activities.json', 'w') as outfile:
    json.dump(st.session_state['activities'], outfile, indent=4)

# function that processes an activity
def activity(index, activity):
  st.session_state['index'] = index
  if 'activities' not in st.session_state:
    st.session_state['activities'] = []
  data = {'track_id': int(index), 'activity': activity, 'user_id': st.session_state['user'], 'datetime': str(datetime.datetime.now())}
  # add to the session state
  st.session_state['activities'].append(data)
  # directly save the activities
  save_activities()
    

def more_recommendations(activity):
    if 'activities' not in st.session_state:
      st.session_state['activities'] = []
    data = {'activity': activity, 'user_id': st.session_state['user'], 'datetime': str(datetime.datetime.now())}
    # add to the session state
    st.session_state['activities'].append(data)
    # directly save the activities
    save_activities()


def select_song(item):
    index = item['index']
    st.session_state['index'] = index
    #song_index = df.index[df['Top Track'] == track].tolist()
    #add song to the activities.json
    activity(index, 'Select Song')
    user_logged_in = st.session_state['user']
    #Run python file when button is pressed   
    RS.RS_function(user_logged_in)
    
    
    
def tile_item(column, item):
  
  with column:
    st.button('▶️', key=random(), on_click=select_song, args=(item,))
    st.image(item['Image-URL-L'], use_column_width='always')
    st.caption(item['Top Track'])
    st.caption(item['Artist'])
    st.caption(item['Genre'])

# def tiles(df): is the same
def recommendations(df):
  
    # check the number of items
    nbr_items = df.shape[0]

    if nbr_items != 0:
        # create columns with the corresponding number of items
        num_cols = 5
        num_rows = -(-nbr_items // num_cols)  # ceil division
        columns = [st.columns(num_cols) for _ in range(num_rows)]

        # convert df rows to dict lists
        items = df.to_dict(orient='records')

        # loop over the items and display them using tile_item
        item_index = 0
        for row in columns:
            for column in row:
                if item_index < nbr_items:
                    tile_item(column, items[item_index])
                    item_index += 1

