# YouTube Data Harvesting and Warehousing using SQL and Streamlit

* YouTube, the online video-sharing platform, has revolutionized the way we consume and interact with media. Launched in 2005, it has grown into a global phenomenon, serving as a hub for entertainment, education, and community engagement. With its vast user base and diverse content library, YouTube has become a powerful tool for individuals, creators, and businesses to share their stories, express themselves, and connect with audiences worldwide.

* In this project, we have tried collecting Data from YouTube API Key and we have collected information like Channel Details, Video Details, and Comment Details using Python Programming and fetched all those data in MYSQL Database and made few analysis out of it.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Implemention](#implemention)
- [Improvement](#improvement)

## Installation
1. **Tools Required:**   
   - VS Code or Any IDE.
   - Python 3.12.3 or higher.
   - XAMPP MySQL.
   - YouTube API key.

2. **Libraries to Install:**
   - `pip install streamlit`
   - `pip install pandas`
   - `pip install mysql.connector`
   - `pip install --upgrade google-api-python-client`

## Usage
   - Use VS Code to execute the `youtubeDDL's.py` and `youtubeproject.py` scripts.
   - Set up and use XAMPP to store and retrieve data.
   - Obtain a YouTube API key by following this [tutorial](https://www.youtube.com/watch?v=F5yQ1BgDIDQ).

## Implementation

a) ETL Process: 
   The whole idea is, with the input of Channelid we are extracting all the information like Channel Details, Video Details, and Comment Details with the help of DataFrames and we have converted it into Tables in Database tables which is mentioned in Scripts 'youtubeDDL's.py' and we also showing Channelids which are already available in the Database.

b) Execution Order:
   Considering you have the Tools required and Libraries installed, Please execute youtubeDDL's.py and then youtubeproject.py should be executed. However, no parallel execution is recommended.

b) Streamlit Application:
   This will User Interface to interact with users, Like all the other libraries it can be installed but it cannot be executed in the VScode Terminal, 
      Step1: You have to run the below command:
   <img width="614" alt="image" src="https://github.com/Immervin/Mycode/assets/164136203/3d513a26-19a7-4a53-bfb0-1d17bb2bf0cf">
      Step2 : Here Streamlit run is the keyword to run and then the name of the file which you want to run.
      Step3 : please give input when it navigates to the localhost of the streamlit application.

## Improvement
   However, this is developed to show you on API Key data retrieval and to store data in the backend, it cannot able to update when the same channelid is passed.
   It has some basic Questions from the data which we collect and showed how it can be used for analyzing any open-source data or it can be used as a base to develop any application.
