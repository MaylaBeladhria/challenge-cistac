"""Practice questions on feelings, friends, routines and more (autism profile, original content, English).

Design rules: no timer, positive-only feedback with a short explanation, no scoring against others,
'I need a break' always available, and ways of asking for help or a quiet moment are presented as good choices.
These are PRACTICE activities, not a screening or a therapy, and never produce any diagnosis.

v5: 9 topics (5 new), names change every time ({A}/{B}/{C}), and 3 topics are generated
(faces, "what do they think?", patterns) so the questions do not repeat. See practice.py for the no-repeat rule.
"""
import random

import autism_content as au
import games_content as g
from practice import Bank, gen_id, item, level_from_history

CATEGORIES = ["Feelings", "Faces & feelings", "Friends & talking", "Say what you mean", "What do they think?",
              "Routines", "When plans change", "My body & calm", "Patterns & sorting",
              # v6 games (games_content.py)
              "Emotion detective",
              # final version (autism_content.py): activities of the autism document
              "My day in cards", "Change detective", "Conversation bubbles", "Clue puzzle", "Solution box",
              "Mission: pack my bag", "My interests world"]

_i = item

ITEMS = [
    # ---- Feelings
    _i(1, "Feelings", 1, "{A} gets a big birthday cake. How does {A} feel?",
       ["😀 Happy", "😢 Sad", "😠 Angry"], "😀 Happy", "Getting something nice often makes us feel happy."),
    _i(2, "Feelings", 1, "{A}'s ice cream falls on the ground. How might {A} feel?",
       ["😢 Sad", "😀 Happy", "😴 Sleepy"], "😢 Sad", "When something we like is lost, we can feel sad."),
    _i(3, "Feelings", 1, "A very loud thunder makes {A} jump. How might {A} feel?",
       ["😨 Scared", "😀 Happy", "😴 Sleepy"], "😨 Scared", "Sudden loud sounds can make people feel scared."),
    _i(4, "Feelings", 1, "{A} yawns and rubs their eyes after a long day. How does {A} feel?",
       ["😴 Tired", "😠 Angry", "😀 Excited"], "😴 Tired", "Yawning and rubbing eyes are signs of being tired."),
    _i(5, "Feelings", 2, "{B} took {A}'s toy without asking. How might {A} feel?",
       ["😠 Upset", "😀 Excited", "😴 Sleepy"], "😠 Upset", "When someone takes our things, we can feel upset."),
    _i(6, "Feelings", 2, "{A} worked hard and finished a big puzzle. How might {A} feel?",
       ["😊 Proud", "😨 Scared", "😢 Sad"], "😊 Proud", "Finishing something hard can make us feel proud."),
    _i(7, "Feelings", 2, "It is almost {A}'s turn on the swing. How might {A} feel?",
       ["🤩 Excited", "😨 Scared of the swing", "😴 Sleepy"], "🤩 Excited", "Waiting for something fun can feel exciting."),
    _i(8, "Feelings", 3, "{A}'s best friend {B} is moving to another city. What might {A} feel?",
       ["A mix of sad and happy for the friend", "Only angry", "Only sleepy"],
       "A mix of sad and happy for the friend", "We can feel more than one feeling at the same time."),
    _i(9, "Feelings", 3, "{A} is about to give a talk to the class and their hands feel shaky. How might {A} feel?",
       ["Nervous", "Bored", "Proud already"], "Nervous", "Shaky hands can be a sign of feeling nervous."),
    _i(31, "Feelings", 1, "{A} finds a lost teddy bear under the bed. How does {A} feel?",
       ["😀 Happy", "😠 Angry", "😨 Scared"], "😀 Happy", "Finding something we missed feels good."),
    _i(32, "Feelings", 1, "{A} wanted to go to the park, but it is raining. How might {A} feel?",
       ["😞 Disappointed", "🤩 Excited", "😴 Sleepy"], "😞 Disappointed",
       "When a plan we liked cannot happen, we can feel disappointed."),
    _i(33, "Feelings", 2, "{A} opens a present and finds the exact game they wanted. How might {A} feel?",
       ["😮 Surprised and happy", "😢 Sad", "😠 Angry"], "😮 Surprised and happy",
       "An unexpected nice thing can make us surprised and happy at the same time."),
    _i(34, "Feelings", 2, "{A} cannot find their mum in the big shop. How might {A} feel?",
       ["😟 Worried", "😀 Happy", "😴 Sleepy"], "😟 Worried",
       "Feeling lost can make us worried. Asking a shop helper is a good idea."),
    _i(35, "Feelings", 3, "{A} tries the same puzzle piece five times and it never fits. How might {A} feel?",
       ["😤 Frustrated", "😴 Sleepy", "🤩 Excited"], "😤 Frustrated",
       "When something keeps not working, we can feel frustrated. A short break can help."),
    _i(36, "Feelings", 3, "{A} trips in front of the class, and some children look. How might {A} feel?",
       ["😳 Embarrassed", "😊 Proud", "😴 Bored"], "😳 Embarrassed",
       "Feeling embarrassed is normal. It passes, and everyone trips sometimes."),
    # ---- Friends & talking
    _i(10, "Friends & talking", 1, "You want to play with the ball {A} has. What can you say?",
       ["'Can I play with you?'", "Grab the ball and run", "Shout at {A}"], "'Can I play with you?'",
       "Asking politely is a clear way to join a game."),
    _i(11, "Friends & talking", 1, "{A} says 'Hello!' to you. What can you do?",
       ["Say 'Hello' or wave back", "Shout at them", "Take their bag"], "Say 'Hello' or wave back",
       "A hello or a wave are friendly ways to answer."),
    _i(12, "Friends & talking", 1, "The room is very loud and you feel uncomfortable. What can you do?",
       ["Ask a grown-up for a quiet break", "Hit the wall", "Say nothing and stay"], "Ask a grown-up for a quiet break",
       "Asking for what you need, like a quiet break, is a great idea."),
    _i(13, "Friends & talking", 2, "You did not understand the teacher's instruction. What can you do?",
       ["Ask: 'Can you explain again, please?'", "Pretend you understood", "Leave without telling anyone"],
       "Ask: 'Can you explain again, please?'", "It is always okay to ask for help or for an instruction to be repeated."),
    _i(14, "Friends & talking", 2, "{A} looks sad. What is a kind thing to do?",
       ["Ask: 'Are you okay? Do you want to talk?'", "Laugh at them", "Ignore them"],
       "Ask: 'Are you okay? Do you want to talk?'", "Asking kindly shows you care."),
    _i(15, "Friends & talking", 2, "You do not like a game and want to say no. What can you say?",
       ["'No thank you, I would like something else.'", "Call the others names", "Break the game"],
       "'No thank you, I would like something else.'", "You can say no in a calm, kind way."),
    _i(16, "Friends & talking", 3, "{A} and {B} want the same toy. What is a fair idea?",
       ["Take turns", "Fight for it", "Hide the toy"], "Take turns", "Taking turns is fair for everyone."),
    _i(17, "Friends & talking", 3, "You spilled {A}'s drink by mistake. What can you do?",
       ["Say sorry and help clean up", "Run away", "Blame someone else"], "Say sorry and help clean up",
       "Mistakes happen. Saying sorry and helping fixes the problem."),
    _i(37, "Friends & talking", 1, "{A} gives you a sticker. What can you say?",
       ["'Thank you!'", "'Give me more!'", "Say nothing and walk away"], "'Thank you!'",
       "Saying thank you tells the other person you liked their gift."),
    _i(38, "Friends & talking", 2, "{A} is talking about dinosaurs. You love trains. What is a good way to talk?",
       ["Listen, ask one question about dinosaurs, then share about trains",
        "Only talk about trains", "Walk away in the middle"],
       "Listen, ask one question about dinosaurs, then share about trains",
       "A conversation is like a ball game: each person takes a turn."),
    _i(39, "Friends & talking", 2, "You want to join {A} and {B} who are building with blocks. What can you do?",
       ["Watch a little, then ask: 'Can I build too?'", "Knock their tower down", "Take all the blocks"],
       "Watch a little, then ask: 'Can I build too?'", "Watching first helps you understand the game, then you ask."),
    _i(40, "Friends & talking", 3, "{A} talks very close to your face and you don't like it. What can you say?",
       ["'Can you step back a little, please?'", "Push {A} hard", "Scream"],
       "'Can you step back a little, please?'", "You can ask for more space in a calm, clear way."),
    _i(41, "Friends & talking", 3, "{A} keeps yawning while you tell a long story. What might it mean?",
       ["{A} may be tired or want to change topic", "{A} is very excited", "{A} wants a longer story"],
       "{A} may be tired or want to change topic",
       "Yawning can mean someone is tired or would like another topic. You can ask them what they think."),
    # ---- Say what you mean (expressions that do not mean the words)
    _i(42, "Say what you mean", 1, "{A} says: 'Can you give me a hand?' What does {A} want?",
       ["Some help", "Your real hand to keep", "A high five only"], "Some help",
       "'Give me a hand' means 'help me'."),
    _i(43, "Say what you mean", 1, "Mum says: 'Hold on a second!' What does she mean?",
       ["Wait a little", "Hold something for exactly one second", "Hold on to the door"], "Wait a little",
       "'Hold on a second' means 'please wait a short time'."),
    _i(44, "Say what you mean", 1, "Dad says: 'Hop in!' next to the car. What does he mean?",
       ["Get into the car", "Jump like a rabbit", "Hop on one foot around the car"], "Get into the car",
       "'Hop in' just means 'get in'. Nobody needs to hop!"),
    _i(45, "Say what you mean", 2, "{A} says the test was 'a piece of cake'. What does {A} mean?",
       ["The test was easy", "The test had cake in it", "{A} was hungry"], "The test was easy",
       "'A piece of cake' means something is very easy."),
    _i(46, "Say what you mean", 2, "Before the show, {A} says to {B}: 'Break a leg!' What does it mean?",
       ["Good luck!", "Please get hurt", "Be careful with your legs"], "Good luck!",
       "In theatre, 'break a leg' is a friendly way to say good luck."),
    _i(47, "Say what you mean", 2, "The teacher says: 'I'm all ears.' What does she mean?",
       ["She is listening carefully", "She has many ears", "She cannot hear"], "She is listening carefully",
       "'I'm all ears' means 'I am ready to listen'."),
    _i(48, "Say what you mean", 2, "{A} says: 'Keep an eye on my bag, please.' What should you do?",
       ["Watch the bag", "Put your eye on the bag", "Close one eye"], "Watch the bag",
       "'Keep an eye on' means 'watch' or 'look after'."),
    _i(49, "Say what you mean", 3, "Grandpa says: 'It's raining cats and dogs!' What does he mean?",
       ["It is raining a lot", "Animals fall from the sky", "Cats and dogs are outside"], "It is raining a lot",
       "'Raining cats and dogs' means very heavy rain."),
    _i(50, "Say what you mean", 3, "{A} says: 'Don't spill the beans about the surprise party!' What does it mean?",
       ["Don't tell the secret", "Don't drop the beans", "Don't eat beans at the party"], "Don't tell the secret",
       "'Spill the beans' means 'tell a secret'."),
    _i(51, "Say what you mean", 3, "{A} drops all the books and says: 'Oh great, just great!' How does {A} feel?",
       ["Annoyed (not happy)", "Very happy", "Proud of dropping them"], "Annoyed (not happy)",
       "Sometimes people say 'great' when it is NOT great. The voice and the situation tell us the real meaning."),
    _i(52, "Say what you mean", 3, "{A} says: 'I'm on cloud nine today!' How does {A} feel?",
       ["Very happy", "Up in the sky", "Tired"], "Very happy", "'On cloud nine' means extremely happy."),
    _i(53, "Say what you mean", 3, "{A} says: 'I'm feeling under the weather.' What does {A} mean?",
       ["{A} feels a bit unwell", "{A} is standing under the rain", "{A} likes the weather"],
       "{A} feels a bit unwell", "'Under the weather' means feeling a little sick."),
    # ---- Routines
    _i(18, "Routines", 1, "What do we usually do first in the morning?",
       ["Wake up", "Go to bed", "Eat dinner"], "Wake up", "The day starts when we wake up."),
    _i(19, "Routines", 1, "What do we do before eating?",
       ["Wash our hands", "Brush our teeth", "Put on pajamas"], "Wash our hands", "Clean hands help keep us healthy."),
    _i(20, "Routines", 1, "What comes after brushing teeth at night?",
       ["Go to sleep", "Eat breakfast", "Go to school"], "Go to sleep", "Brushing teeth is one of the last steps before bed."),
    _i(21, "Routines", 2, "Which comes first: put on socks or put on shoes?",
       ["Put on socks", "Put on shoes"], "Put on socks", "Socks go on before shoes."),
    _i(22, "Routines", 2, "Plan: breakfast, school, lunch, homework. What comes after school?",
       ["Lunch", "Breakfast", "Homework"], "Lunch", "In this plan, lunch comes right after school."),
    _i(23, "Routines", 3, "Making a sandwich: take bread, add filling, ... what comes right after adding the filling?",
       ["Close the sandwich", "Take the bread", "Wash the plate"], "Close the sandwich",
       "After the filling, we close the sandwich, then we eat."),
    _i(24, "Routines", 3, "Plan: wake up, eat breakfast, brush teeth, go to school. Which step is missing?",
       ["Get dressed", "Go to bed", "Eat dinner"], "Get dressed", "We get dressed before leaving for school."),
    _i(54, "Routines", 1, "What do we do after using the toilet?",
       ["Flush and wash our hands", "Go straight to eat", "Go to sleep"], "Flush and wash our hands",
       "Flushing and washing hands keep everyone clean."),
    _i(55, "Routines", 2, "Washing hands: wet hands, add soap, ... what comes next?",
       ["Rub hands together", "Dry hands", "Turn off the light"], "Rub hands together",
       "We rub the soap all over our hands, then rinse and dry."),
    _i(56, "Routines", 2, "Getting ready for school: which do we pack in the school bag?",
       ["Books and a pencil case", "The TV", "The bed"], "Books and a pencil case",
       "We pack the things we need for school."),
    _i(57, "Routines", 3, "Bath time: fill the bath, get in, wash, ... what comes right after washing?",
       ["Rinse the soap off", "Fill the bath", "Eat breakfast"], "Rinse the soap off",
       "After washing, we rinse, then get out and dry ourselves."),
    _i(58, "Routines", 3, "Plan: homework, play, dinner, bath, bed. {A} finished dinner. What is next?",
       ["Bath", "Play", "Homework"], "Bath", "In this plan, the bath comes right after dinner."),
    # ---- When plans change
    _i(59, "When plans change", 1, "{A} wanted the red cup but it is dirty. There is a blue cup. What can {A} do?",
       ["Use the blue cup today", "Refuse to drink all day", "Throw the blue cup"], "Use the blue cup today",
       "Using the other cup is a good solution. The red cup can come back tomorrow."),
    _i(60, "When plans change", 1, "The playground is closed today. What can you do?",
       ["Choose another fun thing, like drawing", "Shout at the gate", "Stay sad all day"],
       "Choose another fun thing, like drawing", "When a plan changes, we can pick a new plan."),
    _i(61, "When plans change", 2, "Your usual teacher is away and a new teacher comes. What can help?",
       ["Say hello and follow the same class rules", "Hide under the desk", "Go home alone"],
       "Say hello and follow the same class rules", "Many things stay the same even when the teacher changes."),
    _i(62, "When plans change", 2, "Swimming is cancelled because the pool is broken. What can you say to yourself?",
       ["'That's disappointing, but I can swim next week.'", "'Everything is ruined forever.'",
        "'I will never swim again.'"], "'That's disappointing, but I can swim next week.'",
       "It is okay to feel disappointed. Saying 'next time' helps us feel better."),
    _i(63, "When plans change", 2, "The bus takes a different road today. What can {A} do if this feels strange?",
       ["Ask the driver or a grown-up what is happening", "Get off the bus alone", "Scream until it stops"],
       "Ask the driver or a grown-up what is happening", "Asking questions makes a change easier to understand."),
    _i(64, "When plans change", 3, "Your picture schedule says 'Art', but today it is 'Music'. What helps most?",
       ["Ask to update the schedule so you know what comes next", "Refuse all activities",
        "Pretend it is still art"], "Ask to update the schedule so you know what comes next",
       "Knowing the new plan makes changes easier."),
    _i(65, "When plans change", 3, "{A} planned to play with {B}, but {B} is sick. What is a good new plan?",
       ["Play with someone else or do a calm activity", "Decide to never play again", "Be angry at {B}"],
       "Play with someone else or do a calm activity", "{B} did not choose to be sick. A plan B can still be fun."),
    # ---- My body & calm
    _i(66, "My body & calm", 1, "Your hands feel tight and your face feels hot. What can help?",
       ["Take slow, deep breaths", "Run into the street", "Hit someone"], "Take slow, deep breaths",
       "Slow breathing helps the body calm down."),
    _i(67, "My body & calm", 1, "The lights and noises in the shop feel too much. What can help?",
       ["Ask for headphones or a quiet spot", "Scream louder than the noise", "Run away alone"],
       "Ask for headphones or a quiet spot", "Making things quieter is a great way to feel better."),
    _i(68, "My body & calm", 1, "Your tummy makes a loud noise and it is lunchtime. What does your body tell you?",
       ["I am hungry", "I am sleepy", "I am cold"], "I am hungry", "Our tummy often tells us when we need food."),
    _i(69, "My body & calm", 2, "You are shivering and your hands are cold. What can you do?",
       ["Put on a jumper", "Take off your shoes", "Eat ice cream"], "Put on a jumper",
       "Shivering tells us we are cold. Warm clothes help."),
    _i(70, "My body & calm", 2, "A label in your T-shirt scratches and bothers you. What can you do?",
       ["Tell a grown-up so they can cut it or change the T-shirt", "Rip your T-shirt", "Cry and say nothing"],
       "Tell a grown-up so they can cut it or change the T-shirt", "Telling someone what bothers you helps fix it."),
    _i(71, "My body & calm", 2, "Which is a calm-down idea?",
       ["Squeeze a soft ball and count to 10", "Slam the door", "Throw toys"], "Squeeze a soft ball and count to 10",
       "Squeezing and counting are calm ways to let big feelings out."),
    _i(72, "My body & calm", 3, "You feel your worry getting bigger, like a balloon. What can you do?",
       ["Breathe out slowly to 'let air out', then talk to someone", "Keep it all inside", "Run in circles"],
       "Breathe out slowly to 'let air out', then talk to someone",
       "Breathing out slowly and talking about it can make a worry smaller."),
    _i(73, "My body & calm", 3, "On a scale from 1 (calm) to 5 (too much), you feel at 4. What is a good step?",
       ["Go to your calm corner before it reaches 5", "Wait until it reaches 5", "Pretend you are at 1"],
       "Go to your calm corner before it reaches 5", "Noticing early helps you calm down sooner."),
    _i(74, "My body & calm", 3, "You have been playing a loud game for a long time and feel very tired. What can you say?",
       ["'I need a quiet break now.'", "'I must keep playing forever.'", "Nothing, and keep going"],
       "'I need a quiet break now.'", "Telling others you need a break is a smart and kind choice for yourself."),
    # ---- Patterns & sorting (static examples; most of this topic is generated, see below)
    _i(25, "Patterns & sorting", 1, "Which one is different?  🍎 🍌 🍇 🚗",
       ["🍎", "🍇", "🚗"], "🚗", "The car is not a fruit."),
    _i(29, "Patterns & sorting", 3, "What comes next?  1, 2, 4, 8, ?",
       ["10", "12", "16"], "16", "Each number is double the one before."),
]

