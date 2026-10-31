# 🧠 AI4Brain – Cognitive Growth Agent

### CISTAC 1.0 – AI4Brain Technical Challenge

**AI4Brain** is an intelligent, adaptive, and non-clinical cognitive growth platform designed to assess, understand, and enhance cognitive abilities through personalized AI coaching and adaptive learning.

It combines Bayesian cognitive profiling, a dynamic Brain Twin, explainable AI, interactive exercises, and personalized learning paths to support continuous cognitive development.

---

## 🚀 Key Features

### 1. Intelligent Cognitive Assessment
- Assessment across five cognitive dimensions:
  - Working Memory
  - Attention
  - Processing Speed
  - Logical Reasoning
  - Mental Flexibility
- Performance tracking using accuracy, response time, errors, and hints.
- Uncertainty-aware cognitive scores.

### 2. Dynamic Brain Twin
- Bayesian-based cognitive profiling.
- Continuously updated cognitive estimates.
- Historical performance tracking.
- 95% credible intervals.
- Optional future projections with uncertainty.

### 3. Explainable AI Coach
- Personalized feedback and recommendations.
- Performance-based explanations.
- Rule-based coaching with optional Large Language Model (LLM) integration.
- Local LLM support through Ollama.
- Optional Anthropic API integration.
- Rule-based fallback for reliable operation.

### 4. Adaptive Learning Engine
- Dynamic exercise difficulty adjustment.
- Personalized learning paths.
- Adaptive exercise selection.
- Progress-based recommendations.
- Automatic adaptation to user performance.

### 5. Interactive Cognitive Dashboard
- Cognitive radar charts.
- Progress curves.
- Performance heatmaps.
- Historical tracking.
- Personalized learning objectives.

### 6. AI Collaboration Score

An innovative scoring mechanism evaluating how effectively users collaborate with AI.

The score considers five dimensions:

| Dimension | Weight |
|---|---:|
| Clarification | 20% |
| Critical Verification | 25% |
| Iteration | 20% |
| Autonomy | 20% |
| Responsible AI Use | 15% |

### 7. Interactive Learning Activities
- Memory and reasoning games.
- Attention and concentration exercises.
- Visual-spatial puzzles.
- Reading and writing activities.
- Personalized practice activities.
- Adaptive difficulty levels.

### 8. Additional Features
- Voice-based coaching (text-to-speech).
- Optional self-reported mood.
- Cognitive growth projections.
- Personalized comfort settings.

---

## 🏗️ System Architecture

AI4Brain follows a modular architecture:

| Component | Main Files | Responsibility |
|---|---|---|
| Assessment | `tasks.py`, `engine.py` | Cognitive assessment and scoring |
| Brain Twin | `engine.py` | Bayesian profiling and history |
| AI Coach | `coach.py` | Explainable personalized coaching |
| Adaptive Learning | `engine.py`, `practice.py` | Exercise adaptation |
| Dashboard | `app.py` | Visualization and progress tracking |
| Collaboration Score | `collab.py` | Human-AI collaboration evaluation |
| Cognitive Activities | `games_content.py`, `visual_games.py` | Interactive cognitive exercises |
| Specialized Activities | `autism_content.py`, `dyslexia_content.py`, `focus_content.py`, `literacy.py` | Personalized learning activities |
| Validation | `simulate.py` | Experimental simulation and evaluation |

### Workflow

1. The user interacts with cognitive activities.
2. The assessment engine collects performance indicators.
3. The Brain Twin updates the cognitive profile.
4. The AI Coach analyzes the results and generates feedback.
5. The adaptive engine selects appropriate exercises.
6. The dashboard visualizes cognitive progress.
7. The system continuously updates the user's learning profile.

---

## 🧪 Cognitive Assessment Methodology

AI4Brain evaluates five dimensions:

