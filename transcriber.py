import os
import pytube
import certifi

from pydantic import BaseModel
from typing import Any, Optional, List
from openai import OpenAI
from pydub import AudioSegment, silence
from moviepy.video.io.VideoFileClip import VideoFileClip

from config import Config

config = Config()
client = OpenAI(api_key=config.OPENAI_KEY)
os.environ['SSL_CERT_FILE'] = certifi.where()


class Segment(BaseModel):
    start: int
    stop: int
    text: str


class YoutubeId(BaseModel):
    title: str
    url: str
    video_id: str
    file_path: str
    transcript: Optional[List[Segment]] = None


class YouTubeTranscriber:

    @classmethod
    def transcribe(cls, urls:  List[str]) -> bool:
        for url in urls:
            youtube_id = cls.transcribe_mp3(cls.download_url(url))
            json_str = youtube_id.model_dump_json()

            file_name = f"{youtube_id.video_id}.json"
            counter = 1
            while os.path.exists(os.path.join(config.DATA_DIR, file_name)):
                file_name = f"{youtube_id.video_id}_{counter}.json"
                counter += 1

            file_path = os.path.join(config.DATA_DIR, file_name)
            try:
                with open(file_path, 'w') as file:
                    file.write(json_str)
                    print(f"JSON dump {file_name}")
            except Exception as e:
                print(f"JSON dump failed: {e}.")
                raise e

    @classmethod
    def download_url(cls, url: str) -> YoutubeId:
        youtube_video = pytube.YouTube(url)
        video_id = str(pytube.extract.video_id(url))
        mp3 = os.path.join(config.DATA_DIR, f"{video_id}.mp3")
        mp4 = os.path.join(config.DATA_DIR, f"{video_id}.mp4")

        youtube_id = YoutubeId(title=youtube_video.title.strip(),
                               url=url, video_id=video_id, file_path=mp3)
        if not os.path.exists(mp3):
            try:
                streams = youtube_video.streams.filter(only_audio=False)
                _ = streams.first().download(filename=mp4)
            except Exception as e:
                print(f"Download failed: {e}.")
                raise e
            cls.mp4_to_mp3(youtube_id)

        return youtube_id

    @classmethod
    def transcribe_mp3(cls, youtube_id: YoutubeId) -> YoutubeId:
        audio = AudioSegment.from_mp3(youtube_id.file_path)
        dBFS = audio.dBFS
        silence_segments = silence.detect_silence(
            audio, min_silence_len=config.SILENCE_LENGTH, silence_thresh=dBFS-16)
        n = len(silence_segments)
        print(f"{n} audio segments: {str(silence_segments)}")

        transcriptions = []
        start = 0
        for i in range(n):
            print(f"Process audio segment {str(i)}/{str(n)} ... ")
            stop = silence_segments[i][0]
            text = cls.audio_segment_to_text(audio[start:stop])
            transcriptions.append(Segment(start=start, stop=stop, text=text))
            start = silence_segments[i][1]

        if start < len(audio):
            text = cls.audio_segment_to_text(audio[start:])
            transcriptions.append(
                Segment(start=start, stop=len(audio), text=text))

        youtube_id.transcript = transcriptions
        if config.DELETE_FILES:
            os.remove(youtube_id.file_path)
        return youtube_id

    @staticmethod
    def mp4_to_mp3(youtube_id: YoutubeId):
        mp3 = os.path.join(config.DATA_DIR, f"{youtube_id.video_id}.mp3")
        mp4 = os.path.join(config.DATA_DIR, f"{youtube_id.video_id}.mp4")
        try:
            video = VideoFileClip(mp4)
            audio = video.audio
            audio.write_audiofile(mp3)
        except Exception as e:
            print(f"MP4 to MP3 conversion failed: {e}.")
            raise e
        os.remove(mp4)

    @staticmethod
    def audio_segment_to_text(audio_segment: Any) -> str:
        print(f"Export audio segment.")
        tmp = "./temp.mp3"
        audio_segment.export(tmp)
        audio_file = open(tmp, "rb")
        print(f"Transcribe audio segment.")
        try:
            transcription = client.audio.transcriptions.create(
                model=config.WHISPER_MODEL,
                file=audio_file
            )
        except Exception as e:
            print(f"OpenAI transcription failed: {e}.")
            raise e
        os.remove(tmp)
        return transcription.text


YouTubeTranscriber.transcribe(
    ["https://www.youtube.com/watch?v=7DfXKkvjW-E&ab_channel=MarquesBrownlee"])
