import os
import pytube
import certifi

from typing import Any, List
from openai import OpenAI
from pydub import AudioSegment, silence
from moviepy.video.io.VideoFileClip import VideoFileClip

from models import Segment, YoutubeTranscript
from config import Config
from helper import tiktoken_len, dump_json

config = Config()
client = OpenAI(api_key=config.OPENAI_KEY)


class YouTubeTranscriber:

    @classmethod
    def transcribe(cls, urls:  List[str]):
        for url in urls:
            youtube_transcript = cls.transcribe_mp3(cls.download_url(url))
            token_size = sum(
                [x.token_size for x in youtube_transcript.transcripts])
            youtube_transcript.token_size = token_size

            dump_json(name=youtube_transcript.video_id + "_transcript", dir=config.DATA_DIR,
                      json_str=youtube_transcript.model_dump_json())

    @classmethod
    def download_url(cls, url: str) -> YoutubeTranscript:
        os.environ['SSL_CERT_FILE'] = certifi.where()
        youtube_video = pytube.YouTube(url)
        video_id = str(pytube.extract.video_id(url))
        mp3 = os.path.join(config.DATA_DIR, f"{video_id}.mp3")
        mp4 = os.path.join(config.DATA_DIR, f"{video_id}.mp4")

        youtube_transcript = YoutubeTranscript(title=youtube_video.title.strip(),
                                               author=str(
                                                   youtube_video.author),
                                               url=url,
                                               video_id=video_id,
                                               date=str(
                                                   youtube_video.publish_date),
                                               file_path=mp3)
        if not os.path.exists(mp3):
            try:
                streams = youtube_video.streams.filter(only_audio=False)
                _ = streams.first().download(filename=mp4)
            except Exception as e:
                print(f"Download failed: {e}.")
                raise e
            cls.mp4_to_mp3(youtube_transcript)
        else:
            print(f"Audio file already exists.")
        return youtube_transcript

    @classmethod
    def transcribe_mp3(cls, youtube_transcript: YoutubeTranscript) -> YoutubeTranscript:
        audio = AudioSegment.from_mp3(youtube_transcript.file_path)
        dBFS = audio.dBFS
        silence_segments = silence.detect_silence(
            audio, min_silence_len=config.SILENCE_LENGTH, silence_thresh=dBFS-16)
        audio_segments = cls.transform_segments(silence_segments, len(audio))
        n = len(audio_segments)
        print(f"{n} audio segments: {str(audio_segments)}")

        transcripts = []
        for i in range(n):
            print(f"Process audio segment {str(i)}/{str(n)} ... ")
            start, stop = audio_segments[i][0], audio_segments[i][1]
            text = cls.audio_segment_to_text(audio[start:stop])
            transcripts.append(
                Segment(start=start, stop=stop, text=text, token_size=tiktoken_len(text)))

        youtube_transcript.transcripts = transcripts
        if config.DELETE_FILES:
            os.remove(youtube_transcript.file_path)
        return youtube_transcript

    @staticmethod
    def transform_segments(silence_segments: List[List[int]], audio_length: int) -> List[List[int]]:
        """"from silence_segments to audio_segments"""
        segments = []
        start = 0
        for i in range(len(silence_segments)):
            stop = silence_segments[i][0]
            if stop-start >= config.MIN_SEGMENT_LENGTH:
                segments.append([start, stop])
                start = silence_segments[i][1]
        segments.append([start, audio_length])
        return segments

    @staticmethod
    def mp4_to_mp3(youtube_video: YoutubeTranscript):
        mp3 = os.path.join(config.DATA_DIR, f"{youtube_video.video_id}.mp3")
        mp4 = os.path.join(config.DATA_DIR, f"{youtube_video.video_id}.mp4")
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