| Cognitive Dimension | Assessment Task |
|---|---|
| Working Memory | Digit sequence tasks |
| Attention | Stroop colour tasks |
| Processing Speed | Quick arithmetic |
| Logical Reasoning | Number series |
| Mental Flexibility | Colour-cued rule switching |

### Bayesian Skill Estimation

The Brain Twin uses Bayesian updating to estimate cognitive performance.

The probability of success is modeled as:

```text
P(success) = chance + (1 - chance) × sigmoid((skill - difficulty) / 12)
```

The system maintains a posterior distribution over skill levels and calculates a 95% credible interval.

---

## 📊 Experimental Validation

AI4Brain includes a simulation-based validation framework using virtual users with known skill levels.

### Adaptive Learning Performance

| Learning Strategy | Mean Absolute Error |
|---|---:|
| Adaptive Learning (AI4Brain) | 8.4 |
| Fixed Difficulty | 9.3 |
| Random Difficulty | 12.0 |

**95% Interval Coverage:**
- Adaptive Learning: 87%
- Fixed Difficulty: 93%
- Random Difficulty: 87%

These results are from simulated experiments.

---

## 🔐 Ethics, Privacy & Safety

AI4Brain follows a privacy-aware and non-clinical approach:

- User consent before data storage.
- Local SQLite database.
- Pseudonymous user profiles.
- Automatic data deletion after 90 days.
- User-controlled data export and deletion.
- Non-biometric interaction mode.
- No diagnosis or clinical screening.
- No sensitive decisions based solely on face or voice.
- Optional self-reported emotional feedback.

The platform supports learning and cognitive development rather than diagnosing medical or developmental conditions.

---

## 🛠️ Technologies Used

- **Programming Language:** Python
- **Frontend:** Streamlit
- **Data Management:** SQLite
- **AI & Profiling:** Bayesian Statistical Modeling
- **Language Models:** Ollama / Anthropic API (optional)
- **Visualization:** Plotly
- **Speech Processing:** Faster-Whisper (optional)
- **Testing:** Pytest

---

## ⚙️ Installation & Execution

### 1. Clone the repository

```bash
git clone https://github.com/MaylaBeladhria/AI4Brain.git
cd AI4Brain
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Linux / macOS**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Optional voice dependencies:

```bash
pip install -r requirements-voice.txt
```

### 4. Launch the application

```bash
streamlit run app.py
```

### 5. Run automated tests

```bash
pytest -q
```

### 6. Run experimental validation

```bash
python simulate.py
```

Validation results are generated in the `validation/` directory.



## 📁 Project Structure

```text
AI4Brain/
│
├── app.py
├── engine.py
├── coach.py
├── collab.py
├── tasks.py
├── tasks_custom.py
├── practice.py
├── simulate.py
│
├── games_content.py
├── visual_games.py
├── autism_content.py
├── dyslexia_content.py
├── focus_content.py
├── literacy.py
├── support_content.py
├── ui_extra.py
├── stt.py
│
├── tests/
│   ├── test_app.py
│   └── test_core.py
│
├── validation/
│   ├── validation.png
│   ├── validation_results.csv
│   └── summary.md
│
├── requirements.txt
├── requirements-voice.txt
├── .gitignore
└── README.md


## 🌟 Innovation & Expected Impact

AI4Brain introduces an integrated approach to cognitive development by combining:

- Dynamic Bayesian Brain Twin modeling.
- Explainable AI-powered coaching.
- Personalized adaptive learning.
- Uncertainty-aware cognitive assessment.
- Human-AI collaboration measurement.

Its mission is to transform cognitive development into a continuous, measurable, explainable, and personalized learning experience.

---

## 🏆 Challenge

**CISTAC 1.0 – AI4Brain: Cognitive Growth Agent Challenge**

**Project:** AI4Brain – Cognitive Growth Agent  
**Category:** Artificial Intelligence / Cognitive Computing / Adaptive Learning  
**Status:** Research & Development Prototype
