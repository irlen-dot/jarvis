from pytubefix import YouTube
from dotenv import load_dotenv
import os
from langchain.tools import tool

load_dotenv()

# TODO Sort By Genre Folders

@tool
def youtube_to_mp3(link: str, folder: str) -> str:
    """
    Downloads a YouTube video as MP3 audio file and saves it to a specified directory.

    Args:
        link (str): The YouTube video URL to download
        name ("lo-fi" | "singing" | "rap" | "motivation" | "opening"): folder

    Returns:
        str: The full path where the MP3 file was saved

    Example:
        YoutubeToMp3(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "opening"
        )

        or

        YoutubeToMp3(
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "rap"
        )
    """

    path = os.path.join(os.getenv("MUSIC_PATH"), folder) 
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    print(stream)
    file_name = f"{yt.title}.mp3"
    stream.download(filename= file_name, output_path=path)
    full_file_path = os.path.join(path, file_name)
    return full_file_path
    # return path