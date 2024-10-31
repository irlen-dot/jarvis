from pytubefix import YouTube
from dotenv import load_dotenv
import os
from langchain.tools import tool

load_dotenv()

# TODO Sort By Genre Folders

# @tool
def youtube_to_mp3(link: str, name: str):
    path = os.path.join(os.getenv("MUSIC_PATH"), name) 
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    print(stream)
    stream.download(filename=f"{yt.title}.mp3", output_path=path)

    # return path