def create_tables():
    import mysql.connector

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database='youtube_data'
    )

    mycursor = mydb.cursor(buffered=True)

    # Create channel_details table if it does not exist
    mycursor.execute('''CREATE TABLE IF NOT EXISTS channel_details (
                        channel_name VARCHAR(255),
                        channel_id VARCHAR(255) PRIMARY KEY,
                        channel_des TEXT,
                        channel_viewc INT,
                        channel_videoc INT,
                        channel_subc INT,
                        channel_plylstid VARCHAR(255),
                        channel_status VARCHAR(50)
                    )''')

    # Create videos table if it does not exist
    mycursor.execute('''CREATE TABLE IF NOT EXISTS videos (
                        video_id VARCHAR(225) PRIMARY KEY,
                        playlist_id VARCHAR(255),
                        video_name VARCHAR(225),
                        video_des TEXT,
                        publish_dt DATETIME,
                        view_count INT,
                        like_count INT,
                        fav_count INT,
                        comment_count INT,
                        duration INT,
                        thumbnail VARCHAR(255),
                        caption_status VARCHAR(255)
                    )''')

    # Create comments table if it does not exist
    mycursor.execute('''CREATE TABLE IF NOT EXISTS comments (
                        comment_id VARCHAR(255) PRIMARY KEY,
                        video_id VARCHAR(255),
                        FOREIGN KEY (video_id) REFERENCES videos(video_id),
                        comment_text TEXT,
                        comment_Author VARCHAR(255),
                        comment_publishd_dt DATETIME
                    )''')

    # Close the cursor and connection
    mycursor.close()
    mydb.close()

# Call the function to create the tables
create_tables()