# ------------------------------------------------------------------ generated topics
FACES = {"😀": "happy", "😢": "sad", "😠": "angry", "😨": "scared", "😴": "sleepy",
         "😮": "surprised", "😕": "confused", "🤩": "excited", "🤢": "feeling sick",
         "😟": "worried", "😤": "frustrated", "😳": "embarrassed", "😌": "calm", "🥱": "bored"}
FACE_LEVEL = {1: ["😀", "😢", "😠", "😨", "😴"],
              2: ["😀", "😢", "😠", "😨", "😴", "😮", "😕", "🤩", "🤢"],
              3: list(FACES)}
CLOSE = [{"😀", "🤩", "😌"}, {"😨", "😟"}, {"😠", "😤"}, {"😴", "🥱"}, {"😕", "😟"}]  # never in the same choice set


def _faces(level, rng, ctx):
    pool = FACE_LEVEL[level]
    ans = rng.choice(pool)
    near = set().union(*[g for g in CLOSE if ans in g])
    others = [f for f in pool if f != ans and f not in near]
    k = 1 if level == 1 else 3  # level 1: two very different faces (emotion radar, autism document)
    dist = rng.sample(others, k)
    if rng.random() < 0.5:
        return item(gen_id("face", level, "name", ans, *sorted(dist)), "Faces & feelings", level,
                    "What feeling does this face show?", [FACES[f] for f in [ans] + dist], FACES[ans],
                    f"This face {ans} looks {FACES[ans]}. Look at the eyes and the mouth.",
                    html=f"<div style='font-size:5rem;text-align:center'>{ans}</div>")
    return item(gen_id("face", level, "pick", ans, *sorted(dist)), "Faces & feelings", level,
                f"Which face looks **{FACES[ans]}**?", [ans] + dist, ans,
                f"{ans} is the {FACES[ans]} face. Look at the eyes and the mouth.")


