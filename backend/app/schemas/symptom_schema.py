from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional


class SymptomRequest(BaseModel):

    model_config = ConfigDict(extra="forbid")

    symptoms: str = Field(
        min_length=3,
        max_length=1000,
        description="Symptoms reported by the user"
    )

    duration: Optional[str] = None

    severity: Optional[str] = None


class Condition(BaseModel):

    name: str = Field(description="Potential health condition")

    explanation: str = Field(
        description="Why this condition may be relevant"
    )

    symptoms_matched: List[str] = Field(
        description="Symptoms reported by the user that match this condition"
    )


class SymptomAnalysis(BaseModel):

    possible_conditions: List[Condition]

    recommended_next_step: str

    disclaimer: str