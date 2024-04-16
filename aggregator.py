import instructor
import os
import re

from openai import OpenAI
from typing import List

from config import Config
from models import Review, YoutubeTranscript, AggregatedReview, AggregatedReviewAspect, AggregatedReviewPoint, MatchedAspects
from helper import load_json, dump_json, matching_files

config = Config()
client = instructor.patch(
    OpenAI(api_key=config.OPENAI_KEY), mode=instructor.Mode.MD_JSON)


class ReviewAggregator:
    @classmethod
    def run(cls, product_name: str):
        dir = os.path.join(config.DATA_DIR, product_name)
        agr_files = matching_files(dir, "aggregated.json")
        review_files = matching_files(dir, "review.json")

        if len(agr_files) > 0:
            print(f"Aggregated review loaded from {agr_files[0]}")
            agr_review = AggregatedReview.model_validate_json(
                load_json(agr_files[0]))
        else:
            print(f"New aggregation.")
            agr_review = cls.load_and_transform(review_files.pop(0))

        for path in review_files:
            new_review = cls.load_and_transform(path)
            title = new_review.reviews[0].reviewPoints[0].vidTitle
            print(f"Merge aggregated reviews with reviews from {title}.")
            agr_review = cls.aggregate(agr_review, new_review)
        dump_json(name="aggregated", dir=dir,
                  json_str=agr_review.model_dump_json())

    @staticmethod
    def load_and_transform(file_path: str) -> AggregatedReview:
        """Add video information to review points for later identification"""
        transcript = YoutubeTranscript.model_validate_json(
            load_json(file_path.replace("_review", "_transcript")))
        review = Review.model_validate_json(load_json(file_path))
        agr_reviews = []
        for orig_review in review.reviews:
            agr_review_points = []
            for orig_review_point in orig_review.reviewPoints:
                agr_review_point = AggregatedReviewPoint(title=orig_review_point.title,
                                                         point=orig_review_point.point,
                                                         quotation=orig_review_point.quotation,
                                                         sentiment=orig_review_point.sentiment,
                                                         vidAuthor=transcript.author,
                                                         vidId=transcript.video_id,
                                                         vidTitle=transcript.title)
                agr_review_points.append(agr_review_point)
            agr_review_aspect = AggregatedReviewAspect(aspect=orig_review.aspect,
                                                       reviewPoints=agr_review_points)
            agr_reviews.append(agr_review_aspect)

        return AggregatedReview(product=review.product, reviews=agr_reviews)

    @classmethod
    def aggregate(cls, agr_review: AggregatedReview, new_review: AggregatedReview) -> AggregatedReview:
        agr_reviews = agr_review.reviews
        new_reviews = new_review.reviews
        for new_review_aspect in new_reviews:
            for agr_review_aspect in agr_reviews:
                matched_aspect = cls.match_aspects(
                    new_review_aspect.aspect, agr_review_aspect.aspect)
                if matched_aspect.match:
                    print(f"Matched new aspect {new_review_aspect.aspect} to existing aspect {agr_review_aspect.aspect} with combined name {matched_aspect.name}.")
                    agr_review_aspect.reviewPoints += new_review_aspect.reviewPoints
                    agr_review_aspect.aspect = matched_aspect.name
                    break
            else:
                print(f"No match. Adding new aspect {new_review_aspect.aspect}")
                agr_reviews.append(
                    AggregatedReviewAspect(
                        aspect=new_review_aspect.aspect,
                        reviewPoints=new_review_aspect.reviewPoints)
                )
        return AggregatedReview(product=agr_review.product,
                                reviews=agr_reviews)

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
                         "content": MatchedAspects(match=False, name="").model_dump_json()})
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