import streamlit as st
import pandas as pd
import template as t
import json
from itertools import cycle
from random import random
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import RS

st.set_page_config(page_title="Music recommender system", layout="wide")

#---------------------

# USER AUTHENTICATION

#---------------------

# Load user data from CSV file
user_data = pd.read_csv("login_data.csv", delimiter = ",")


def authenticate_user(username, password):

    """Authenticate a user based on their username and password."""
    user = user_data[(user_data["Username"] == username) & (user_data["Password"] == password)]
    
    if len(user) == 1:
        user_id = user["User-ID"]
        return True
    else:
        return False


# Define login page
def login():
    
    st.title("Login Page")

    # Get username, password and id from user
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Authenticate user
    if st.button("Login"):
        
        user = user_data[(user_data["Username"] == username) & (user_data["Password"] == password)]
        user_id = int(user["User-ID"].iloc[0])
        if authenticate_user(username, password):
            st.success("Logged in as {}".format(username))

            # Store the user ID in the session state
            st.session_state['user'] = user_id
            
            # Redirect to main page
            st.experimental_set_query_params(logged_in=True, page ='main')
            
        else:
            st.error("Invalid username or password")

    else:
        st.warning("Please enter your username and password")



#---------------------
        
# MAIN PAGE
        
#---------------------

# Define main page
def main():
    
    st.title("Music recommender system", anchor=None)

    # open the activities json file
    with open('activities.json') as json_file:
        users_activities = json.load(json_file)

    #---------------------

    #LOAD DATA

    #---------------------

    # spotify tracks
    df_songs = pd.read_csv('content_data.csv', delimiter=';', encoding='latin-1', on_bad_lines = 'skip')
    # Load user data 
    df_users = pd.read_csv('user_data.csv', delimiter = ",")

    #---------------------

    #STREAMLIT APP

    #---------------------

    st.header('Made for you')
    df = pd.read_csv('recommendations/recommendations.csv', sep=',', encoding='latin-1', dtype=object)
    df_songs.columns = df_songs.columns.str.replace('ï»¿Artist', 'Artist')
    #df = df.merge(df_songs, on='Top_Track')
    t.recommendations(df)

    st.header('Not happy with your recommendations?')
    st.subheader('I want more of...')

    
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns(10)

    def handle_rock_click():
        t.more_recommendations('More Rock')
        user_id = st.session_state['user']
        #Run python file when button is pressed   
        RS.RS_function(user_id)

    def handle_hip_hop_click():
        t.more_recommendations('More Hip Hop/ Rap')
        user_id = st.session_state['user']
        #Run python file when button is pressed   
        RS.RS_function(user_id)

    def handle_techno_click():
        t.more_recommendations('More Techno')
        user_id = st.session_state['user']
        #Run python file when button is pressed   
        RS.RS_function(user_id)
    
    def handle_indie_click():
        t.more_recommendations('More Indie')
        user_id = st.session_state['user']
        #Run python file when button is pressed   
        RS.RS_function(user_id)

    def handle_pop_click():
        t.more_recommendations('More Pop')
        user_id = st.session_state['user']
        #Run python file when button is pressed   
        RS.RS_function(user_id)

    with col1:
        st.button('Rock', on_click=handle_rock_click)

    with col2:
        st.button('Hip Hop/Rap', on_click=handle_hip_hop_click)

    with col3:
        st.button('Techno', on_click=handle_techno_click)

    with col4:
        st.button('Indie', on_click=handle_indie_click)

    with col5:
        st.button('Pop', on_click=handle_pop_click)

 




    #---------------------

    # INITIALIZATION: SESSION STATE

    #---------------------

    # Initialize the 'user' key in the st.session_state dictionary

    if 'user' not in st.session_state:
        st.session_state['user'] = None
        
    if 'activities' not in st.session_state:
        st.session_state['activities'] = []
        
    if 'recommendations' not in st.session_state:
        st.session_state['recommendations'] = df

 
     
# Check if user is logged in and display appropriate page

if st.experimental_get_query_params().get("logged_in", [None])[0] == "True":
    main()
else:
    login()






  
