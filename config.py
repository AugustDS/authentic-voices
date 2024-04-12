import os

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    OPENAI_KEY: str = os.environ.get(
        "OPENAI_KEY", "")
    DATA_DIR: str = os.environ.get(
        "DATA_DIR", "./data")
    DELETE_FILES: bool = os.environ.get("DELETE_FILES", False)
    SILENCE_LENGTH: int = os.environ.get("SILENCE_LENGTH", 800)
    WHISPER_MODEL: str = os.environ.get("WHISPER_MODEL", 'whisper-1')
    PROMPT: str = os.environ.get("PROMPT", ("YouTube video title: {title}. "
                                            "Author: {author}. "
                                            "Trancrsiption: {transcription}. "))
    USE_EXAMPLE: bool = os.environ.get("USE_EXAMPLE", True)
    EXAMPLE_TRANSCRIPT: str = os.environ.get(
        "EXAMPLE_TRANSCRIPT", "./data/example_transcript.json")
    EXAMPLE_REVIEW: str = os.environ.get(
        "EXAMPLE_REVIEW", "./data/example_review.json")
    MIN_SEGMENT_LENGTH: int = os.environ.get("MIN_SEGMENT_LENGTH", 5000)
