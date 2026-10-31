# 🧠 AI4Brain – Cognitive Growth Agent
### CISTAC 1.0 – AI4Brain Challenge

AI4Brain is a non-clinical cognitive growth agent that assesses, understands, and supports users through an uncertainty-aware Brain Twin, explainable AI coaching, and personalized adaptive learning.

## Key Features

- **Cognitive Assessment:** Evaluates five dimensions: working memory, attention, processing speed, logical reasoning, and mental flexibility.
- **Dynamic Brain Twin:** Uses Bayesian skill estimation, SQLite history, and 95% credible intervals to track progress over time.
- **Explainable AI Coach:** Provides personalized feedback and explains why each exercise is recommended. Supports rule-based coaching and optional LLM integration.
- **Adaptive Learning:** Adjusts exercise difficulty and generates personalized learning plans based on user performance.
- **Interactive Dashboard:** Displays cognitive radar charts, progress curves, heatmaps, goals, and behavioral indicators.
- **AI Collaboration Score:** Measures clarification, critical verification, iteration, autonomy, and responsible AI use.
- **Interactive Activities:** Includes memory, attention, reasoning, visual-spatial, reading, writing, and focus activities.
- **Accessibility & Support:** Offers personalized activities, adjustable support levels, calm mode, hints, breaks, and optional voice features.

## System Architecture

| Component | Main files | Purpose |
|---|---|---|
| Assessment & profiling | `tasks.py`, `engine.py` | Cognitive tasks, scoring, and behavioral indicators |
| Brain Twin | `engine.py` | Bayesian profile, historical data, and uncertainty |
| AI Coach | `coach.py` | Personalized and explainable feedback |
| Adaptive learning | `engine.py`, `practice.py` | Difficulty adjustment and learning plans |
| Dashboard | `app.py` | Progress visualization and goals |
| AI Collaboration Score | `collab.py` | Human–AI collaboration evaluation |
| Activities | `games_content.py`, `visual_games.py`, `support_content.py`, `focus_content.py`, `literacy.py` | Interactive learning activities |
| Validation | `simulate.py` | Simulation-based evaluation |

## Cognitive Dimensions

| Dimension | Example task |
|---|---|
| Working Memory | Digit sequence |
| Attention | Stroop colour task |
| Processing Speed | Quick arithmetic |
| Logical Reasoning | Number series |
| Mental Flexibility | Colour-cued rule switching |

## Brain Twin & Scoring

The Brain Twin estimates skill using Bayesian updating:

```text
P(success) = chance + (1 - chance) × sigmoid((skill - difficulty) / 12)
```

After each exercise, the model updates the skill estimate and its 95% credible interval. The adaptive engine selects a difficulty targeting approximately 75% expected success.

## AI Collaboration Score

The score combines five dimensions:

| Dimension | Weight |
|---|---:|
| Clarification | 20% |
| Critical verification | 25% |
| Iteration | 20% |
| Autonomy | 20% |
| Responsible AI use | 15% |

## Experimental Validation

Simulation-based evaluation with virtual users:

| Learning strategy | Mean absolute error | 95% interval coverage |
|---|---:|---:|
| Adaptive learning | 8.4 | 87% |
| Fixed level | 9.3 | 93% |
| Random level | 12.0 | 87% |

These results are obtained from simulated users.

## Ethics & Privacy

- Non-clinical purpose: the platform supports learning and cognitive development, not diagnosis.
- User consent before data storage.
- Local SQLite storage and pseudonymous profiles.
- User options to export and delete profile data.
- Automatic data deletion after 90 days.
- Non-biometric behavioral indicators based on interaction logs.
- Optional self-reported mood; no decisions based solely on face or voice.
- Support profiles personalize activities and do not diagnose or infer a condition.

## Technologies

Python · Streamlit · SQLite · Bayesian modeling · Plotly · Pytest · Ollama (optional) · Anthropic API (optional) · Faster-Whisper (optional)

## Installation & Execution

```bash
git clone https://github.com/YOUR-USERNAME/AI4Brain.git
cd AI4Brain

python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
pip install -r requirements-voice.txt  # Optional
streamlit run app.py
```

Run tests and simulation:

```bash
pytest -q
python simulate.py
```

The simulation report is generated in the `validation/` directory.

## Repository Structure

```text
AI4Brain/
├── app.py
├── engine.py
├── coach.py
├── collab.py
├── tasks.py
├── tasks_custom.py
├── practice.py
├── simulate.py
├── games_content.py
├── visual_games.py
├── support_content.py
├── focus_content.py
├── literacy.py
├── autism_content.py
├── dyslexia_content.py
├── tests/
├── validation/
├── requirements.txt
└── requirements-voice.txt
```

## Challenge

**CISTAC 1.0 – AI4Brain: Cognitive Growth Agent**

**Project:** AI4Brain – Cognitive Growth Agent  
**Domain:** Artificial Intelligence · Cognitive Computing · Adaptive Learning
