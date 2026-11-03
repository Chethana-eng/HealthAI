
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/v1/analyze";

function App() {
  const [symptoms, setSymptoms] = useState("");
  const [duration, setDuration] = useState("");
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const analyzeSymptoms = async (e) => {
    e.preventDefault();

    if (symptoms.trim().length < 3) {
      setError("Please enter at least 3 characters describing your symptoms.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          symptoms: symptoms.trim(),
          duration: duration || null,
          severity: severity || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to analyze symptoms. Please try again."
        );
      }

      setResult(data);
    } catch (err) {
      setError(
        err.message === "Failed to fetch"
          ? "Cannot connect to HealthAI. Please check whether the backend is running."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  };

  const analysis = result?.data || result;
  const conditions = analysis?.possible_conditions || [];

  const isEmergency =
    result?.status === "emergency" ||
    result?.status === "urgent" ||
    result?.emergency === true;

  return (
    <div className="app">
      <nav className="navbar">
        <div className="brand">
          <div className="brand-icon">H+</div>
          <span>HealthAI</span>
        </div>
        <span className="nav-label">AI-Powered Health Insights</span>
      </nav>

      <main className="container">
        <section className="hero">
          <span className="eyebrow">INTELLIGENT SYMPTOM ASSESSMENT</span>
          <h1>
            Understand your health.
            <br />
            <span>Make informed decisions.</span>
          </h1>
          <p>
            Describe how you're feeling and let our AI-powered assistant
            provide preliminary health insights.
          </p>
        </section>

        <section className="assessment-card">
          <div className="section-heading">
            <div>
              <span className="step-label">01 / ASSESSMENT</span>
              <h2>Tell us how you're feeling</h2>
              <p>Provide details about your symptoms below.</p>
            </div>
            <div className="form-icon">✚</div>
          </div>

          <form onSubmit={analyzeSymptoms}>
            <label htmlFor="symptoms">Describe your symptoms *</label>
            <textarea
              id="symptoms"
              placeholder="Example: I have been experiencing a headache, mild fever and fatigue..."
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              maxLength={1000}
              required
            />
            <div className="character-count">
              {symptoms.length}/1000 characters
            </div>

            <div className="form-row">
              <div>
                <label htmlFor="duration">How long have you experienced this?</label>
                <select
                  id="duration"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                >
                  <option value="">Select duration</option>
                  <option value="Less than a day">Less than a day</option>
                  <option value="1-3 days">1–3 days</option>
                  <option value="4-7 days">4–7 days</option>
                  <option value="1-2 weeks">1–2 weeks</option>
                  <option value="More than 2 weeks">More than 2 weeks</option>
                </select>
              </div>

              <div>
                <label htmlFor="severity">How severe are your symptoms?</label>
                <select
                  id="severity"
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                >
                  <option value="">Select severity</option>
                  <option value="Mild">Mild</option>
                  <option value="Moderate">Moderate</option>
                  <option value="Severe">Severe</option>
                </select>
              </div>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Analyzing your symptoms..." : "Analyze My Symptoms →"}
            </button>
          </form>

          <div className="privacy-note">
            <span>🔒</span>
            Your symptoms are processed to generate preliminary insights.
          </div>
        </section>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <h3>Analyzing your symptoms</h3>
            <p>HealthAI is processing your information...</p>
          </div>
        )}

        {error && (
          <div className="error-message">
            <strong>Something went wrong</strong>
            <p>{error}</p>
          </div>
        )}

        {result && !isEmergency && (
          <section className="results">
            <div className="results-heading">
              <span className="step-label">02 / AI ANALYSIS</span>
              <h2>Preliminary health insights</h2>
              <span className="source">
                {result.source === "cache" ? "⚡ Cached result" : "✦ Gemini AI"}
              </span>
            </div>

            {conditions.length > 0 ? (
              <div className="condition-grid">
                {conditions.map((condition, index) => (
                  <article className="condition-card" key={index}>
                    <span className="condition-number">
                      POSSIBLE CONDITION 0{index + 1}
                    </span>
                    <h3>{condition.name}</h3>
                    <p>{condition.explanation}</p>

                    {condition.symptoms_matched?.length > 0 && (
                      <div className="matched">
                        <strong>Matching symptoms</strong>
                        <div className="tags">
                          {condition.symptoms_matched.map((symptom, i) => (
                            <span key={i}>{symptom}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </article>
                ))}
              </div>
            ) : (
              <p className="error-message">
                No condition details were returned. Please try again.
              </p>
            )}

            {analysis?.recommended_next_step && (
              <div className="next-step">
                <h3>Recommended next step</h3>
                <p>{analysis.recommended_next_step}</p>
              </div>
            )}

            <div className="disclaimer">
              <strong>Important medical disclaimer</strong>
              <p>
                {analysis?.disclaimer ||
                  "These results are AI-generated preliminary insights, not a medical diagnosis. Consult a qualified healthcare professional for medical advice."}
              </p>
            </div>
          </section>
        )}

        {isEmergency && (
          <div className="emergency">
            <h2>Urgent medical attention may be needed</h2>
            <p>
              {result.message ||
                result.detail ||
                "Your symptoms may require immediate medical assessment. Please seek emergency medical care."}
            </p>
            <strong>
              Do not rely on this application for emergency medical care.
            </strong>
          </div>
        )}
      </main>

      <footer>
        <strong>HealthAI</strong> · AI-assisted preliminary health insights
        <p>Not a substitute for professional medical evaluation.</p>
      </footer>
    </div>
  );
}

export default App;
