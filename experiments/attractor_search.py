# experiments/attractor_search.py
from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from symbolic_dynamics.hypercube import Hypercube
from symbolic_dynamics.walkers.walker import Walker
from symbolic_dynamics.grammars.grammar_generators import random_grammar
from symbolic_dynamics.observers.attractor import detect_cycle


def bits(state: Sequence[int]) -> str:
    return "".join(str(b) for b in state)


@dataclass(frozen=True)
class BestCycle:
    first_seen: int
    repeated_at: int
    cycle_length: int
    sequence: List[str]
    trajectory: List[List[int]]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search for attractor cycles by sampling random sequences.")
    p.add_argument("--dimension", type=int, default=8)
    p.add_argument("--symbols", type=int, default=8, help="Symbol count in grammar")
    p.add_argument("--steps", type=int, default=64, help="Sequence length per trial")
    p.add_argument("--trials", type=int, default=200, help="Number of sampled sequences")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--show-trajectory", action="store_true", help="Print full trajectory bitstrings")
    p.add_argument("--show-cycle-table", action="store_true", help="Print cycle step table (state/symbol/next)")
    return p.parse_args()


def search_best_cycle(
    *,
    dimension: int,
    symbol_count: int,
    steps: int,
    trials: int,
    seed: int,
) -> Optional[BestCycle]:
    rng = random.Random(seed)

    space = Hypercube(dimension)
    grammar = random_grammar(symbol_count, dimension)

    # Your SymbolicGrammar stores mapping in .rules
    symbols = sorted(list(grammar.rules.keys()))
    if not symbols:
        return None

    walker = Walker(space=space, grammar=grammar)

    best: Optional[BestCycle] = None
    best_score: Optional[Tuple[int, int]] = None  # (cycle_len, -first_seen)

    for _ in range(trials):
        seq = [rng.choice(symbols) for _ in range(steps)]
        traj = walker.run(seq)
        cyc = detect_cycle(traj)
        if not cyc:
            continue

        first_seen = int(cyc["first_seen"])
        repeated_at = int(cyc["repeated_at"])
        cycle_len = int(cyc["cycle_length"])

        score = (cycle_len, -first_seen)
        if best_score is None or score > best_score:
            best_score = score
            best = BestCycle(
                first_seen=first_seen,
                repeated_at=repeated_at,
                cycle_length=cycle_len,
                sequence=seq,
                trajectory=traj,
            )

    return best


def print_cycle_states(best: BestCycle) -> None:
    cycle_states = best.trajectory[best.first_seen : best.repeated_at]
    print("\nCycle states (bitstrings):")
    for s in cycle_states:
        print(" ", bits(s))


def print_cycle_table(best: BestCycle) -> None:
    """
    Align operators with cycle transitions.

    - trajectory[i] --(sequence[i])--> trajectory[i+1]
    - cycle covers indices: [first_seen, repeated_at)
    - transitions cover i in [first_seen, repeated_at-1]
    """
    fs = best.first_seen
    ra = best.repeated_at

    print("\nCycle table (state --symbol--> next_state):")
    for i in range(fs, ra):
        state_i = best.trajectory[i]
        state_next = best.trajectory[i + 1] if (i + 1) < len(best.trajectory) else None

        sym = best.sequence[i] if i < len(best.sequence) else "(no-symbol)"
        if state_next is None:
            print(f" {i:>3}: {bits(state_i)} -- {sym} --> (end)")
        else:
            print(f" {i:>3}: {bits(state_i)} -- {sym} --> {bits(state_next)}")

    # Show wrap implication (last cycle state goes back to first)
    if ra < len(best.trajectory):
        last_state = best.trajectory[ra - 1]
        first_state = best.trajectory[fs]
        print(f" wrap: {bits(last_state)} ~~> {bits(first_state)} (repeat detected at index {ra})")


def main() -> int:
    args = parse_args()
    best = search_best_cycle(
        dimension=args.dimension,
        symbol_count=args.symbols,
        steps=args.steps,
        trials=args.trials,
        seed=args.seed,
    )

    print("Trials:", args.trials)

    if best is None:
        print("Best cycle: None")
        return 0

    print("Best cycle:", (best.first_seen, best.cycle_length))
    print("Best sequence:", best.sequence)

    print_cycle_states(best)

    if args.show_cycle_table:
        print_cycle_table(best)

    if args.show_trajectory:
        print("\nFull trajectory (bitstrings):")
        for s in best.trajectory:
            print(" ", bits(s))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
