import logging
import paho.mqtt.client as mqtt
from Database import DB
from Mqtt import on_message
from config import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC

def main():
    # Configuração do banco de dados
    db = DB()

    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, db)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        logging.info(f"Assinado no tópico {MQTT_TOPIC} e aguardando mensagens...")

        client.loop_forever()
    except Exception as e:
        logging.error(f"Erro na conexão com o MQTT: {e}")
    finally:
        db.close_connection()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
