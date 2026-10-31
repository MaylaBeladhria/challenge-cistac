# Cognitive Growth Agent — final version (CISTAC 1.0 – AI4Brain)

A **non-clinical** agent that assesses, understands, coaches and helps users improve across cognitive dimensions,
with an uncertainty-aware Brain Twin, explainable coaching and a measured AI Collaboration Score.

## Run
```bash
pip install -r requirements.txt
pip install -r requirements-voice.txt   # optional: voice reading (first use downloads a ~150 MB model)
streamlit run app.py                 # coach: rule-based by default; free local LLM: COACH_PROVIDER=ollama; or ANTHROPIC_API_KEY
pytest -q                            # 71 automated tests (unit + end-to-end UI)
python simulate.py                   # full validation report -> ./validation
```

## Architecture
| Challenge layer | File | What it does |
|---|---|---|
| A – Assessment & profiling | `tasks.py`, `engine.py` | Plug-in dimensions (5 levels each); logs score, response time, errors, hints, answer changes, time to first choice, abandoned exercises |
| Brain Twin | `engine.py` | SQLite history + Bayesian skill posterior (estimate + 95% interval); optional projection with uncertainty band |
| B – Explainable coach | `coach.py` | LLM fed with Brain Twin + behaviour JSON, clinical-term filter, rule-based fallback; every exercise shows *why* it was chosen |
| C – Adaptive learning & dashboard | `engine.py`, `app.py` | Calibration phase, level adaptation, ranked plan, radar, progress curves, heatmap, goals, behaviour signals |
| AI Collaboration Score | `collab.py` | Documented formula; verification measured in situ by spot-the-error challenges |
| Validation | `simulate.py` | Virtual users with known skill: accuracy, interval coverage, robustness |
| Profile activities | `practice.py`, `support_content.py`, `focus_content.py`, `literacy.py`, `games_content.py` | No-repeat question banks (static + generated) for autism, ADHD and dyslexia; writing check word + letter level |
| Bonus | `app.py` | Voice coaching (text-to-speech, no microphone), self-reported mood (non-biometric emotion awareness), projection |

## Final version: degree of support + the activities of the three documents
### Degree in the profile form
The parent / guardian chooses a **degree (level of support needed)** for the autism, dyslexia and ADHD profiles:
*Mild (light support) · Moderate (some support) · Severe (a lot of support)*. It can be changed in ⚙ Comfort options.
`SAFE_LABELS=1` shows "Light / Some / A lot of support". It is never a diagnosis: it only changes the presentation.

| | Mild | Moderate | Severe |
|---|---|---|---|
| Questions per series (practice tabs, brain-game rounds) | 5 | 4 | 3 |
| Highest level of the practice questions and games | 3 | 3 | 2 |
| Highest brain-game level | 5 (age limit applies) | 4 | 2 |
| Hints | on demand | already open | always shown |
| Tools default level | 2 · Training | 2 · Training | 1 · Discovery |
| Other | | | dyslexia: calm mode on by default |

### Autism document: 12 activities (all suited to the autism profile)
| Activity | Where | How it was built |
|---|---|---|
| Ma journée en cartes | 🌈 questions *My day in cards* + 🧰 *My day* | what's next (2 pictures) → order 3-4 cards → my own plan: add, move, tick done, ⚠️ change announced in advance |
| Le radar des émotions | 🧰 *Emotion radar* + faces questions | 2 very different faces → all faces + colour → what could help; "I don't know" always accepted, no explanation required |
| Le menu de communication | 🧰 *Talk board* + sidebar quick board | 1 of 2 pictures → starter + picture → several pictures; shown and said aloud; available during every activity |
| Mission : préparer mon sac | 🌈 *Mission: pack my bag* | school, park, swimming, sport, picnic; 1 of 2 → tick 3 → tick 4; a comfort object is never "wrong" |
| Le détective des changements | 🌈 *Change detective* | one change → several changes (tick) → a short story: choose a way to adapt (several good answers) |
| Le studio des sons et des sensations | 🧰 *Sound studio* | rain, waves, birds, wind, soft bells, slow colours, bubbles, stars; never automatic, low volume, stop at any time; 👍 / 👎 / 🤷 → my calm kit |
| Les bulles de conversation | 🌈 *Conversation bubbles* | Hello / Thank you → choose a reply (saying no politely counts) → continue a small dialogue; speech and eye contact never required |
| Le magasin des choix | 🧰 *Choice shop* | 1 of 2 + "none of these" → basket → selection for a situation; no right or wrong |
| Le puzzle des indices | 🌈 *Clue puzzle* | animal ↔ home → 2 clues → 3 clues |
| La boîte à solutions | 🌈 *Solution box* | 2 → 4 → 5 solutions incl. "another idea of my own"; every good solution is accepted |
| Mon parcours à mon rythme | 🧰 *My steps* | 2 steps → 4 → 5-6; one step at a time, back, pause / resume, no time limit; level 3: choose the order of some steps |
| Mon monde d'intérêts | 🧰 *My interests* + 🌈 *My interests world* | animals, space, vehicles, dinosaurs; favourite of two → small games → my sentence and my scene; the chosen world is used in the questions |

