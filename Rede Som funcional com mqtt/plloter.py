import matplotlib.pyplot as plt
import numpy as np

def plot_som(weights, samples, title, ldr_readings=None, clusters=None, show_samples=True):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    ax.set_title(title)
    ax.set_xlabel("R")
    ax.set_ylabel("G")
    ax.set_zlabel("B")

    if show_samples:
        samples = list(zip(*samples))
        ax.scatter(samples[0], samples[1], samples[2], c="blue", label="Amostras", s=50)

    weights_rgb = np.array(weights)

    ax.scatter(weights_rgb[:, 0], weights_rgb[:, 1], weights_rgb[:, 2],
               c=weights_rgb, label="Pesos", s=100, marker="^")

    for i, weight in enumerate(weights):
        ax.text(weight[0], weight[1], weight[2], f"{i}", color="black", fontsize=12, ha="center")

    if ldr_readings and clusters:
        for reading, cluster in zip(ldr_readings, clusters):
            cluster_color = weights[cluster]
            ax.scatter(*reading, c=[cluster_color], label=f"Leitura -> Cluster {cluster}", s=70, marker="x")
            print(f"Leitura LDR: {reading} -> Cor do cluster: {cluster_color}")
    ax.legend()
    plt.show()