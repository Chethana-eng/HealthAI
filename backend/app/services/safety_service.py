EMERGENCY_KEYWORDS = [
    "severe chest pain",
    "difficulty breathing",
    "shortness of breath",
    "unconscious",
    "severe bleeding",
    "stroke symptoms"
]


def check_emergency(symptoms: str):

    text = symptoms.lower()

    for keyword in EMERGENCY_KEYWORDS:

        if keyword in text:
            return True

    return False


def get_emergency_response():

    return {
        "status": "emergency",
        "message": (
            "Your reported symptoms may require "
            "urgent medical attention. Please contact "
            "local emergency services or seek immediate "
            "medical care. Do not wait for an AI assessment."
        )
    }