### Dyslexia document: 12 games (all suited to the dyslexia profile)
| Game | Where | How it was built |
|---|---|---|
| Le détective des sons | 🔤 *Sound detective* | first sound → middle / end sound → which sound changed (cat → cap) |
| Le train des syllabes | 🔤 *Syllable train* (upgraded) | picture + word, one wagon per syllable, sound model in the hint |
| Construis le mot | 🧱 *Build the word* | letter tiles (sh, ch, ck, oo, igh...) that say their sound; first letter given → picture only → listen only; b/d distractor tiles |
| La machine à mots presque jumeaux | 🔤 *Twin words* | very different → what is different (pat / bat) → which word did you hear (ship, sheep, shop, chip) |
| La chasse aux lettres cachées | 🔤 *Hidden letters* | b among x/o/s → b among d/p with a memory tip → tick the words that contain b |
| Le puzzle des phrases | 🧱 *Sentence puzzle* + 🔤 *Word order* | word cards read aloud when pressed: 3 cards → with a complement → with connectors |
| L'écho magique | 🧱 *Magic echo* | the words light up while the voice reads; slower / faster; replay without limit; then "I read it myself" |
| Le marché des mots | 🔤 *Word market* | one rule → two kinds of rules → find the rule |
| La chasse au sens | 🔤 *Meaning hunt* | 1 sentence → 4 sentences with details → implicit information; the text can be listened to |
| Le labyrinthe des rimes | 🔤 *Rhyme maze* (upgraded) | 2 words → 4 words → tick all the rhymes |
| L'atelier des préfixes et suffixes | 🔤 *Prefixes & suffixes* | word ↔ picture (rainy, unhappy) → choose the part (re-, un-, -ful, -less, -er, -ly) → use it in a sentence |
| Mon histoire en images | 🔤 *Story in pictures* + 🧱 *My story* | order 3 pictures → word bank → write 2-3 sentences (helps optional, read aloud, saved) |

### ADHD document
Same 8 games as in v6 (robot rescue, detective, school bag, emotion detective, treasure map, copy the rhythm,
space pause station): already in the app, unchanged, now with the degree rules.

Files: `autism_content.py`, `dyslexia_content.py`, `ui_extra.py` (interactive tools), `engine.py` (degree,
`kv` table for saved plans / baskets / calm kit / stories, deleted with the profile and exported in the JSON).

## What's new in v7: 🧩 Puzzle & 🍂 hidden leaves (tab "Puzzle & leaves")
| Game | Skills (practice only) | ADHD | Autism | Dyslexia | Levels 1 → 3 |
|---|---|---|---|---|---|
| 🧩 Puzzle | visual-spatial thinking, planning, persistence | ✅ | ✅ | ✅ | 4 pieces + faded picture on the board → 9 pieces + small model → 12 pieces, no model ("peek" button) |
| 🍂 Find the same leaves | look-alike shapes, visual memory | ✅ | ✅ | ✅ | 8 leaves face up, find the 2 identical → memory game, 8 hidden cards (look first) → 12 hidden cards with look-alike leaves |

