
import hashlib
import json
import logging
import time

from fastapi import APIRouter, HTTPException

from app.schemas.symptom_schema import SymptomRequest

from app.services.preprocessing import preprocess_symptoms

from app.services.safety_service import (
    check_emergency,
    get_emergency_response
)

from app.services.llm_service import analyze_with_gemini

from app.services.cache_service import (
    get_cached_result,
    set_cached_result
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/v1",
    tags=["HealthAI"]
)


def validate_symptom_input(text: str):

    cleaned = text.strip().lower()

    invalid_inputs = {
        "i have",
        "i am",
        "i'm",
        "im",
        "hello",
        "hi",
        "help",
        "asdfgh",
        "qwerty",
        "test",
        "not sure"
    }

    if cleaned in invalid_inputs:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please describe a specific symptom, "
                "such as headache, fever or nausea."
            )
        )


@router.post("/analyze")
async def analyze_symptoms(request: SymptomRequest):

    request_start = time.perf_counter()

    try:

        # 1. Normalize input

        normalized = preprocess_symptoms(
            request.symptoms
        )

        # 2. Validate input

        validate_symptom_input(normalized)

        # 3. Emergency screening

        if check_emergency(normalized):

            logger.warning(
                "Emergency symptoms detected."
            )

            return get_emergency_response()

        # 4. Generate context-specific cache key

        cache_data = {
            "symptoms": normalized,
            "duration": request.duration or "",
            "severity": request.severity or ""
        }

        cache_string = json.dumps(
            cache_data,
            sort_keys=True
        )

        cache_key = hashlib.sha256(
            cache_string.encode("utf-8")
        ).hexdigest()

        # 5. Check cache

        cached_result = get_cached_result(cache_key)

        if cached_result is not None:

            latency = time.perf_counter() - request_start

            logger.info(
                "Cache hit. Total request latency: %.3f seconds",
                latency
            )

            return {
                "status": "success",
                "source": "cache",
                "normalized_symptoms": normalized,
                "data": cached_result,
                "latency_seconds": round(latency, 3)
            }

        # 6. Call Gemini asynchronously

        result = await analyze_with_gemini(
            symptoms=normalized,
            duration=request.duration or "Not specified",
            severity=request.severity or "Not specified"
        )

        # 7. Cache successful response

        set_cached_result(
            cache_key,
            result
        )

        # 8. Calculate total request latency

        latency = time.perf_counter() - request_start

        logger.info(
            "Gemini request completed. Total latency: %.3f seconds",
            latency
        )

        # 9. Return analysis

        return {
            "status": "success",
            "source": "gemini",
            "normalized_symptoms": normalized,
            "data": result,
            "latency_seconds": round(latency, 3)
        }

    except HTTPException:
        raise

    except ValueError as error:

        logger.exception(
            "Symptom analysis validation error: %s",
            error
        )

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:

        logger.exception(
            "HealthAI analysis failed."
        )

        raise HTTPException(
            status_code=503,
            detail=(
                "HealthAI is temporarily unable to "
                "process your request. Please try again."
            )
        )
