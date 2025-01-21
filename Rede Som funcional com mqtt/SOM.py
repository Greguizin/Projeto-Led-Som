import random

class SOM:
    def winner(self, weights, sample):
        distances = [
            sum((sample[i] - weights[c][i]) ** 2 for i in range(len(sample)))
            for c in range(len(weights))
        ]
        return distances.index(min(distances))

    def update(self, weights, sample, J, alpha):
        for i in range(len(weights[J])):
            weights[J][i] += alpha * (sample[i] - weights[J][i])
        return weights

def train_som(samples, num_clusters=10, epochs=100, alpha=0.5):
    """Treina o SOM com os dados fornecidos."""
    weights = [[random.uniform(0, 1) for _ in range(3)] for _ in range(num_clusters)]
    som = SOM()

    for _ in range(epochs):
        for sample in samples:
            J = som.winner(weights, sample)
            weights = som.update(weights, sample, J, alpha)
    
    return weights