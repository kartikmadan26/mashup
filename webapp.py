# importing all required libraries
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

SENDER_ADDRESS=st.secrets["email"]
# encrypted password
SENDER_PASSWORD=st.secrets["password"]
SMTP_SERVER_ADDRESS='smtp.gmail.com'

def slicing(path, y, sounds):
    # path = "audio"+str(i)+".mp3"
    sound = AudioSegment.from_file(path)
    start_time = y*1000
    extract = sound[:start_time]
    print(path)
    sounds.append(extract)


def merge(sounds, mashup):
    for i in sounds:
        mashup = mashup+i
    return mashup

def download_audio(link, name):
    yt = YouTube(link)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=".")
    # base, ext = os.path.splitext(out_file)
    new_file = name + '.mp3'
    os.rename(out_file, new_file)

def mp3_to_zip(mp3_file_path, zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
        zip_file.write(mp3_file_path, arcname=mp3_file_path)

def main():
    st.header('Create your own mashup')

    with st.form("my_form"):
        singer_name = st.text_input('Please enter name of Singer',placeholder="Singer Name")
        number_of_videos=st.number_input("Insert number of videos ",min_value=10,)
        audio_duration=st.number_input("Duration of each video ",min_value=20,)
        file_name=st.text_input("Please enter file name",placeholder="File Name")
        email_id = st.text_input('Please enter your Email ID',placeholder="Email")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Please check your mailbox")
            results = YoutubeSearch(
            singer_name, max_results=number_of_videos).to_dict()
            urls = []
            for i in results:
                if i['duration'] == 0:
                    continue
                url = i['url_suffix']
                url = "https://www.youtube.com"+url
                urls.append(url)
            threads = []
            for i in range(len(urls)):
                name = "audio"+str(i)
                t = threading.Thread(target=download_audio, args=(urls[i], name))
                t.start()
                threads.append(t)
            for thread in threads:
                thread.join()
            threads = []
            file_list = []
            sounds = []
            mashup = AudioSegment.empty()
            for i in range(number_of_videos):
                path = "audio"+str(i)+".mp3"
                file_list.append(path)
                t = threading.Thread(target=slicing, args=(
                    path, audio_duration, sounds))
                t.start()
                threads.append(t)
            for thread in threads:
                thread.join()
            base = merge(sounds, mashup)
            if ".mp3" not in file_name:
                file_name = file_name+".mp3"
            base.export(file_name, format="mp3")
            for i in range(len(file_list)):
                os.remove(file_list[i])
            mp3_to_zip(file_name,"zipfile.zip")
            os.remove(file_name)
            send_email(SENDER_ADDRESS, SENDER_PASSWORD, email_id, SMTP_SERVER_ADDRESS, 587, 'Here is your zip file', 'Mashup', 'zipfile.zip')
    st.write("By :- Kartik Madan (102003565) ")
if __name__=='__main__':
    main()
