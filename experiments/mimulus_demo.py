from api.mimulus_mode import MimulusExperiment
from symbolic_dynamics.observers.attractor import detect_cycle
from symbolic_dynamics.observers.entropy import symbol_entropy
from symbolic_dynamics.observers.trajectory_stats import drift_from_origin


def format_state(state):
    return "".join(str(bit) for bit in state)


def main():

    exp = MimulusExperiment(8)

    exp.add_symbol("cave", "you")
    exp.add_symbol("horse", "partner")
    exp.add_symbol("ladder", "friends")
    exp.add_symbol("flowers", "children")
    exp.add_symbol("storm", "trouble")

    sequence = "cave horse cave storm ladder"

    trajectory = exp.run_sequence(sequence)

    print("Mapping:")

    for row in exp.mapping_table():
        print(row)

    print("\nSequence:")
    print(sequence)

    print("\nTrajectory:")

    for i, state in enumerate(trajectory):
        print(f"{i:02d}: {format_state(state)}  {state}")

    tokens = sequence.split()

    print("\nEntropy:", symbol_entropy(tokens))
    print("Drift:", drift_from_origin(trajectory))
    print("Cycle:", detect_cycle(trajectory))


if __name__ == "__main__":
    main()
