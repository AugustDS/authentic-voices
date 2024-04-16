from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Segment(BaseModel):
    start: int
    stop: int
    token_size: int
    text: str


class YoutubeTranscript(BaseModel):
    title: str
    author: str
    url: str
    video_id: str
    date: str
    file_path: str
    token_size: Optional[int] = None
    transcripts: Optional[List[Segment]] = None


class Sentiment(Enum):
    positive = 'positive'
    negative = 'negative'
    neutral = 'neutral'


class CustomBaseModel(BaseModel):
    class Config:
        json_encoders = {
            Enum: lambda v: v.value,
        }


class ReviewPoint(CustomBaseModel):
    title: str = Field(description="Title for the review point.")
    point: str = Field(description="The review point.")
    quotation: str = Field(
        description="Exact quotation from the text to support the review point.")
    sentiment: Sentiment = Field(
        description="Whether the review point is positive, negative or neutral.")


class ReviewAspect(CustomBaseModel):
    aspect: str = Field(
        description="Aspect of the product that the review points address.")
    reviewPoints: List[ReviewPoint] = Field(
        default_factory=list, description="List of review points extracted from the text that address the aspect.")


class Review(CustomBaseModel):
    product: str = Field(
        description="Name of the product being reviewed.")
    reviews: List[ReviewAspect] = Field(
        default_factory=list, description="List of review aspects extracted from the text.")


class AggregatedReviewPoint(CustomBaseModel):
    title: str = Field(description="Title for the review point.")
    point: str = Field(description="The review point.")
    quotation: str = Field(
        description="Exact quotation from the text to support the review point.")
    sentiment: Sentiment = Field(
        description="Whether the review point is positive, negative or neutral.")
    vidAuthor: Optional[str]
    vidId: Optional[str]
    vidTitle: Optional[str]


class AggregatedReviewAspect(CustomBaseModel):
    aspect: str = Field(
        description="Aspect of the product that the review points address.")
    reviewPoints: List[AggregatedReviewPoint] = Field(
        default_factory=list, description="List of review points extracted from the text that address the aspect.")


class AggregatedReview(CustomBaseModel):
    product: str = Field(
        description="Name of the product being reviewed.")
    reviews: List[AggregatedReviewAspect] = Field(
        default_factory=list, description="List of review aspects extracted from the text.")


class MatchedAspects(BaseModel):
    match: bool = Field(
        description="If two review aspects match and can be combined to the same aspect.")
    name: str = Field(
        description="Name of the combined/aggregated review aspects.")
