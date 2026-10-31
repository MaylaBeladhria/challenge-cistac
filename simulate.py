"""Validation by simulation: virtual users with a KNOWN skill answer exercises; we check whether the
Brain Twin recovers that skill and whether its 95% interval is honest.

Scenarios
- model 'matched'    : users answer exactly as the estimator assumes (sanity check, somewhat circular)
- model 'mismatched' : different success-curve slope + 5% random lapses (fairer test)
- policy             : 'adaptive' (our level selection) vs 'fixed' (always level 3) vs 'random' level
- behaviour          : typical / random (guessing) / slow (always over the time limit) / hint_spammer

Run:  python simulate.py          (full, ~1 min)      python simulate.py --quick
Outputs in ./validation : validation_results.csv, summary.md, validation.png
"""
import random
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import engine

CHECK = (5, 10, 20, 40)
MODELS = {"matched": (12.0, 0.0), "mismatched": (18.0, 0.05)}  # (curve slope, lapse rate)
SKILLS = list(range(10, 100, 10))


def _level(policy, mean, rng):
    if policy == "adaptive":
        return engine.next_level(mean)
    if policy == "fixed":
        return 3
    return rng.randint(1, 5)


def one_user(skill, dim, policy, behaviour, model, rng, nrng):
    chance = engine.CHANCE[dim]
    scale, lapse = MODELS[model]
    logp = np.zeros_like(engine.GRID)
    mean, out = 50.0, []
    for i in range(1, max(CHECK) + 1):
        level = _level(policy, mean, rng)
        t = engine.make_trial(dim, level, rng)
        d = (level - 0.5) * 20
        p = chance + (1 - chance) / (1 + np.exp(-(skill - d) / scale))
        p = chance if behaviour == "random" else p * (1 - lapse) + chance * lapse
        correct = nrng.random() < p
        rt = t["tlimit"] * (1.4 if behaviour == "slow" else float(nrng.uniform(0.3, 0.9)))
        hint = behaviour == "hint_spammer" and nrng.random() < 0.7
        logp = engine.update_logp(logp, level, engine.evidence(correct, rt, t["tlimit"], hint), chance)
        mean, lo, hi = engine.summarize(logp)
        if i in CHECK:
            out.append(dict(n=i, est=mean, lo=lo, hi=hi))
    return out


def run(quick=False, seed=0, reps=None):
    reps = reps or (4 if quick else 20)
    rng, nrng = random.Random(seed), np.random.default_rng(seed)
    dims = [d for d in ("Attention", "Mental flexibility") if d in engine.DIMENSIONS] or list(engine.DIMENSIONS)[:1]
    rows = []

    def add(skill, dim, policy, behaviour, model, rep):
        for r in one_user(skill, dim, policy, behaviour, model, rng, nrng):
            rows.append(dict(skill=skill, dim=dim, policy=policy, behaviour=behaviour, model=model, rep=rep, **r))

    for model in MODELS:
        for policy in ("adaptive", "fixed", "random"):
            for skill in SKILLS:
                for rep in range(reps):
                    add(skill, dims[rep % len(dims)], policy, "typical", model, rep)
    for behaviour in ("random", "slow", "hint_spammer"):
        for rep in range(reps * 3):
            add(0 if behaviour == "random" else 70, dims[rep % len(dims)], "adaptive", behaviour, "mismatched", rep)
    return pd.DataFrame(rows)


def summarize(res):
    res = res.copy()
    res["abs_err"] = (res.est - res.skill).abs()
    res["covered"] = (res.lo <= res.skill) & (res.skill <= res.hi)
    res["width"] = res.hi - res.lo
    typ = res[res.behaviour == "typical"]
    acc = (typ.groupby(["model", "policy", "n"])
           .agg(MAE=("abs_err", "mean"), coverage_95=("covered", "mean"), interval_width=("width", "mean"))
           .round(2).reset_index())
    ref = res[(res.behaviour == "typical") & (res.skill == 70) & (res.policy == "adaptive")
              & (res.model == "mismatched") & (res.n == 40)].assign(behaviour="typical (reference, true=70)")
    rb = pd.concat([ref, res[(res.behaviour != "typical") & (res.n == 40)]])
    rob = (rb.groupby("behaviour").agg(mean_estimate=("est", "mean"), mean_interval_width=("width", "mean"))
           .round(1).reset_index())
    return dict(accuracy=acc, robustness=rob)


def make_figure(res):
    from matplotlib.figure import Figure
    s = summarize(res)
    fig = Figure(figsize=(16, 4.6))
    a1, a2, a3 = fig.subplots(1, 3)

    acc = s["accuracy"]
    for pol, g in acc[acc.model == "mismatched"].groupby("policy"):
        a1.plot(g.n, g.MAE, marker="o", label=pol)
    a1.set(title="Error vs number of exercises (mismatched model)", xlabel="exercises", ylabel="mean abs. error (points)")
    a1.legend(); a1.grid(alpha=.3)

    t = res[(res.behaviour == "typical") & (res.policy == "adaptive") & (res.model == "mismatched") & (res.n == 40)]
    g = t.groupby("skill").agg(est=("est", "mean"), half=("hi", lambda x: 0)).reset_index()
    g["lo"] = t.groupby("skill").lo.mean().values
    g["hi"] = t.groupby("skill").hi.mean().values
    a2.plot([0, 100], [0, 100], "k--", label="perfect")
    a2.errorbar(g.skill, g.est, yerr=[g.est - g.lo, g.hi - g.est], fmt="o-", capsize=3, label="estimate + 95% interval")
    a2.set(title="Estimate vs true skill (40 exercises)", xlabel="true skill", ylabel="estimated skill")
    a2.legend(); a2.grid(alpha=.3)

    rob = s["robustness"]
    a3.bar(rob.behaviour, rob.mean_estimate, color=["#6C5CE7", "#e17055", "#fdcb6e", "#00b894"][:len(rob)])
    a3.axhline(70, color="k", ls="--", lw=1)
    a3.set(title="Robustness: mean estimate at 40 exercises", ylabel="estimate (dashed = true 70 for non-random)")
    a3.tick_params(axis="x", labelrotation=15)
    fig.tight_layout()
    return fig


def _md(df):
    head = "| " + " | ".join(map(str, df.columns)) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in df.itertuples(index=False))


def main(quick=False):
    out = Path("validation")
    out.mkdir(exist_ok=True)
    res = run(quick=quick)
    s = summarize(res)
    res.to_csv(out / "validation_results.csv", index=False)
    make_figure(res).savefig(out / "validation.png", dpi=130)
    (out / "summary.md").write_text(
        "## Accuracy (typical users)\n\n" + _md(s["accuracy"]) + "\n\n## Robustness at 40 exercises\n\n"
        + _md(s["robustness"]) + "\n", encoding="utf-8")
    print(_md(s["accuracy"][s["accuracy"].n == 40]))
    print(_md(s["robustness"]))
    print("Saved in ./validation")


if __name__ == "__main__":
    main(quick="--quick" in sys.argv)
