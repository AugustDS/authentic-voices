import instructor

from openai import OpenAI
from typing import List

from config import Config
from models import YoutubeTranscript, Review, ReviewAspect, MatchedAspects
from helper import load_json, dump_json

config = Config()
client = instructor.patch(
    OpenAI(api_key=config.OPENAI_KEY), mode=instructor.Mode.MD_JSON)


class ReviewAggregator:
    @classmethod
    def aggregate(cls, agr_reviews: List[ReviewAspect], new_reviews: List[ReviewAspect]) -> List[ReviewAspect]:
        mgd_reviews = []
        for new_review_aspect in new_reviews:
            for agr_review_aspect in agr_reviews:
                matched_aspect = cls.match_aspects(
                    new_review_aspect.aspect, agr_review_aspect.aspect)
                if matched_aspect.match:
                    print(
                        f"Matched new aspect {new_review_aspect.aspect} to existing aspect {agr_review_aspect.aspect} with combined name {matched_aspect.name}.")
                    mgd_reviews.append(
                        ReviewAspect(
                            aspect=matched_aspect.name,
                            reviewPoints=agr_review_aspect.reviewPoints + new_review_aspect.reviewPoints
                        )
                    )
                    continue
            else:
                print(
                    f"No match. Adding new aspect {new_review_aspect.aspect}")
                mgd_reviews.append(
                    ReviewAspect(
                        aspect=new_review_aspect.aspect,
                        reviewPoints=new_review_aspect.reviewPoints)
                )
        return mgd_reviews

    @staticmethod
    def match_aspects(aspect_1: str, aspect_2: str) -> MatchedAspects:
        messages = []
        # Example 1
        messages.append({"role": "user",
                         "content": config.PROMPT_MATCH.format(
                             aspect_1="Price", aspect_2="Cost")})
        messages.append({"role": "assistant",
                         "content": MatchedAspects(match=True, name="Price").model_dump_json()})
        # Example 2
        messages.append({"role": "user",
                         "content": config.PROMPT_MATCH.format(
                             aspect_1="Design", aspect_2="Performance")})
        messages.append({"role": "assistant",
                         "content": MatchedAspects(match=False).model_dump_json()})
        # Example 3
        messages.append({"role": "user",
                         "content": config.PROMPT_MATCH.format(
                             aspect_1="Camera", aspect_2="Camera")})
        messages.append({"role": "assistant",
                         "content": MatchedAspects(match=True, name="Camera").model_dump_json()})
        # Message
        messages.append({"role": "user",
                         "content": config.PROMPT_MATCH.format(
                             aspect_1=aspect_1, aspect_2=aspect_2)})
        try:
            resp = client.chat.completions.create(
                model=config.GPT_MODEL,
                messages=messages,
                response_model=MatchedAspects,
            )
            return resp
        except Exception as e:
            print(f"LLM call failed: {e}.")
            raise e

    @staticmethod
    def load_review(file_path: str) -> Review:
        return Review.model_validate_json(load_json(file_path))

    @staticmethod
    def load_transcript(file_path: str) -> YoutubeTranscript:
        return YoutubeTranscript.model_validate_json(
            load_json(file_path))
