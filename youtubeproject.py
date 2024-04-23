import streamlit as st
import pandas as pd
import mysql.connector
import googleapiclient.discovery
import re

api_service_name = "youtube"
api_version = "v3"
api_key=""

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

# channel_details
def channel_details(channel_id):
    request = youtube.channels().list(part="snippet,contentDetails,statistics,status", id=channel_id)
    response = request.execute()
    
    for channel in response['items']:
        data = {
            'channelid': channel['id'],
            'channelname': channel['snippet']['title'],
            'channeldes': channel['snippet']['description'],
            'channelviewc': channel['statistics']['viewCount'],
            'channelvideoc':channel['statistics']['videoCount'],
            'channelsubc': channel['statistics']['subscriberCount'],
            'channelplyid': channel['contentDetails']['relatedPlaylists']['uploads'],
            'channelstatus': channel['status']['privacyStatus']
        }

    return data

# Function to convert duration string to seconds
def duration_to_seconds(duration_str):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duration_str)
    if match:
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        seconds = int(match.group(3)[:-1]) if match.group(3) else 0
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return None
    
   
#videoids collection
def get_video_ids(channel_playlist_id):
    video_id = []
    next_page_token = None
    while True:
        response = youtube.playlistItems().list(part='contentDetails',playlistId=channel_playlist_id,maxResults=50,pageToken=next_page_token).execute()
        for i in response['items']:
            video_id.append(i['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break    
    return video_id,channel_playlist_id

#video data information
def get_video_data(vid,pid):
    # Retrieve the video data
    response = youtube.videos().list(part='snippet,statistics,contentDetails',id=vid).execute()

    # Check if response contains any items
    if 'items' in response:
        # videos = {}
        for video in response['items']:
            video_data = {
                'videoId': video['id'],
                'playlistid':pid,
                'videoName': video['snippet']['title'],
                'videoDescription': video['snippet'].get('description','NA'),
                'publishDate': video['snippet']['publishedAt'],
                'viewCount': video['statistics'].get('viewCount',0),
                'likeCount': video['statistics'].get('likeCount', 0),
                'favoriteCount': video['statistics'].get('favoriteCount', 0),
                'commentCount': video['statistics'].get('commentCount', 0),
                'duration': duration_to_seconds(video['contentDetails'].get('duration', 0)),
                'thumbnail': video['snippet']['thumbnails']['high']['url'],
                'captionstatus':video['contentDetails']['caption']
            }
            # videos[video['id']] = video_data
        return video_data
    else:
        print("No videos found for the given ID.")
        return None
    
#comment
def get_comment_details(vid):

    response = youtube.commentThreads().list(part='snippet', maxResults=10, videoId=vid).execute()

    comment_data=[]
    
    for i in response['items']:
        comment_data.append({
        'commentId': i['snippet']['topLevelComment']['id'],
        'videoid':vid,
        'commenttext': i['snippet']['topLevelComment']['snippet']['textOriginal'],
        'author': i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
        'publishedDate': i['snippet']['topLevelComment']['snippet'].get('publishedAt','NA')
         })

    return comment_data

#10 Questions 
def execute_query(user_response):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database='youtube_data'
    )

    mycursor = mydb.cursor(buffered=True)

    query = ""
    if user_response == "What are the names of all the videos and their corresponding channels?":
        query = 'SELECT c.channel_name AS "Channel Name" ,v.video_name AS "Video Name" FROM channel_details c, videos v WHERE c.channel_plylstid=v.playlist_id ORDER BY c.channel_id'
    elif user_response == "Which channels have the most number of videos, and how many videos do they have?":
        query = 'SELECT channel_name AS "Channel Name", channel_videoc AS "Most Number of Videos" FROM channel_details WHERE channel_videoc IN (SELECT MAX(channel_videoc) FROM channel_details)'
    elif user_response == "What are the top 10 most viewed videos and their respective channels?":
        query = 'SELECT c.channel_name AS "Channel Name", v.video_name AS "Video Name", v.view_count AS "View Count" FROM channel_details c, videos v WHERE c.channel_plylstid=v.playlist_id ORDER BY view_count DESC LIMIT 10'
    elif user_response == "How many comments were made on each video, and what are their corresponding video names?":
        query = 'SELECT v.video_name, COUNT(c.comment_text) AS comment_count FROM videos v LEFT JOIN comments c ON v.video_id = c.video_id AND comment_id NOT LIKE "error%" GROUP BY v.video_name'
    elif user_response == "Which videos have the highest number of likes, and what are their corresponding channel names?":
        query = 'SELECT v.video_name AS "Video Name", v.like_count AS "Like Count", cd.channel_name AS "Channel Name" FROM videos v JOIN channel_details cd ON v.playlist_id = cd.channel_plylstid WHERE v.like_count = (SELECT MAX(like_count) FROM videos)'
    elif user_response == "What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        query = '''SELECT v.video_name AS "Video Name", SUM(v.like_count) AS "Total Likes", 'NA' AS "Total Dislikes" 
                    FROM videos v GROUP BY v.video_id, v.video_name '''
    elif user_response == "What is the total number of views for each channel, and what are their corresponding channel names?":
        query = 'SELECT channel_name AS "Channel Name", channel_viewc AS "Channel View Count" FROM channel_details'
    elif user_response == "What are the names of all the channels that have published videos in the year 2022?":
        query = 'SELECT DISTINCT cd.channel_name AS "Channel Name" FROM channel_details cd JOIN videos v ON cd.channel_plylstid = v.playlist_id WHERE YEAR(v.publish_dt) = 2022'
    elif user_response == "What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        query = 'SELECT cd.channel_name AS "Channel Name", AVG(v.duration) AS "Average Duration" FROM channel_details cd JOIN videos v ON cd.channel_plylstid = v.playlist_id GROUP BY cd.channel_name'
    elif user_response == "Which videos have the highest number of comments, and what are their corresponding channel names?":
        query = '''select distinct tply.video_name "Video Name",cd.channel_name "Channel Name",tply.count_comment "Comment Count" from 
                     (select count_comment,
					         v.playlist_id,
							 video_name 
					  from(SELECT count_comment,
					               video_id 
						   FROM (SELECT COUNT(comment_id) AS count_comment,
						                video_id 
								 FROM comments                    
								 where comment_id not like 'error%' GROUP BY video_id) AS tmax) tvideo,videos v 
					  where tvideo.video_id=v.video_id)tply, channel_details cd 
where cd.channel_plylstid=tply.playlist_id and 
count_comment =(SELECT MAX(count_comment) 
                FROM (SELECT COUNT(comment_id) AS count_comment 
				FROM comments GROUP BY video_id) AS tmax)'''

    mycursor.execute(query)
    result = mycursor.fetchall()
    columns = [i[0] for i in mycursor.description]
    df = pd.DataFrame(result, columns=columns)
    mydb.close()
    return df



try:
    # Establish a connection to the MySQL database
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database='youtube_data'
    )

  
    mycursor = mydb.cursor(buffered=True)  

    # Get user input for channel ID
    channel_id = st.text_input("Enter Channel ID:")

    if channel_id:
        # Validate channel ID
        if len(channel_id) != 24:
            raise ValueError("Invalid Channel ID")

        # Check if channel_id exists in channel_details table
        mycursor.execute('SELECT * FROM channel_details WHERE channel_id = %s', (channel_id,))
        out_channel = mycursor.fetchall()

        questions = {
    "Questionaries": [
        "What are the names of all the videos and their corresponding channels?", 
        "Which channels have the most number of videos, and how many videos do they have?",
        "What are the top 10 most viewed videos and their respective channels?", 
        "How many comments were made on each video, and what are their corresponding video names?",
        "Which videos have the highest number of likes, and what are their corresponding channel names?",
        "What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
        "What is the total number of views for each channel, and what are their corresponding channel names?",
        "What are the names of all the channels that have published videos in the year 2022?",
        "What is the average duration of all videos in each channel, and what are their corresponding channel names?",
        "Which videos have the highest number of comments, and what are their corresponding channel names?"
    ]
}

        if out_channel:
            # If channel_id exists, fetch details from channel_details table
            columns = [i[0] for i in mycursor.description]
            df_final_channel = pd.DataFrame(out_channel, columns=columns)
            # st.dataframe(df_final_channel,hide_index=True)

            #db video data 
            mycursor.execute('SELECT * FROM videos WHERE playlist_id in (select channel_plylstid from channel_details where channel_id= %s) ', (channel_id,))
            out_video = mycursor.fetchall()

            columns = [i[0] for i in mycursor.description]
            df_final_video = pd.DataFrame(out_video, columns=columns)
            # st.dataframe(df_final_video,hide_index=True)

            mycursor.execute('select * from comments where video_id in (select video_id from videos where playlist_id in (select channel_plylstid from channel_details where channel_id= %s))',(channel_id,))
            
            out_comment=mycursor.fetchall()

            columns = [i[0] for i in mycursor.description]
            df_final_comments = pd.DataFrame(out_comment, columns=columns)

                             
            options = [ 'Channel Details','Video Details','Comment Details']

            # Create a radio button with the options list
            selected_option = st.radio( "Select below options",options)

            # Display the selected dataframe based on the option chosen
            if selected_option == 'Channel Details':
                st.dataframe(df_final_channel,hide_index=True)
            elif selected_option == 'Video Details':
                st.dataframe(df_final_video,hide_index=True)
            elif selected_option == 'Comment Details':
                st.dataframe(df_final_comments,hide_index=True)

 

            # Display the questions and dropdown menus
            user_response = st.selectbox("Questionaries", questions["Questionaries"])
            if user_response:
                df = execute_query(user_response)
                if not df.empty:
                    st.dataframe(df, hide_index=True)
                else:
                    st.write("No data available for this question.")                            
        

        else:
            # If channel_id does not exist, fetch details from YouTube API
            dict_channel_details = channel_details(channel_id)
            df_channel_details = pd.DataFrame(dict_channel_details, index=[0])

            # Insert details into channel_details table
            for index, row in df_channel_details.iterrows():
                mycursor.execute('''INSERT INTO channel_details (channel_name, channel_id, channel_des, channel_viewc,channel_videoc, channel_subc, channel_plylstid, channel_status) 
                                 VALUES (%s, %s, %s, %s, %s, %s, %s,%s)''', 
                                 (row['channelname'], row['channelid'], row['channeldes'], row['channelviewc'],row['channelvideoc'], row['channelsubc'], row['channelplyid'], row['channelstatus']))
            mydb.commit()

            # Fetch inserted details from channel_details table
            mycursor.execute('SELECT * FROM channel_details WHERE channel_id = %s', (channel_id,))
            result = mycursor.fetchall()
            columns = [i[0] for i in mycursor.description]
            df_final_channel = pd.DataFrame(result, columns=columns)
            # st.dataframe(df_final_channel,hide_index=True)

            #Video section Execution

            mycursor.execute('SELECT channel_plylstid FROM channel_details WHERE channel_id = %s', (channel_id,))
            result_pid=mycursor.fetchall()
            
            # Extract playlist IDs 
            playlist_ids = [pid_row[0] for pid_row in result_pid]  

            for playlist_id in playlist_ids:
                # Fetch video data for each playlist ID and insert into the database
                video_id, pid = get_video_ids(playlist_id)

            lvideodata = []

            for i in video_id:
                video_data = get_video_data(i, pid)
                lvideodata.append(video_data)

            df_video = pd.DataFrame(lvideodata)

            for index, row in df_video.iterrows():
                    mycursor.execute('''INSERT INTO videos (video_id, playlist_id, video_name, video_des, publish_dt, view_count, like_count, fav_count, comment_count, duration, thumbnail, caption_status) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                                    (row['videoId'], playlist_id, row['videoName'], row['videoDescription'], row['publishDate'], row['viewCount'], row['likeCount'], row['favoriteCount'], row['commentCount'], row['duration'], row['thumbnail'], row['captionstatus']))

            mydb.commit()

                # Fetch inserted details from videos table
            mycursor.execute('SELECT * FROM videos WHERE playlist_id in (select channel_plylstid from channel_details where channel_id= %s)', (channel_id,))
            result = mycursor.fetchall()
            columns = [i[0] for i in mycursor.description]
            df_final_video = pd.DataFrame(result, columns=columns)
            # st.dataframe(df_final_video, hide_index=True)
            # display(df)

            #comment section insert
            mycursor.execute('SELECT video_id FROM videos WHERE playlist_id in (select channel_plylstid from channel_details where channel_id= %s)',(channel_id,))
            results = mycursor.fetchall()
            videoid_list = [result[0] for result in results]

            comment_result = []
            for comment in videoid_list:
                try:
                    comment_result = get_comment_details(comment)
                    df_comments = pd.DataFrame(comment_result)

                    for index, row in df_comments.iterrows():
                        mycursor.execute('''INSERT INTO comments(comment_id, video_id, comment_text, comment_author, comment_publishd_dt)
                                            VALUES (%s, %s, %s, %s, %s)''',
                                        (row['commentId'], row['videoid'], row['commenttext'], row['author'], row['publishedDate']))
                        mydb.commit()

                except Exception as e:
                    if 'commentsDisabled' in str(e):
                        # Insert dummy comment when comments are disabled
                        mycursor.execute('''INSERT INTO comments (comment_id, video_id, comment_text, comment_author, comment_publishd_dt)
                                            VALUES (%s, %s, %s, %s, %s)''',
                                        ('error' + str(comment), comment, 'Commentdisabled', 'Commentdisabled', 'NA'))
                        mydb.commit()
                        # print(f"Comments are disabled for video with video_id: {video_id}")
                    else:
                        print(f"An error occurred: {str(e)}")
            
            #fetch comment details
            mycursor.execute('SELECT * FROM videos WHERE playlist_id in (select channel_plylstid from channel_details where channel_id= %s)',(channel_id,))
            result = mycursor.fetchall()
            columns = [i[0] for i in mycursor.description]
            df_final_comments = pd.DataFrame(result, columns=columns)



            options = [ 'Channel Details','Video Details','Comment Details']

            # Create a radio button with the options list
            selected_option = st.radio( "Select below options",options)

            # Display the selected dataframe based on the option chosen
            if selected_option == 'Channel Details':
                st.dataframe(df_final_channel,hide_index=True)
            elif selected_option == 'Video Details':
                st.dataframe(df_final_video,hide_index=True)
            elif selected_option == 'Comment Details':
                st.dataframe(df_final_comments,hide_index=True)

            # Display the questions and dropdown menus
            user_response = st.selectbox("Questionaries", questions["Questionaries"])
            if user_response:
                df = execute_query(user_response)
                if not df.empty:
                    st.dataframe(df, hide_index=True)
                else:
                    st.write("No data available for this question.")   

    # Close the database connection
    mydb.close()

except ValueError as ve:
    # Display error message in Streamlit
    st.error(str(ve))

except Exception as e:
    # Display error message in Streamlit
    st.error(f"An error occurred: {str(e)}")
