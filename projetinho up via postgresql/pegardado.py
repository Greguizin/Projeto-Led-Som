from sqlalchemy import create_engine, Column, Integer, Float
from sqlalchemy.orm import Session, declarative_base
from dotenv import load_dotenv
import os
import time
import random
import matplotlib.pyplot as plt
import numpy as np
from models import LdrReading
import paho.mqtt.client as mqtt  # Biblioteca MQTT
import json  # Para serializar weights

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Banco de Dados PostgreSQL
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Configurações do MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "meu/topico"

# Criar engine do SQLAlchemy
engine = create_engine(
    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# Base declarativa para mapeamento de tabelas
Base = declarative_base()

# Criar tabelas no banco, se não existirem
Base.metadata.create_all(engine)


def fetch_data_from_postgresql():
    """Busca os dados da tabela 'ldr_readings' no banco de dados PostgreSQL."""
    try:
        with Session(engine) as session:
            result = session.query(LdrReading.red, LdrReading.green, LdrReading.blue).all()
            return [list(row) for row in result]
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return []


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


def get_ldr_readings():
    return [
        [150 / 255.0, 0 / 255.0, 150 / 255.0],  # Cor roxo
        [255 / 255.0, 255 / 255.0, 255 / 255.0],  # Cor branca
        [200 / 255.0, 0 / 255.0, 255 / 255.0],  # Cor roxo
        [50 / 255.0, 200 / 255.0, 50 / 255.0],  # Cor verde
        [243 / 255.0, 180 / 255.0, 240 / 255.0],  # Cor rosa
        [0 / 255.0, 0 / 255.0, 255 / 255.0],  # Cor azul
        [185 / 255.0, 130 / 255.0, 65 / 255.0]
    ]


def publish_weights_mqtt(weights):
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    time.sleep(1)  # Espera para garantir que a conexão foi estabelecida
    weights_json = json.dumps(weights)
    client.publish(MQTT_TOPIC, weights_json)
    print(f"Mensagem publicada no tópico '{MQTT_TOPIC}': {weights_json}")

    client.loop_stop()
    client.disconnect()

def main():
    # Buscar dados da tabela no PostgreSQL
    T = fetch_data_from_postgresql()
    print(T)
    if not T:
        print("Nenhum dado encontrado no banco de dados!")
        return

    num_clusters = 10
    weights = [
        [random.uniform(0, 1) for _ in range(3)] for _ in range(num_clusters)
    ]
    ob = SOM()
    epochs = 100
    alpha = 0.5

    plot_som(weights, T, "Pesos Iniciais e Amostras")

    for _ in range(epochs):
        for sample in T:
            J = ob.winner(weights, sample)
            weights = ob.update(weights, sample, J, alpha)

    plot_som(weights, T, "Pesos Treinados e Amostras")

    ldr_readings = get_ldr_readings()
    print("Leituras LDR:", ldr_readings)

    clusters = [ob.winner(weights, reading) for reading in ldr_readings]
    print("Pesos dos clusters:", weights)

    plot_som(weights, T, "Classificação de Leituras do LDR", ldr_readings, clusters, show_samples=False)

    # Publicar pesos no MQTT
    publish_weights_mqtt(weights)


if __name__ == "__main__":
    main()
