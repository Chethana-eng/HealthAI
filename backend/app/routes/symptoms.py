import hashlib
import json

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


router = APIRouter(
    prefix="/api/v1",
    tags=["HealthAI"]
)


@router.post("/analyze")
def analyze_symptoms(request: SymptomRequest):

    try:

        # 1. Normalize input

        normalized = preprocess_symptoms(
            request.symptoms
        )

        # 2. Emergency screening

        if check_emergency(normalized):

            return get_emergency_response()

        # 3. Generate a context-specific cache key

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
            cache_string.encode()
        ).hexdigest()

        # 4. Check cache

        cached_result = get_cached_result(cache_key)

        if cached_result is not None:

            return {
                "status": "success",
                "source": "cache",
                "normalized_symptoms": normalized,
                "data": cached_result
            }

        # 5. Call Gemini

        result = analyze_with_gemini(
            symptoms=normalized,
            duration=request.duration or "Not specified",
            severity=request.severity or "Not specified"
        )

        # 6. Cache successful response

        set_cached_result(
            cache_key,
            result
        )

        return {
            "status": "success",
            "source": "gemini",
            "normalized_symptoms": normalized,
            "data": result
        }

    except ValueError as error:

        raise HTTPException(
            status_code=422,
            detail=str(error)
        )

    except Exception:

        raise HTTPException(
            status_code=503,
            detail=(
                "HealthAI is temporarily unable to "
                "process your request. Please try again."
            )
        )