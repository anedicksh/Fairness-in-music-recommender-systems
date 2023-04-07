#libraries
import numpy as np
import random
import pandas as pd
import json
from numpy.linalg import norm
from numpy import dot

def RS_function(user_logged_in):
    
    data = pd.read_csv('content_data.csv', delimiter = ';')
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]

    data.Genre.unique()

    #rename genre for songs with whitespace behind 'Rock' (see unique genres)
    data.loc[list(data[data.Genre == 'Rock '].index),'Genre'] = 'Rock'
    #remove rows with nan values (see unique genre values)
    data = data[~data.Genre.isna()]
    data = data.reset_index()

    #read user data and reset index (to make it less messy)
    user_data = pd.read_csv('user_data.csv',index_col=0)
    user_data = user_data.reset_index(drop=True)

    user_data['%_Frequency'] = user_data.groupby(['User-ID'], group_keys=False)['Listening frequency'].apply(lambda x: x*100 / sum(x))


    #create dictionary with titles and listening frequency
    def get_list_freq(user_id, df_subset):
        
        df_user = df_subset[df_subset['User-ID'] == user_id]
            
        return dict(zip(df_user['Top Track'], df_user['Listening frequency']))

    #create vector with listening frequencies
    def create_list_freq_vector(user_list_freq_dict, all_top_tracks_array):
        
        user_top_tracks = user_list_freq_dict.keys()
        
        return [0 if v not in user_top_tracks else user_list_freq_dict[v] for v in all_top_tracks_array]



    def cosine_distance(list_freq_vector_user_a, list_freq_vector_user_b):
        
    #     a . b  -> dot(a, b)
    #     -----
    #     |a||b| -> norm(a) * norm(b)
        
        return dot(list_freq_vector_user_a, list_freq_vector_user_b) / (norm(list_freq_vector_user_a) * norm(list_freq_vector_user_b))


    def retrieve_user_hist(user_id):
        #define songs and preferences of user to be saved
        genres = ['Indie', 'Pop', 'Hip Hop/ Rap', 'Rock', 'Techno']
        user0_songs = pd.DataFrame()
        user0_prefs = {'Hip Hop/ Rap': 0,
                        'Indie': 0,
                        'Pop': 0,
                        'Rock': 0,
                        'Techno': 0}
        song_ids = []
        user_new = False
        
        #try opening activities file (=user has already performed at least one action)
        try:
            with open('activities.json') as f:
                hist = list(json.load(f))   
        
            #check if last action was voicing a preference or selecting a song and create dummy
            if hist[-1]['activity'] == 'Select Song':
                recent_pref = None
            else:
                recent_pref = hist[-1]['activity'] #set dummy
                user0_prefs[hist[-1]['activity'][5:]] = user0_prefs[hist[-1]['activity'][5:]] + 0.5 #add bonus factor for recently pressed button
        
            #retrieve songs from listening activity and user prefs     
            for entry in hist:
                if entry['activity'] == 'Select Song':
                    song_ids.append(entry['track_id'])
                else:
                    #define user prefs history
                    user0_prefs[entry['activity'][5:]] = user0_prefs[entry['activity'][5:]] + 0.5
        
            #add song to user songs            
            for index in song_ids:
                song = data[data['index'] == index].copy()
                song['User-ID'] = user_id
                user0_songs = pd.concat([user0_songs, song])
        
            #create count of each element (to eliminate duplicates but get count of each song)
            user0_songs = user0_songs.groupby(user0_songs.columns.tolist(),as_index=False).size()
        
            #rename 'size' column
            user0_songs = user0_songs.rename(columns = {'size':'Listening frequency'})
        
            #add normalized listening frequency
            user0_songs['%_Frequency'] = user0_songs['Listening frequency'] / sum(user0_songs['Listening frequency'])
        
        #code if user has not yet perceived an action
        except:
            user_new = True
            recent_pref = None
            
        return user0_songs,user0_prefs, recent_pref, user_new



    def sample_recom():
        recommendations = pd.DataFrame()
        
        for genre in genres:
            #sample 1 lesser known song for each genre
            index = random.sample(list(data[(data.Genre == genre) & (data.Popularity < 30)].index),
                                      k = 1)
            song = data[data.index == index[0]]
            recommendations = pd.concat([song, recommendations])
            
            #sample 1 popular song for each genre
            index = random.sample(list(data[(data.Genre == genre) & (data.Popularity > 30)].index),
                                      k = 1)
            song = data[data.index == index[0]]
            recommendations = pd.concat([song, recommendations])
        
        return recommendations


    def retrieve_sim_users(user_data, a_user_id, n_sim_users):
    
        
        top_track_array = user_data['Top Track'].unique()
        top_track_array = np.sort(top_track_array).tolist()
        
        
        #create list of all users
        all_user_ids = user_data['User-ID'].unique().tolist()
        
        #create dictionary with listening counts
        a_user_list_freq = get_list_freq(a_user_id, user_data)
        
        #retrieve top keys
        a_user_top_tracks = a_user_list_freq.keys()
        
        #retrieve listening frequency vector
        a_user_list_freq_vector = create_list_freq_vector(a_user_list_freq, top_track_array)
        
        distances = {}
        
        for u_id in all_user_ids:
        
            if u_id == a_user_id:
                continue
            
            #create dictionary with listening counts
            user_list_freq = get_list_freq(u_id, user_data)
            
            #retrieve listening frequency vector
            user_list_freq_vector = create_list_freq_vector(user_list_freq, top_track_array)
           
            #calculate cosine distances
            d = cosine_distance(a_user_list_freq_vector, user_list_freq_vector)
            
            #put distances in dictionary
            distances[u_id] = d
        
        # Sort the dictionary 'distances' by value in descending order of distance measure
        distances_sorted = {k: v for k, v in sorted(distances.items(), key=lambda item: item[1], reverse=True)}
        
        # Retrieve the 3 user IDs with the highest distance measure (most similar to user A)
        most_sim_users = list(distances_sorted.keys())[:n_sim_users]
        return most_sim_users        
        

    def get_genre_proportion(user_data, user_id):
        #get listening frequency per genre of given user
        genre_prop = user_data[user_data['User-ID'] == user_id].groupby(['Genre'])['Listening frequency'].sum().reset_index()
        
        #Create Column with proportion
        genre_prop['Prop'] = genre_prop.apply(lambda row: row['Listening frequency'] / sum(genre_prop['Listening frequency']),
                                          axis = 1)
        
        #create dictionary to return
        prop = {k:v for k, v in zip(genre_prop.Genre, genre_prop.Prop)}
        return prop


    def adjust_weights(prop, user0_prefs):
        genres = ['Indie', 'Pop', 'Hip Hop/ Rap', 'Rock', 'Techno']

        #create list for the adjusted weights to be returned
        user_weights = []
        
        #make sure every genre is present in weights and all genres have atleast weight of 0.05
        for genre in genres:
            #try function because not every user may have every genre
            #if genre exists in prop:
            try:          
                #every genre always has atleast 0.05 weight in recommendations
                if prop[genre] < 0.05:
                    prop[genre] = 0.05
                    user_weights.append(prop[genre])
                
                else:
                    user_weights.append(prop[genre])
            
            #if genre does not exist in prop:        
            except:
                prop[genre] = 0.05
                user_weights.append(prop[genre])
        
        prop_min5 = prop
        
        #include user preferences
        final_weights = {}
        for key in prop_min5:
            #add factors based on preferences the user voiced
            final_weights[key] = prop_min5[key]+user0_prefs[key]
        
        
        
        return final_weights


    def retrieve_songs(all_user_data, a_user_id, sim_users,prop):
    
        #retrieve all songs from similar users
        sim_songs = all_user_data[all_user_data['User-ID'].isin(sim_users)]
        user_songs = all_user_data[all_user_data['User-ID'] == a_user_id]
        recom_songs = sim_songs[~sim_songs['index'].isin(list(user_songs['index']))]

        #split songs into well and lesser known songs
        sim_songs_wellk = recom_songs[recom_songs.Popularity > 30]
        sim_songs_lessk = recom_songs[recom_songs.Popularity < 30]
        
        #create dataframe
        recommendations = pd.DataFrame()
        
        #Retrieve weights for genres
        user_weights = []
        genres = ['Indie', 'Pop', 'Hip Hop/ Rap', 'Rock', 'Techno']
        for genre in genres:
            user_weights.append(prop[genre])

        while len(recommendations) < 20:
        #for i in range(10):
            #pick genre with odds, depending on users listening behavior
            user_genre = random.choices(genres,
                                        weights = user_weights,
                                        k = 1)
            
            #for the rare case that no songs can be picked (because the similar users have no songs that the user hasn't already listened to, we need a try function)
            try:                  
                #define df with songs of similar users that are the picked genre 
                df_sub_wellk = sim_songs_wellk[(sim_songs_wellk['Genre'] == user_genre[0])]
                
                
                
                indexes = list(df_sub_wellk['index'])
                freq_weights = list(df_sub_wellk['%_Frequency'])

                #pick song based on users listening frequency (the more similar users listened to the song, the more likely song is to be picked)
                index = random.choices(indexes,
                                      weights = freq_weights,
                                      k = 1)
                
                #add song to recommendation
                song_wellk = df_sub_wellk[df_sub_wellk['index'] == index[0]]
                recommendations = pd.concat([recommendations, song_wellk.iloc[0:1]]) #if song was in df_sub_wellk multiple times, add it only once
                recommendations = recommendations.drop_duplicates(ignore_index = True) #avoid adding the same song to recommendations multiple times            
            except:
                continue
            
            #resample user_genre for lesserknown
            try:
                user_genre = random.choices(genres,
                                            weights = user_weights,
                                            k = 1)                               
                                           
                df_sub_lessk = sim_songs_lessk[(sim_songs_lessk['Genre'] == user_genre[0])]
                
                indexes = list(df_sub_lessk['index'])
                freq_weights = list(df_sub_lessk['%_Frequency'])
            
                index = random.choices(indexes,
                                      weights = freq_weights,
                                      k = 1)
            
                song_lessk = df_sub_lessk[df_sub_lessk['index'] == index[0]]
                   
                recommendations = pd.concat([recommendations, song_lessk.iloc[0:1]]) #if song was in df_sub_wellk multiple times, add it only once
                recommendations = recommendations.drop_duplicates(ignore_index = True)
                
            except:
                continue
        
        return recommendations[['Artist','Top Track', 'Genre','Popularity']][:20].reset_index(drop=True)


    def retrieve_recommendations():
        #reading in previos user activity
        user0_songs, user0_prefs, recent_pref, user_new = retrieve_user_hist(user_logged_in)
        #if user is new, sample recommendations
        if user_new == True:
            recommendations = sample_recom()
        
        #if user is not new (1 or more songs in history)
        else:
            #merge user data with songs the user has listened to
            user_data_complete = pd.concat([user_data, user0_songs])
            
            #identify most similar users
            most_sim_users = retrieve_sim_users(user_data = user_data_complete,
                                                a_user_id = user_logged_in,
                                                n_sim_users = 3)
            
            #get genre proportion of user 0
            prop = get_genre_proportion(user_data = user_data_complete,
                                        user_id = user_logged_in)
            
            #retrieve adjusted weights
            prop_adj = adjust_weights(prop, user0_prefs)
            
            recommendations = retrieve_songs(all_user_data = user_data_complete,
                                             a_user_id = user_logged_in,
                                             sim_users = most_sim_users,
                                             prop = prop_adj)
            

            
        return recommendations

    recommendations = retrieve_recommendations()
    links = pd.read_csv('content_data.csv', sep = ';')
    links = links[['Artist',  'Top Track', 'Image-URL-L']]

    user_data = pd.read_csv('user_data.csv', sep = ",")
    user_data = user_data[['Artist',  'Top Track', 'index']]

    recommendations = pd.merge(user_data, recommendations, on=["Artist", "Top Track"], how = "inner")
    recommendations.drop_duplicates(subset=['Artist', 'Top Track'], keep='first', inplace=True)
    
    #merge with recommendations
    recommendations = pd.merge(recommendations,
                               links,
                               on = ['Artist', 'Top Track'],
                               how = 'inner', )
    

    #save to csv for recommendations in streamlit
    recommendations.to_csv('recommendations/recommendations.csv')
    
  

