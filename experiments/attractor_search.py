# experiments/attractor_search.py
from __future__ import annotations

import argparse
import random
from typing import List, Optional, Sequence, Tuple

from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.walkers.walker import Walker
from symbolic_dynamics.grammars.grammar_generators import random_grammar
from symbolic_dynamics.observers.attractor import detect_cycle


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search for attractor cycles by sampling random sequences.")
    p.add_argument("--dimension", type=int, default=8)
    p.add_argument("--symbols", type=int, default=8, help="Symbol count in grammar")
    p.add_argument("--steps", type=int, default=64, help="Sequence length per trial")
    p.add_argument("--trials", type=int, default=200, help="Number of sampled sequences")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--show-trajectory", action="store_true", help="Also print full trajectory bitstrings")
    return p.parse_args()


def bits(state: Sequence[int]) -> str:
    return "".join(str(b) for b in state)


def slice_cycle(trajectory: List[List[int]], first_seen: int, repeated_at: int) -> List[List[int]]:
    # cycle states are trajectory[first_seen : repeated_at]
    return trajectory[first_seen:repeated_at]


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)

    space = Hypercube(args.dimension)
    grammar = random_grammar(args.symbols, args.dimension)

    # Your SymbolicGrammar stores mapping in .rules
    symbols = sorted(list(grammar.rules.keys()))
    if not symbols:
        print("No symbols in grammar.")
        return 2

    walker = Walker(space=space, grammar=grammar)

    best_cycle: Optional[Tuple[int, int]] = None  # (first_seen, cycle_len)
    best_seq: Optional[List[str]] = None
    best_cycle_states: Optional[List[List[int]]] = None
    best_traj: Optional[List[List[int]]] = None

    for _ in range(args.trials):
        seq = [rng.choice(symbols) for _ in range(args.steps)]
        traj = walker.run(seq)
        cyc = detect_cycle(traj)
        if not cyc:
            continue

        first_seen = int(cyc["first_seen"])
        repeated_at = int(cyc["repeated_at"])
        cycle_len = int(cyc["cycle_length"])

        # prefer longer cycles; tie-breaker: earlier start
        score = (cycle_len, -first_seen)
        if best_cycle is None or score > (best_cycle[1], -best_cycle[0]):
            best_cycle = (first_seen, cycle_len)
            best_seq = seq
            best_cycle_states = slice_cycle(traj, first_seen, repeated_at)
            best_traj = traj

    print("Trials:", args.trials)
    print("Best cycle:", best_cycle)
    print("Best sequence:", best_seq)

    if best_cycle_states is not None:
        print("\nCycle states (bitstrings):")
        for s in best_cycle_states:
            print(" ", bits(s))

    if args.show_trajectory and best_traj is not None:
        print("\nFull trajectory (bitstrings):")
        for s in best_traj:
            print(" ", bits(s))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
