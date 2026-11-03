import re
from rapidfuzz import process, fuzz


SYMPTOM_VOCABULARY = [
    "headache",
    "fever",
    "cough",
    "fatigue",
    "body pain",
    "nausea",
    "vomiting",
    "dizziness",
    "sore throat",
    "chest pain",
    "shortness of breath",
    "runny nose",
    "stomach pain",
    "diarrhea"
]


def preprocess_symptoms(text: str):

    if not text or not text.strip():
        raise ValueError("Please enter your symptoms.")

    cleaned = text.lower().strip()

    cleaned = re.sub(
        r"[^\w\s]",
        " ",
        cleaned
    )

    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned
    )

    words = cleaned.split()

    processed_words = []

    for word in words:

        match = process.extractOne(
            word,
            SYMPTOM_VOCABULARY,
            scorer=fuzz.ratio,
            score_cutoff=90
        )

        if match:
            processed_words.append(match[0])
        else:
            processed_words.append(word)

    normalized = " ".join(processed_words)

    return normalized