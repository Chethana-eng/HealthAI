
import logging
import time

from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.symptom_schema import SymptomAnalysis

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTIONS = """
You are HealthAI, an AI assistant providing preliminary health information.

You are NOT a doctor and must never provide a definitive diagnosis.

Instructions:
1. Analyze the symptoms provided by the user.
2. Return at least 3 plausible potential conditions when sufficient
   information is available.
3. Explain why each condition could be relevant.
4. Only mention symptoms actually provided by the user.
5. Never invent patient information.
6. Do not provide unsupported probabilities or certainty.
7. Recommend professional medical evaluation.
8. If information is insufficient, clearly communicate uncertainty.
9. Do not provide dangerous medication instructions.
10. Always include a medical disclaimer.

Return a complete JSON response matching the supplied schema.
Do not stop before completing the JSON response.
"""

async def analyze_with_gemini(
    symptoms: str,
    duration="Not specified",
    severity="Not specified"
):
    prompt = f"""
    Analyze the following patient information.

    Symptoms: {symptoms}
    Duration: {duration}
    Severity: {severity}

    Return at least 3 plausible potential conditions.

    Keep explanations concise and complete.
    Ensure the entire response is valid JSON.
    """

    start_time = time.perf_counter()

    try:
        response = await client.aio.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTIONS,
                response_mime_type="application/json",
                response_schema=SymptomAnalysis,
                temperature=0.2,
                max_output_tokens=2500
            )
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        # Log the finish reason to help identify truncation.
        if response.candidates:
            candidate = response.candidates[0]
            logger.info(
                "Gemini finish reason: %s",
                candidate.finish_reason
            )

        try:
            result = SymptomAnalysis.model_validate_json(
                response.text
            )
        except Exception:
            logger.error(
                "Gemini returned invalid or incomplete JSON: %s",
                response.text
            )
            raise ValueError(
                "The AI returned an incomplete response. Please try again."
            )

        if len(result.possible_conditions) < 3:
            raise ValueError(
                "The AI could not identify at least 3 plausible conditions. "
                "Please provide more symptom details."
            )

        return result.model_dump()

    except ValueError:
        raise

    except Exception:
        logger.exception("Gemini API request failed.")
        raise RuntimeError(
            "Gemini analysis service failed."
        )

    finally:
        latency = time.perf_counter() - start_time
        logger.info(
            "Gemini request latency: %.2f seconds",
            latency
        )