FOODS = [("🍓", "strawberries"), ("🍌", "bananas"), ("🍕", "pizza"), ("🍪", "cookies"), ("🍎", "apples"),
         ("🥕", "carrots"), ("🍇", "grapes"), ("🧀", "cheese")]
TOYS = [("⚽", "ball"), ("🧸", "teddy bear"), ("🚗", "toy car"), ("🪁", "kite"), ("🎈", "balloon"), ("🦖", "dinosaur"),
        ("📕", "book"), ("🔑", "key")]
PLACES = ["box", "basket", "drawer", "bag", "cupboard", "toy chest"]
BOXES = [("crayon box", "crayons", "🕯️ candles"), ("egg box", "eggs", "🪀 a yo-yo"),
         ("biscuit tin", "biscuits", "🧵 sewing things"), ("pencil case", "pencils", "🍬 sweets")]


def _minds(level, rng, ctx):
    cat = "What do they think?"
    if level == 1:  # preferences: other people can like different things
        (e1, f1), (e2, f2) = rng.sample(FOODS, 2)
        return item(gen_id("mind1", f1, f2), cat, level,
                    f"{{A}} loves {e1} {f1}. {{B}} loves {e2} {f2}. There are both on the table. "
                    f"What will **{{A}}** choose?", [f"{e1} {f1}", f"{e2} {f2}", "Nothing at all"],
                    f"{e1} {f1}", f"{{A}} likes {f1}. People can like different things from us.")
    if level == 2:  # seeing leads to knowing
        e, obj = rng.choice(TOYS)
        place = rng.choice(PLACES)
        return item(gen_id("mind2", obj, place), cat, level,
                    f"{{A}} opens the {place} and sees a {e} {obj} inside. {{B}} was in the other room and did "
                    f"not look. Who knows what is in the {place}?", ["{A}", "{B}", "Both of them"], "{A}",
                    f"Only {{A}} looked inside. {{B}} did not see it, so {{B}} does not know.")
    if rng.random() < 0.65:  # level 3: someone does not know that something moved
        e, obj = rng.choice(TOYS)
        p1, p2, p3 = rng.sample(PLACES, 3)
        return item(gen_id("mind3", obj, p1, p2, p3), cat, level,
                    f"{{A}} puts the {e} {obj} in the {p1} and goes outside. While {{A}} is away, {{B}} moves "
                    f"the {obj} to the {p2}. {{A}} comes back. Where will {{A}} look first?",
                    [f"In the {p1}", f"In the {p2}", f"In the {p3}"], f"In the {p1}",
                    f"{{A}} did not see the {obj} move, so {{A}} still thinks it is in the {p1}.")
    box, normal, real = rng.choice(BOXES)
    return item(gen_id("mind3b", box), cat, level,
                f"There is a {box}. Inside there are {real}, not {normal}! {{B}} has never opened it. "
                f"What will {{B}} think is inside?", [normal.capitalize(), real.capitalize(), "Nothing"],
                normal.capitalize(), f"{{B}} only sees a {box}, so {{B}} will think there are {normal} inside.")