Why these three profiles: calm games with clear rules, a visible goal and no reading or timer (autism); short and
rewarding, they train sustained attention and working memory (ADHD); telling look-alike shapes apart and visual
memory, with a success that does not depend on reading (dyslexia). Not added to the typical profile's main tabs
(it appears there if a comfort option is on).
- The pictures (house, boat, rocket, garden) and the leaves (7 shapes x 6 colours) are **drawn by the code**
  (Pillow / SVG): every game is new and no image file is needed.
- Puzzle: take a piece, press 📍 *Here*; only the right place accepts it ("this piece goes somewhere else").
- Leaves: when two cards differ, the app says why ("same colour, but not the same shape").
- A game counts as a success with few mistakes (puzzle ≤ half the pieces; memory ≤ 2 tries per pair + 1);
  three successes → next level, two failures → easier. Files: `visual_games.py`, `app.py` (`visual_tab`).

## What's new in v6: 7 interactive games, each placed in the profiles it suits
| Game | Skills (practice only) | ADHD | Autism | Dyslexia | Levels 1 → 3 |
|---|---|---|---|---|---|
| 🤖 Robot rescue | selective attention, instructions | ✅ | | | colour only → colour + shape → the rule changes between rounds |
| 🕵️ Detective | visual search, details, reasoning | ✅ | | | 1 feature → 2 features → clues from 3 scenes (drawn keys: colour, size, teeth) |
| 🎒 Pack your school bag | organisation, priorities | ✅ | ✅ routines | | 1 subject, 4 objects → 3 subjects (tick several) → checklist: what is missing? |
| 😊 Emotion detective | emotions, calming strategies | ✅ frustration | ✅ | | faces → a situation, **several right feelings** → choose a strategy |
| 🗺️ Treasure map | memory, sequencing, planning | ✅ | | ✅ left / right | 1 direction → 3 directions to remember → plan a route around rocks |
| 🥁 Copy the rhythm | listening, sound sequences | ✅ | | ✅ sounds in order | 2 sounds → 3-4 → 5-6, answers shown after listening |
| 🚀 Space pause station | noticing feelings, calming down | ✅ | ✅ | ✅ (every profile) | breathing star → star or planets → my own pause idea |

Why not everywhere: the robot and detective games use quick rule changes and many objects, useful for attention
practice but not the calm, predictable pace chosen for the autism profile; the rhythm game helps dyslexia because
hearing and keeping sounds in order is a building block of reading; the treasure map trains left / right, often
tricky with dyslexia. Difficulty adapts as before (3 right answers → harder, ≤ 1 → easier, so fewer objects).
No timer in any game. Each game has its own positive message ("Case solved! You checked the clues carefully").
Files: `games_content.py` (games), `practice.py` (tick-several answers, several right answers, praise).

## What's new in v5
| Change | Where |
|---|---|
| **ADHD profile** with its own main activity: ⚡ *Focus & self-control* (5 topics, rounds of 5, stars, movement breaks) | `focus_content.py`, `app.py` |
| **Questions no longer repeat**: never-seen first (history stored per child), topic rotation, names that change, generated questions | `practice.py` |
| **Autism**: 5 new topics (faces, expressions, what others think, changes of plan, body & calm), ~75 questions + generated ones | `support_content.py` |
| **Dyslexia**: ✍️ *Writing practice* (look-hide-write, copy, dictation) with word **and letter** correction, and 🔤 *Word games* | `literacy.py`, `app.py` |
| Brain games and reading sentences avoid recent repeats too (last 60 exercises / all sentences read) | `engine.py` |

## Child profile form
At first launch the parent/guardian fills in: **first name or nickname**, **age**, a **learning profile**
(typical / autism / dyslexia / ADHD) and a **consent** box. Sidebar: switch between profiles, change comfort options,
delete a profile and its data. The profile only personalises the activities: the app never diagnoses, screens
or guesses a condition. `SAFE_LABELS=1` (environment variable) switches the form to strictly non-clinical
wording ("No specific need / Calm & routine support / Reading support / Focus & movement support") if the brief's "non-clinical" rule
worries you for the submission: the behaviour is identical.

