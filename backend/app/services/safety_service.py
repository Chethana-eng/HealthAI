
import re

EMERGENCY_KEYWORDS = [
    "severe chest pain",
    "chest pain",
    "difficulty breathing",
    "difficulty in breathing",
    "shortness of breath",
    "trouble breathing",
    "cannot breathe",
    "can't breathe",
    "unable to breathe",
    "not able to breathe",
    "gasping for air",
    "unconscious",
    "unresponsive",
    "severe bleeding",
    "heavy bleeding",
    "stroke symptoms",
    "face drooping",
    "sudden weakness",
    "sudden numbness"
]


def check_emergency(symptoms: str) -> bool:

    text = symptoms.lower().strip()

    # Normalize punctuation and extra spaces
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    text = re.sub(r"\s+", " ", text)

    for keyword in EMERGENCY_KEYWORDS:

        if keyword in text:
            return True

    return False


def get_emergency_response():

    return {
        "status": "emergency",
        "message": (
            "Your reported symptoms may indicate a "
            "medical emergency. Please contact local "
            "emergency services or seek immediate medical "
            "attention. Do not wait for an AI assessment."
        )
    }
