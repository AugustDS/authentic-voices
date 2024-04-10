import os
import ast

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    OPENAI_KEY: str = os.environ.get("OPENAI_KEY", "")
    DATA_DIR: str = os.environ.get(
        "DATA_DIR", "")
    DELETE_FILES: bool = os.environ.get("DELETE_FILES", False)
    SILENCE_LENGTH: int = os.environ.get("SILENCE_LENGTH", 1000)
    WHISPER_MODEL: str = os.environ.get("WHISPER_MODEL", 'whisper-1')