| Profile | Main activity | Defaults |
|---|---|---|
| Typical | 🎯 Brain games (5 adaptive dimensions) | Fun mode under 14 |
| Dyslexia | 📖 **Reading practice** (read aloud, voice correction, retry) · ✍️ **Writing practice** (look, hide, write) · 🔤 **Word games** | Reading support (friendly font, bigger text, listen-aloud) |
| Autism | 🌈 **Feelings, friends & routines**: 9 topics, ~75 written questions + generated ones, names change every time | Calm mode (no timers, no animations, 3-step plan), "I need a break" button |
| ADHD | ⚡ **Focus & self-control**: spot the target, same or different, stop & go, follow the steps, plan & self-control | Focus support (rounds of 5, stars, movement breaks), Fun mode |

All profiles also get the Brain Twin, Coach, Dashboard and Collaboration score.

### Reading practice with voice (dyslexia profile)
1. A sentence is shown (level 1-5 adapted to the child; listen-aloud available).
2. The child **reads aloud** (`st.audio_input`); a **local** speech model (faster-whisper) transcribes it in memory.
3. The transcript is shown and **a parent can fix it**; near-matches are accepted (speech recognition is noisy).
4. Word-by-word check: all correct -> praise; otherwise mistakes are highlighted and the **voice agent reads the
   correct sentence slowly, then the tricky words**, and the child tries again (first vs second try tracked).
Typing ("type it") always works without any microphone or voice package. The recording is never saved or sent.

