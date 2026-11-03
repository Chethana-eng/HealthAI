
from pydantic import BaseModel, Field
from typing import List, Optional


class SymptomRequest(BaseModel):

    symptoms: str = Field(
        min_length=3,
        max_length=1000
    )

    duration: Optional[str] = None

    severity: Optional[str] = None


class Condition(BaseModel):

    name: str

    explanation: str

    symptoms_matched: List[str]


class SymptomAnalysis(BaseModel):

    possible_conditions: List[Condition]

    recommended_next_step: str

    disclaimer: str