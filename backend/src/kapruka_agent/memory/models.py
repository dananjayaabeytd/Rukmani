"""What a remembered fact about a customer looks like."""

from typing import Literal

from pydantic import BaseModel, Field

Category = Literal["recipient", "occasion", "preference", "customer", "other"]


class ExtractedFact(BaseModel):
    """A fact the extraction model found in the latest exchange."""

    text: str = Field(
        description='One short fact in English, e.g. "Customer\'s mother Kamala lives in Kandy".'
    )
    category: Category = Field(
        description="recipient (a person they buy for), occasion (a date/event), "
        "preference (likes, dislikes, budget), customer (about the customer), other"
    )
    explicit: bool = Field(
        default=False,
        description='True if the customer explicitly asked to remember it ("remember...").',
    )


class ExtractionResult(BaseModel):
    """The extraction model's answer: zero or more new facts."""

    facts: list[ExtractedFact] = Field(default_factory=list)


class MemoryFact(BaseModel):
    """A fact kept in long-term memory for one visitor."""

    id: str
    text: str
    category: Category = "other"
    mentions: int = 1  # how many times it came up — repeated facts matter more
    explicit: bool = False  # the customer asked us to remember it
    created_at: float  # epoch seconds
    last_seen_at: float  # epoch seconds, updated each time it comes up again