SETS = {"fruit": ["🍎", "🍌", "🍇", "🍓", "🍐", "🍒"], "animal": ["🐶", "🐱", "🐰", "🐻", "🐸", "🐵"],
        "vehicle": ["🚗", "🚌", "🚲", "🚂", "✈️", "🚀"], "clothes": ["👕", "👖", "🧦", "🧢", "👗", "🧤"],
        "weather": ["☀️", "🌧️", "❄️", "🌈", "⛅", "⚡"]}
SHAPES = ["🔴", "🔵", "🟢", "🟡", "🟣", "🟥", "🟦", "🟩"]


def _patterns(level, rng, ctx):
    cat = "Patterns & sorting"
    if rng.random() < 0.5:  # odd one out
        s1, s2 = rng.sample(list(SETS), 2)
        k = 3 if level == 1 else 4
        group = rng.sample(SETS[s1], k)
        odd = rng.choice(SETS[s2])
        row = group + [odd]
        rng.shuffle(row)
        return item(gen_id("odd", *row), cat, level, "Which one is different?  " + " ".join(row),
                    [odd] + rng.sample(group, 2), odd, f"{odd} is not a {s1} like the others.")
    unit = {1: "AB", 2: rng.choice(["AAB", "ABC", "ABB"]), 3: rng.choice(["AABB", "ABCB", "ABAC"])}[level]
    syms = rng.sample(SHAPES, len(set(unit)))
    m = dict(zip(sorted(set(unit)), syms))
    seq = [m[c] for c in unit * 3]
    cut = rng.randint(len(unit) + 2, len(seq) - 1)
    shown, ans = seq[:cut], seq[cut]
    extra = [s for s in SHAPES if s not in syms]
    choices = list(dict.fromkeys([ans] + [s for s in syms if s != ans] + extra))[:3]
    return item(gen_id("pat", unit, *shown), cat, level, "What comes next?  " + " ".join(shown) + " ?",
                choices, ans, f"The pattern repeats: {' '.join(m[c] for c in unit)}. So {ans} comes next.")


BANK = Bank(CATEGORIES, ITEMS, {"Faces & feelings": _faces, "What do they think?": _minds,
                                "Patterns & sorting": _patterns, "Emotion detective": g.emotions,
                                "My day in cards": au.day_cards, "Change detective": au.change_detective,
                                "Conversation bubbles": au.conversation, "Clue puzzle": au.clue_puzzle,
                                "Solution box": au.solution_box, "Mission: pack my bag": au.mission_bag,
                                "My interests world": au.interests})


def soc_level(df_act, cap=3):
    return level_from_history(df_act, cap)


def pick_item(df_act, cap=3, category=None, rng=random, recent=(), ctx=None):
    return BANK.pick(df_act, cap, category, rng, recent, ctx)
