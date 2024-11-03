from pytubefix import YouTube
from dotenv import load_dotenv
import os
from langchain.tools import tool

from jarvis.helper.db import Database

load_dotenv()

class MusicService():
    def __init__(self):
        self.music_path = os.getenv("MUSIC_PATH")

    def download_video_as_mp3(self, link: str, folder_name: str) -> str:
            """
            Downloads a YouTube video as MP3 audio file and saves it to a specified directory.
        
            Args:
                link (str): The YouTube video URL to download
                name ("lo-fi" | "singing" | "rap" | "motivation" | "opening"): folder
        
            Returns:
                str: The full path where the MP3 file was saved 
            """
            path = os.path.join(self.music_path, folder_name)

            yt = YouTube(link)

            stream = yt.streams.filter(only_audio=True).first()
            file_name = f"{yt.title}.mp3"
            stream.download(filename= file_name, output_path=path)

            full_file_path = os.path.join(path, file_name)

            return full_file_path

@tool
def youtube_to_mp3(link: str, folder: str) -> str:
    """
    Downloads a YouTube video as MP3 audio file and saves it to a specified directory.

    Args:
        link (str): The YouTube video URL to download
        folder ("lo-fi" | "singing" | "rap" | "motivation" | "opening"): The folder in which we have to save the mp3 file. It is an enum

    Returns:
        str: The full path where the MP3 file was saved
    """

    music_service = MusicService()
    path = music_service.download_video_as_mp3(link=link, folder_name=folder)

    return path
    # return path