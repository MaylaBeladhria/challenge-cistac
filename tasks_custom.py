"""Add your own dimensions here (e.g. for the 'surprise element' of the final defence).

1. Write a generator (level 1-5, rng) -> dict, decorated with @register(name, description, chance)
2. Set ENABLE_EXAMPLE = True (or export ENABLE_EXAMPLE_DIM=1) and restart the app.
The radar chart, plan, coach, heatmap and simulation pick the new dimension up automatically.
"""
import os

ENABLE_EXAMPLE = os.getenv("ENABLE_EXAMPLE_DIM") == "1"

if ENABLE_EXAMPLE:
    from tasks import pick_choices, register

    @register("Number sense", "Estimate quantities quickly without exact calculation.")
    def number_sense(level, rng):
        hi = 20 + 10 * level
        a, b = rng.randint(11, hi), rng.randint(11, hi)
        ans = a * b
        dist = [int(ans * 1.25), int(ans * 0.8), ans + 100, max(1, ans - 100)]
        return dict(prompt=f"Which value is the exact product of {a} x {b}?",
                    tlimit=12.0, choices=pick_choices(ans, dist, rng), answer=ans,
                    hint="Split one number: a x (10 + r) = 10a + a x r.")
