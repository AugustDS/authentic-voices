import instructor

from openai import OpenAI
from typing import List

from config import Config
from models import YoutubeTranscript, Review
from helper import load_json, dump_json

config = Config()
client = instructor.patch(
    OpenAI(api_key=config.OPENAI_KEY), mode=instructor.Mode.MD_JSON)


class ReviewExtractor:

    @classmethod
    def run(cls, file_path: str):
        youtube_transcript = cls.load_transcript(file_path)
        messages = cls.create_message(youtube_transcript)
        response = cls.extract_review(messages)
        dump_json(name=youtube_transcript.video_id+"_review",
                  dir=config.DATA_DIR, json_str=response.model_dump_json())

    @classmethod
    def create_message(cls, youtube_transcript: YoutubeTranscript):
        messages = []

        if config.USE_EXAMPLE:
            print("Create example messages.")
            example_video = cls.load_transcript(config.EXAMPLE_TRANSCRIPT)
            example_prompt = cls.create_prompt(example_video)
            example_resp = cls.load_review(config.EXAMPLE_REVIEW)
            messages.append({"role": "user",
                            "content": example_prompt})
            messages.append({"role": "assistant",
                            "content": example_resp.model_dump_json()})

        print("Create new message.")
        prompt = cls.create_prompt(youtube_transcript)
        messages.append({"role": "user",
                        "content": prompt})
        return messages

    @staticmethod
    def extract_review(messages: List[dict]) -> Review:
        print("Run LLM.")
        try:
            resp = client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=messages,
                response_model=Review,
            )
        except Exception as e:
            print(f"LLM call failed: {e}.")
            raise e
        return resp

    @staticmethod
    def create_prompt(youtube_transcript: YoutubeTranscript) -> str:
        text = " ".join([x.text for x in youtube_transcript.transcripts])
        content = config.PROMPT.format(
            title=youtube_transcript.title, author=youtube_transcript.author, transcription=text)
        return content

    @staticmethod
    def load_review(file_path: str) -> Review:
        return Review.model_validate_json(load_json(file_path))

    @staticmethod
    def load_transcript(file_path: str) -> YoutubeTranscript:
        return YoutubeTranscript.model_validate_json(
            load_json(file_path))
