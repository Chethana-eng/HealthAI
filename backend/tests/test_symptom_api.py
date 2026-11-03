from fastapi.testclient import TestClient
from unittest.mock import patch
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_invalid_empty_symptoms():

    response = client.post(
        "/api/v1/analyze",
        json={
            "symptoms": ""
        }
    )

    assert response.status_code == 422


def test_invalid_short_symptoms():

    response = client.post(
        "/api/v1/analyze",
        json={
            "symptoms": "hi"
        }
    )

    assert response.status_code == 422


@patch("app.routes.symptoms.analyze_with_gemini")
@patch("app.routes.symptoms.check_emergency")
def test_successful_symptom_analysis(
    mock_emergency,
    mock_gemini
):

    mock_emergency.return_value = False

    mock_gemini.return_value = {
        "possible_conditions": [
            {
                "name": "Gastritis",
                "explanation": "May be associated with stomach discomfort.",
                "symptoms_matched": ["stomach pain"]
            },
            {
                "name": "Acid reflux",
                "explanation": "May cause a burning sensation.",
                "symptoms_matched": ["burning sensation"]
            },
            {
                "name": "Indigestion",
                "explanation": "May cause upper abdominal discomfort.",
                "symptoms_matched": ["stomach discomfort"]
            }
        ],
        "recommended_next_step": "Consult a healthcare professional.",
        "disclaimer": "This is not a medical diagnosis."
    }

    response = client.post(
        "/api/v1/analyze",
        json={
            "symptoms": "burning sensation in stomach",
            "duration": "1-3 days",
            "severity": "Moderate"
        }
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["source"] == "gemini"

    mock_gemini.assert_called_once()


def test_emergency_symptoms_bypass_gemini():

    with patch(
        "app.routes.symptoms.check_emergency"
    ) as mock_emergency, patch(
        "app.routes.symptoms.get_emergency_response"
    ) as mock_response, patch(
        "app.routes.symptoms.analyze_with_gemini"
    ) as mock_gemini:

        mock_emergency.return_value = True

        mock_response.return_value = {
            "status": "emergency",
            "message": "Seek emergency medical care immediately."
        }

        response = client.post(
            "/api/v1/analyze",
            json={
                "symptoms": "severe chest pain and difficulty breathing",
                "duration": "10 minutes",
                "severity": "Severe"
            }
        )

        assert response.status_code == 200

        assert response.json()["status"] == "emergency"

        mock_gemini.assert_not_called()



@patch("app.routes.symptoms.analyze_with_gemini")
@patch("app.routes.symptoms.check_emergency")
@patch("app.routes.symptoms.get_cached_result")
@patch("app.routes.symptoms.set_cached_result")
def test_symptom_result_caching(
    mock_set_cache,
    mock_get_cache,
    mock_emergency,
    mock_gemini
):

    mock_emergency.return_value = False
    mock_get_cache.return_value = None

    mock_gemini.return_value = {
        "possible_conditions": [
            {
                "name": "Gastritis",
                "explanation": "Possible stomach inflammation.",
                "symptoms_matched": ["stomach pain"]
            },
            {
                "name": "Acid reflux",
                "explanation": "Possible acid reflux.",
                "symptoms_matched": ["burning sensation"]
            },
            {
                "name": "Indigestion",
                "explanation": "Possible indigestion.",
                "symptoms_matched": ["stomach discomfort"]
            }
        ],
        "recommended_next_step": "Consult a doctor.",
        "disclaimer": "Not a medical diagnosis."
    }

    payload = {
        "symptoms": "burning sensation in stomach",
        "duration": "1-3 days",
        "severity": "Moderate"
    }

    # First request
    response1 = client.post("/api/v1/analyze", json=payload)

    assert response1.status_code == 200
    assert response1.json()["source"] == "gemini"

    # Second request
    mock_get_cache.return_value = (
        response1.json()["data"]
    )

    response2 = client.post("/api/v1/analyze", json=payload)

    assert response2.status_code == 200
    assert response2.json()["source"] == "cache"

    assert mock_gemini.call_count == 1