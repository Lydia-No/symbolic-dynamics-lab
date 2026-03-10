import matplotlib.pyplot as plt


def plot_trajectory(traj):

    xs = list(range(len(traj)))

    ys = [sum(state) for state in traj]

    plt.plot(xs, ys)

    plt.xlabel("step")

    plt.ylabel("active bits")

    plt.title("cube trajectory")

    plt.show()
