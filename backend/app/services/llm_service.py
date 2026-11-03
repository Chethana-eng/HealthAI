import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.symptom_schema import SymptomAnalysis


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


SYSTEM_INSTRUCTIONS = """
You are HealthAI, an AI assistant that provides
preliminary health information.

You are NOT a doctor and must NEVER provide a
definitive medical diagnosis.

Your responsibilities:

1. Analyze the symptoms provided by the user.
2. Identify at least three plausible potential
   health conditions when sufficient information
   is available.
3. Explain why each condition may be relevant.
4. Identify which reported symptoms are associated
   with each possibility.
5. Never invent symptoms or patient information.
6. Do not claim certainty or assign unsupported
   probabilities.
7. Recommend appropriate professional medical
   evaluation.
8. If information is insufficient, clearly explain
   the uncertainty and request more information.
9. Never provide dangerous medication instructions.
10. Always clarify that this is not a diagnosis.

Return structured output matching the supplied schema.
"""


def analyze_with_gemini(
    symptoms: str,
    duration: str = "Not specified",
    severity: str = "Not specified"
):

    prompt = f"""
    Patient-reported symptoms: {symptoms}

    Duration: {duration}

    Severity: {severity}

    Provide a cautious preliminary assessment.
    """

    response = client.models.generate_content(

        model=settings.GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM_INSTRUCTIONS,

            response_mime_type="application/json",

            response_schema=SymptomAnalysis,

            temperature=0.2
        )
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response.")

    result = SymptomAnalysis.model_validate_json(
        response.text
    )

    if len(result.possible_conditions) < 3:
        raise ValueError(
            "The model returned insufficient conditions."
        )

    return result.model_dump()