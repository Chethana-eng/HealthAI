# HealthAI

A patient symptom checker built using React, FastAPI and Google Gemini.

HealthAI takes symptoms described in natural language and uses an LLM to generate possible health conditions, explain why they may be relevant, and suggest appropriate next steps.

**Note:** This is an informational prototype, not a medical diagnostic tool.

## What I built

- A React interface for entering symptoms, duration and severity.
- A FastAPI backend to process requests and communicate with Gemini.
- Symptom preprocessing to normalize user input.
- Emergency keyword screening before AI analysis.
- Structured JSON responses validated using Pydantic.
- In-memory caching to avoid repeated API calls.
- Error handling for invalid inputs and temporary Gemini failures.

## How it works

```text
User Input
    ↓
React Frontend
    ↓
FastAPI Backend
    ↓
Input Validation & Preprocessing
    ↓
Emergency Screening
    ↓
Cache Lookup
    ↓
Gemini API (on cache miss)
    ↓
Pydantic Response Validation
    ↓
Result Returned to Frontend
```

## Tech Stack

- **Frontend:** React
- **Backend:** Python, FastAPI
- **LLM:** Google Gemini
- **Validation:** Pydantic
- **Caching:** cachetools
- **Testing:** pytest

## Project Structure

```text
HealthAI/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
└── README.md
```

## Running locally

**1. Clone the repository**

```bash
git clone YOUR_REPOSITORY_URL
cd HealthAI
```

**2. Set up the backend**

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=your_model_name
```

Run the server:

```bash
uvicorn app.main:app --reload
```

Backend API: `http://127.0.0.1:8000`

API docs: `http://127.0.0.1:8000/docs`

**3. Set up the frontend**

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL provided by Vite.

## API

`POST /api/v1/analyze`

Example request:

```json
{
  "symptoms": "Headache and mild fever",
  "duration": "2 days",
  "severity": "Moderate"
}
```

The API returns potential conditions, explanations, matching symptoms, recommended next steps and a disclaimer.

## A few implementation decisions

**Why Gemini?**

A small student-developer decision: I went with Gemini partly because its free tier made experimentation easier on a student budget! More importantly, it let me work with a pretrained LLM and structured JSON responses without building a model from scratch.

**Why caching?**

Identical requests can reuse previously generated results. The current TTL cache holds up to 100 entries for 5 minutes. It is in-memory, so the cache resets when the backend restarts.

**Why Pydantic?**

LLM output is not automatically trustworthy or correctly formatted. Pydantic validates the response against the expected schema before it is returned.

**What about emergency symptoms?**

The backend checks for selected emergency-related keywords before calling Gemini. This is only a basic screening mechanism; it is not comprehensive and cannot determine whether someone is medically safe.

## Testing

Run the backend tests:

```bash
python -m pytest -v
```

The test suite covers the implemented validation, safety, caching and service behavior. See the test files for the exact cases.

## Current limitations

- Gemini responses depend on external API availability and latency.
- AI-generated conditions may be inaccurate or incomplete.
- Emergency keyword matching can miss important symptoms.
- Cache entries are not persistent across restarts.

Possible next steps include Redis caching, stronger input handling, broader safety testing and API rate limiting.

## AI tools used

ChatGPT assistance was used during development for implementation guidance, debugging, Gemini integration and documentation. The generated suggestions were reviewed and adapted while building and testing the application.

---
