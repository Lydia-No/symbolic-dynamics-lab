# experiments/attractor_search.py
from __future__ import annotations

import argparse
import random
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from symbolic_dynamics.grammars.grammar_generators import random_grammar


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Search for attractors by sampling random sequences.")
    p.add_argument("--dimension", type=int, default=8)
    p.add_argument("--symbols", type=int, default=8, help="Symbol count in grammar")
    p.add_argument("--steps", type=int, default=64, help="Sequence length per trial")
    p.add_argument("--trials", type=int, default=200, help="Number of sampled sequences")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def _looks_like_symbol_map(obj: Any) -> bool:
    if not isinstance(obj, dict) or not obj:
        return False
    keys = list(obj.keys())
    if not all(isinstance(k, str) for k in keys):
        return False
    # Values can be operators / callables / objects — we don't constrain heavily
    return True


def _infer_symbol_list(grammar: Any) -> List[str]:
    """
    Best-effort symbol extraction:
    1) Common attribute names
    2) Any attribute that is a dict[str, ...]
    3) Any attribute that is a list/tuple[str]
    4) Any dict-like inside __dict__
    """
    # 1) common names
    for name in (
        "symbols",
        "symbol_list",
        "alphabet",
        "vocabulary",
    ):
        if hasattr(grammar, name):
            v = getattr(grammar, name)
            if isinstance(v, (list, tuple)) and all(isinstance(x, str) for x in v):
                return list(v)

    for name in (
        "symbol_to_operator",
        "symbol_map",
        "operators",
        "mapping",
        "rules",
        "grammar",
    ):
        if hasattr(grammar, name):
            v = getattr(grammar, name)
            if _looks_like_symbol_map(v):
                return sorted(list(v.keys()))

    # 2) scan attributes for dict[str,*]
    for name in dir(grammar):
        if name.startswith("_"):
            continue
        try:
            v = getattr(grammar, name)
        except Exception:
            continue
        if _looks_like_symbol_map(v):
            return sorted(list(v.keys()))

    # 3) scan attributes for list[str]
    for name in dir(grammar):
        if name.startswith("_"):
            continue
        try:
            v = getattr(grammar, name)
        except Exception:
            continue
        if isinstance(v, (list, tuple)) and v and all(isinstance(x, str) for x in v):
            return list(v)

    # 4) scan __dict__ as last resort
    d = getattr(grammar, "__dict__", {})
    if isinstance(d, dict):
        for _, v in d.items():
            if _looks_like_symbol_map(v):
                return sorted(list(v.keys()))
        for _, v in d.items():
            if isinstance(v, (list, tuple)) and v and all(isinstance(x, str) for x in v):
                return list(v)

    raise AttributeError(
        "Could not infer symbols from grammar. "
        "Run: python3 -c \"... print(g.__dict__) ...\" and check which field holds your mapping/list."
    )


def _run_sequence(grammar: Any, sequence: Sequence[str]) -> Any:
    """
    Try likely execution surfaces without crashing.
    """
    # Grammar might have a method
    for method_name in ("walk", "run", "execute", "apply_sequence"):
        fn = getattr(grammar, method_name, None)
        if callable(fn):
            return fn(sequence)

    # Or a Walker exists
    try:
        from symbolic_dynamics.walkers.walker import Walker  # type: ignore
    except Exception:
        Walker = None  # type: ignore

    if Walker is not None:
        try:
            w = Walker(grammar=grammar)  # type: ignore
        except TypeError:
            w = Walker(grammar)  # type: ignore

        for method_name in ("walk", "run", "execute"):
            fn = getattr(w, method_name, None)
            if callable(fn):
                return fn(sequence)

    raise AttributeError("Could not run sequence: no grammar.walk/run or Walker.walk/run found.")


def _extract_cycle(result: Any) -> Optional[Tuple[int, int]]:
    """
    Cycle formats vary; accept common patterns.
    """
    # direct tuple
    if isinstance(result, tuple) and len(result) == 2 and all(isinstance(x, int) for x in result):
        return result  # type: ignore

    for name in ("first_cycle", "cycle", "cycle_info"):
        v = getattr(result, name, None)
        if isinstance(v, tuple) and len(v) == 2 and all(isinstance(x, int) for x in v):
            return v  # type: ignore

    # nested report
    for name in ("attractor", "attractor_report"):
        rep = getattr(result, name, None)
        if rep is not None:
            v = getattr(rep, "first_cycle", None)
            if isinstance(v, tuple) and len(v) == 2:
                return v  # type: ignore

    return None


def main() -> int:
    args = parse_args()
    rng = random.Random(args.seed)

    grammar = random_grammar(args.symbols, args.dimension)
    symbols = _infer_symbol_list(grammar)

    best_cycle: Optional[Tuple[int, int]] = None
    best_score: Optional[Tuple[int, int]] = None
    best_seq: Optional[List[str]] = None

    failures = 0
    for _ in range(args.trials):
        seq = [rng.choice(symbols) for _ in range(args.steps)]
        try:
            result = _run_sequence(grammar, seq)
        except Exception as e:
            failures += 1
            if failures == 1:
                print("First run failure:", repr(e))
                print("Tip: inspect grammar fields with:")
                print('  python3 -c "from symbolic_dynamics.grammars.grammar_generators import random_grammar; g=random_grammar(8,8); print(g.__dict__)"')
            continue

        cycle = _extract_cycle(result)
        if cycle:
            start, length = cycle
            score = (length, -start)
            if best_score is None or score > best_score:
                best_score = score
                best_cycle = cycle
                best_seq = seq

    print("Trials:", args.trials, "| Failures:", failures)
    print("Best cycle:", best_cycle)
    print("Best sequence:", best_seq)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