### Writing practice: look, hide, write (dyslexia profile)
1. A sentence is shown (level 1-5, adapted from the child's last first tries; never-written sentences first).
2. Three modes: **👀 look, hide, write** (from memory), **📝 copy** (the sentence stays), **🎧 listen & write** (dictation).
3. The check is word by word **and letter by letter**: missing / extra words, and inside each misspelled word the
   letters to fix are shown in red. The kind of slip is recognised (mirror letters b/d p/q, swapped letters,
   missing / extra / double letter, vowel) and a short friendly tip is given.
4. Capital letter and final full stop are reminded, but never lower the score.
5. The voice reads the sentence and **spells the tricky words letter by letter**; the child looks again and writes
   it a second time (first vs second try tracked on the dashboard).
6. Misspelled words become **tricky words**: they come back in the spelling game ⭐.

### Word games (dyslexia profile)
Spelling (hear the word, pick the right spelling among look-alikes such as *frend / freind / friend*), syllables
(clap the beats), rhymes (level 3: which one does NOT rhyme), word order (rebuild a mixed-up sentence).
All generated, so they keep changing.

### Feelings, friends & routines (autism profile)
9 topics x 3 levels: feelings, faces & feelings, friends & talking, **say what you mean** (expressions such as
"a piece of cake", "break a leg", sarcasm), **what do they think?** (preferences, who knows what, someone who did
not see an object move), routines, **when plans change**, **my body & calm** (body signals, noise, calm-down ideas),
patterns & sorting. No timer, positive-only feedback with a short explanation, a break button, and ways of asking
for help or for quiet presented as good choices. Practice, not screening or therapy.

### Focus & self-control (ADHD profile)
| Topic | What it trains (practice only) | Example |
|---|---|---|
| Spot the target | finding one picture among look-alikes | "How many 🐟?" in a grid of 🐟 🐠 🐡 |
| Same or different? | attention to detail | two rows of pictures, one swapped |
| Stop & go | waiting / stopping before acting | "GO for 🐶, STOP for 🐱"; level 3: the rule flips with the box colour |
| Follow the steps | keeping instructions in mind | read "First clap, then jump, then sit", hide, "what came second?" |
| Plan & self-control | everyday situations | raising your hand, splitting homework, checklists, "first chores, then game" |
Rounds of 5 questions with stars, then a **movement break** ("do 5 frog jumps", "stretch up high"...). Focus support
also adds movement breaks after each round of brain games.

### Why the questions no longer repeat (`practice.py`)
1. Every answer is stored with the question id, so **never-seen questions come first**, across sessions.
2. In *Mix* mode, the topic practised the longest time ago comes first.
3. Names (`{A}`, `{B}`) change every time and answers are shuffled; faces, minds, patterns, all focus games and all
   word games are **generated** (new emojis, objects, orders, words).
4. Only when everything at a level has been seen, the question seen the longest time ago comes back (with new names).
Brain games regenerate an exercise that matches one of the last 60; reading and writing sentences follow rule 1.

## Limits of these profiles (say it in the report)
No evaluation with children or specialists yet; ASR is less accurate on children's voices and accents;
content is short and in English; the practice questions make no therapeutic claim. Generated questions are
checked by automated tests, but a distractor can occasionally be a real word; the writing check covers spelling,
not handwriting or meaning.

## Dimensions
| Dimension | Task | Main bias / limit |
|---|---|---|
| Working memory | Digit sequence (backwards from level 3) | Digit familiarity, display time |
| Attention | Stroop colour task | Colour-vision differences, reading language |
| Processing speed | Quick arithmetic | Input device speed, maths anxiety |
| Logical reasoning | Number series (5 pattern types) | Maths background |
| Mental flexibility | Colour-cued rule switching | Colour perception, rule learning |

Add a dimension in ~15 lines (see `tasks_custom.py`): the radar, plan, coach, heatmap and simulation adapt automatically.

## Scoring and uncertainty
`P(success) = chance + (1-chance)·sigmoid((skill − difficulty)/12)`, difficulty = (level−0.5)·20.
Outcome per trial: wrong = 0, correct = 1, correct but slow = 0.85, hint used ≤ 0.7.
A grid posterior over skill 0–100 is updated after each trial with a forgetting factor of 0.97; the profile shows the
posterior mean and the 95% credible interval. Level selection targets about 75% expected success.

## Behaviour signals (non-biometric)
Hint rate, answer changes, share of time before the first choice, speed vs time limit, abandoned exercises.
They come from interaction logs only, have no diagnostic meaning and never judge the person.

## AI Collaboration Score
`Score = 0.20·Clarification + 0.25·Verification + 0.20·Iteration + 0.20·Autonomy + 0.15·Responsible use`
- Clarification / Iteration: share of messages with clarifying questions / refinement requests (keywords, English only).
- **Verification: measured in situ.** The coach states a claim about the user's own profile; half are wrong on purpose.
  Score per challenge: right decision 1.0 if verified (0.8 if not), wrong decision 0.3 if verified (0 if blind).
  Falls back to a keyword heuristic until 3 challenges are done.
- Autonomy: 100·(1 − hint rate). Responsible use: 100 − 40 per "give me the answer" − 30 per contact detail shared.
Weights are an unvalidated design proposal.

## Validation (simulated users, `python simulate.py`)
Typical users, 40 exercises, "mismatched" model (different curve slope + 5% random lapses):

| Level policy | Mean abs. error (points) | 95% interval coverage |
|---|---|---|
| adaptive (ours) | 8.4 | 87% |
| fixed level 3 | 9.3 | 93% |
| random level | 12.0 | 87% |

Robustness at 40 exercises (true skill 70 for non-random): reference typical user 66; random guesser 3 (correctly very low);
always-slow user 35 and hint-heavy user 27 (**known limitation: speed and hints lower the estimate**).
Honest reading: adaptive selection is the most accurate, the interval is slightly over-confident when the user does not
follow our model (87% < 95%), and the matched model is partly circular. Validation uses simulated users, not real people.

## Ethics & data
Consent before storage; local SQLite; pseudonym; 90-day automatic deletion; delete + export buttons; no camera or
microphone; no sensitive decision from face/voice; no medical information asked or stored (support settings are preferences); mood is self-reported and optional; non-clinical vocabulary enforced.

## Limits
Difficulty scale designed, not clinically calibrated; no real-user study yet; keyword heuristics are English-only;
speed-based scoring can disadvantage some users; projections are scenarios, never certainties.

## Submission checklist
- [ ] Repository public, no API key committed (`.gitignore` already excludes the database)
- [ ] Screenshots in `docs/` and linked here
- [ ] Demo video 3–5 min · Technical report ≤ 8 pages · Slides ≤ 15 · everything in English
