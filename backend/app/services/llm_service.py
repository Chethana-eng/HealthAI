
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.symptom_schema import SymptomAnalysis


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


SYSTEM_INSTRUCTIONS = """
You are HealthAI, an AI assistant providing
preliminary health information.

You are NOT a doctor and must NEVER provide
a definitive medical diagnosis.

Responsibilities:

1. Analyze only the symptoms reported by the user.
2. Identify up to three plausible conditions.
3. Do not invent symptoms or patient information.
4. Explain uncertainty when information is insufficient.
5. Never assign unsupported probabilities.
6. Never prescribe medication or dosage.
7. Recommend appropriate professional evaluation.
8. Identify warning signs requiring urgent care.
9. Always include a medical disclaimer.

Return structured output matching the supplied schema.
"""


def analyze_with_gemini(
    symptoms: str,
    duration: str = "Not specified",
    severity: str = "Not specified"
):

    if not settings.GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing.")

    prompt = f"""
    Patient-reported symptoms: {symptoms}

    Duration: {duration}

    Severity: {severity}

    Provide a cautious preliminary assessment.
    Do not invent missing information.
    If information is insufficient, explain why.
    """

    try:

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
            raise ValueError(
                "Gemini returned an empty response."
            )

        result = SymptomAnalysis.model_validate_json(
            response.text
        )

        return result.model_dump()

    except ValueError:
        raise

    except Exception as error:
        raise RuntimeError(
            "Gemini analysis service failed."
        ) from error
