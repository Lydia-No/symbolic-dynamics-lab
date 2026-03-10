# pages/2_Attractor_Search.py
from __future__ import annotations

import streamlit as st

from experiments.attractor_search import search_best_cycle, bits, print_cycle_table


st.set_page_config(page_title="Attractor Search", layout="wide")
st.title("Attractor Search 🔁")
st.caption("Randomly samples sequences to find a repeated-state cycle (attractor) in the hypercube trajectory.")

with st.sidebar:
    st.header("Search parameters")
    dimension = st.slider("Hypercube dimension", 2, 16, 8)
    symbol_count = st.slider("Symbol count in random grammar", 2, 32, 8)
    steps = st.slider("Steps per trial", 8, 512, 64)
    trials = st.slider("Trials", 10, 2000, 200)
    seed = st.number_input("RNG seed", min_value=0, value=0, step=1)

    show_cycle_table = st.toggle("Show cycle table (state --symbol--> next_state)", value=True)
    show_full_trajectory = st.toggle("Show full trajectory", value=False)

    run = st.button("Run search", type="primary")

if not run:
    st.info("Set parameters and click **Run search**.")
    st.stop()

with st.spinner("Searching..."):
    best = search_best_cycle(
        dimension=int(dimension),
        symbol_count=int(symbol_count),
        steps=int(steps),
        trials=int(trials),
        seed=int(seed),
    )

if best is None:
    st.warning("No cycle found in sampled trials.")
    st.stop()

left, right = st.columns([2, 1], gap="large")

with right:
    st.subheader("Best result")
    st.write(
        {
            "cycle": (best.first_seen, best.cycle_length),
            "first_seen_index": best.first_seen,
            "cycle_length": best.cycle_length,
            "repeat_detected_at": best.repeated_at,
            "sequence_length": len(best.sequence),
        }
    )

with left:
    st.subheader("Best sequence")
    st.code(" ".join(best.sequence), language="text")

    cycle_states = best.trajectory[best.first_seen : best.repeated_at]
    st.subheader("Cycle states (bitstrings)")
    st.code("\n".join(bits(s) for s in cycle_states), language="text")

    if show_cycle_table:
        st.subheader("Cycle table (aligned operators)")
        lines = []
        fs = best.first_seen
        ra = best.repeated_at
        for i in range(fs, ra):
            sym = best.sequence[i] if i < len(best.sequence) else "(no-symbol)"
            s0 = bits(best.trajectory[i])
            s1 = bits(best.trajectory[i + 1])
            lines.append(f"{i:>3}: {s0} -- {sym} --> {s1}")
        lines.append(f"wrap: {bits(best.trajectory[ra - 1])} ~~> {bits(best.trajectory[fs])}")
        st.code("\n".join(lines), language="text")

    if show_full_trajectory:
        st.subheader("Full trajectory (bitstrings)")
        st.code("\n".join(bits(s) for s in best.trajectory), language="text")
