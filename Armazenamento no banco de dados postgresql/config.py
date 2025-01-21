import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "ldr/readings"
