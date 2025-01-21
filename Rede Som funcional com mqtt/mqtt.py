import json
import paho.mqtt.client as mqtt
from postgree import fetch_data_from_postgresql
from SOM import train_som
from plloter import plot_som
import time
# Configurações do MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_COMMAND = "meu/topico/comando"  # Tópico para receber o comando "sim"
MQTT_TOPIC_WEIGHTS = "meu/topico/pesos"   # Tópico para enviar os pesos

def publish_weights_mqtt(weights):
    """Publica os pesos no tópico MQTT."""
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.loop_start()

    time.sleep(1)
    weights_json = json.dumps(weights)
    client.publish(MQTT_TOPIC_WEIGHTS, weights_json)
    print(f"Pesos publicados no tópico '{MQTT_TOPIC_WEIGHTS}': {weights_json}")

    client.loop_stop()
    client.disconnect()

def on_message(client, userdata, message):
    """Callback para tratar mensagens recebidas."""
    payload = message.payload.decode("utf-8").strip()
    print(f"Mensagem recebida no tópico '{message.topic}': {payload}")

    if payload.lower() == "sim":
        print("Comando 'sim' recebido. Iniciando processamento...")
        
        # Conexão ao banco e treinamento do SOM
        engine = userdata["engine"]
        samples = fetch_data_from_postgresql(engine)
        
        if not samples:
            print("Nenhum dado encontrado no banco de dados!")
            return

        # Treinar o SOM
        weights = train_som(samples)

        # Fazer o plot antes de publicar
        plot_som(weights, samples, "Pesos Treinados e Amostras")

        # Publicar os pesos via MQTT no tópico de pesos
        publish_weights_mqtt(weights)

def setup_mqtt_listener(engine):
    """Configura o cliente MQTT para ouvir mensagens."""
    client = mqtt.Client(userdata={"engine": engine})
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
    client.subscribe(MQTT_TOPIC_COMMAND)  # Escuta o tópico de comandos
    client.loop_start()
    print(f"Escutando mensagens no tópico '{MQTT_TOPIC_COMMAND}'...")
    return client
