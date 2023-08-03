# importing all required libraries
from youtubesearchpython import *
import streamlit as st
import sys
from youtube_search import YoutubeSearch
from pytube import YouTube
import os
from pydub import AudioSegment
import threading
import time
from SendEmail import send_email
import zipfile
import shutil
import concurrent.futures
import math
import concurrent.futures
import os
import moviepy.editor as mp
SENDER_ADDRESS=st.secrets["email"]
# encrypted password
SENDER_PASSWORD=st.secrets["password"]
SMTP_SERVER_ADDRESS='smtp.gmail.com'

def downloading(l,j):
    yt = YouTube(l)
    yt = yt.streams.get_by_itag(18)
    yt.download('videos/',filename='song'+f'{j}'+'.mp4')

def convert(index):
    video_file = 'videos/song{}.mp4'.format(index)
    audio_file = 'audios/song{}.mp3'.format(index)
    
    clip = mp.VideoFileClip(video_file)
    audio = clip.audio
    audio.write_audiofile(audio_file)

def converting(n):
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(convert, index) for index in range(n)]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(e)

def cutting(z,m,output):
        file='audios/song'+str(m)+'.mp3'
        sound = AudioSegment.from_mp3(file)
    #Selecting Portion we want to cut
        StrtMin = 0
        StrtSec = 0
        EndMin = 0
        EndSec = min(z,sound.duration_seconds)
    # Time to milliseconds conversion
        StrtTime = StrtMin*60*1000+StrtSec*1000
        EndTime = EndMin*60*1000+EndSec*1000
    # Opening file and extracting portion of it
        extract = sound[StrtTime:EndTime]
        output.append(extract)  

def target(singer_name,n,dur):
    
    z=dur
    s=math.ceil(n/19)
    string=singer_name


    videosSearch = CustomSearch(string+' songs', VideoDurationFilter.short)

    list=[]
    while len(list)<n:
        # print(videosSearch.result()['result'][i]['link'])
        for i in range(19):
            # do not append live youtube videos and append the required number of links that are n
            if len(list) <= n:
                if videosSearch.result()['result'][i]['duration'] != 'Live':
                    list.append(videosSearch.result()['result'][i]['link'])
            if len(list)== n:
                break
        videosSearch.next()
    l1 = []
    count = 0
    for item in list:
        if item not in l1:
            count += 1
            l1.append(item)
    data = [(element,index) for index,element in enumerate(list[:n])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        executor.map(lambda x: downloading(*x), data)
    converting(n)
    merged=AudioSegment.empty()
    output=[]
    data2 = [(z, index, output) for index in range(n)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor2:
        executor2.map(lambda x: cutting(*x), data2)
    for i in output:
         merged=merged+i
    merged.export('media/mashup.mp3', format='mp3')
    import zipfile
    zipObj = zipfile.ZipFile('media/mashup.zip', 'w')
    zipObj.write('media/mashup.mp3')
    zipObj.close()

def main():
    st.header('Create your own mashup')

    with st.form("my_form"):
        singer_name = st.text_input('Please enter name of Singer',placeholder="Singer Name")
        number_of_videos=st.number_input("Insert number of videos ",min_value=10,)
        audio_duration=st.number_input("Duration of each video ",min_value=20,)
        email_id = st.text_input('Please enter your Email ID',placeholder="Email")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Please check your mailbox")
            if not (os.path.exists('audios')):
                os.mkdir('audios')

            if not (os.path.exists('videos')):
                os.mkdir('videos')

            if not (os.path.exists('media')):
                os.mkdir('media')
            target(singer_name,number_of_videos,audio_duration)
            send_email(SENDER_ADDRESS, SENDER_PASSWORD, email_id, SMTP_SERVER_ADDRESS, 587, 'Your Mashup is Ready', 'Mashup', 'media/mashup.zip')
            shutil.rmtree('audios')
            shutil.rmtree('videos')
            shutil.rmtree('media')
    st.write("By :- Kartik Madan (102003565) ")
if __name__=='__main__':
    main()
