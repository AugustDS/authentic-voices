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
    GPT_MODEL: str = os.environ.get("GPT_MODEL", 'gpt-4-turbo')
    PROMPT: str = os.environ.get("PROMPT", ("You are an expert on extracting information from YouTube review video transcriptions. "
                                            "For each product find the best fitting review aspects which should be some broad "
                                            "product dimension (e.g. design, performance, user experience). For each aspect extract "
                                            "the actual review points according to the provided schema. The title of the video is "
                                            "{title}, with author {author} and trancrsiption {transcription}."))
    PROMPT_MATCH: str = os.environ.get("PROMPT", ("Decide whether the following two review aspects can be aggregated. "
                                                  "If true it means they target the same or a very similar product aspect. "
                                                  "If the aspects are not identical, return the best fitting name for the aggregated aspect. "
                                                  "First aspect: {aspect_1}. Second aspect: {aspect_2}."))
    USE_EXAMPLE: bool = os.environ.get("USE_EXAMPLE", True)
    EXAMPLE_TRANSCRIPT: str = os.environ.get(
        "EXAMPLE_TRANSCRIPT", "./data/example_transcript.json")
    EXAMPLE_REVIEW: str = os.environ.get(
        "EXAMPLE_REVIEW", "./data/example_review.json")
    MIN_SEGMENT_LENGTH: int = os.environ.get("MIN_SEGMENT_LENGTH", 5000)
    DUPLICATE_REVIEWS: bool = os.environ.get("DUPLICATE_REVIEWS", False)
    MAX_ATTEMPTS: int = os.environ.get("MAX_ATTEMPTS", 3)
