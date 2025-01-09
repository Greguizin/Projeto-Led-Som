import logging
import json
import os
from dotenv import load_dotenv
from cv2 import imread
from sqlalchemy import create_engine, select, Column, Integer, Float
from sqlalchemy.orm import Session, declarative_base
from sqlalchemy.ext.declarative import declarative_base
import paho.mqtt.client as mqtt
from models import LdrReading
# Carregar variáveis de ambiente
load_dotenv()

# Definir a base do SQLAlchemy para as models
Base = declarative_base()


class DB:
    def __init__(self, db_directory='DB') -> None:
        """Objeto responsável por cuidar do acesso ao banco de dados com as leituras e imagens"""
        self.db_directory = db_directory
        load_dotenv(encoding='utf-8')
        logging.info("Criando conexão com Banco de Dados... ")

        # Carregar variáveis de ambiente do PostgreSQL
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")

        # Conexão PostgreSQL com SQLAlchemy
        connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
        self.engine = create_engine(connection_string, echo=False)
        self.session = Session(self.engine)

        # Criar as tabelas, caso ainda não existam

        logging.info("Sessão do banco de dados inicializada com sucesso!")

    def close_connection(self) -> None:
        """Fechar a conexão com o banco de dados"""
        self.session.close()
        self.engine.dispose()
        logging.info("Instância de conexão com o banco fechada com sucesso!")

    def insert_ldr_reading(self, red, green, blue) -> None:
        """Inserir a leitura LDR no banco de dados"""
        try:
            ldr_reading = LdrReading(red=red, green=green, blue=blue)
            self.session.add(ldr_reading)
            self.session.commit()
            logging.info(f"Leitura LDR inserida com sucesso: red={red}, green={green}, blue={blue}")
        except Exception as e:
            logging.error(f"Erro ao inserir leitura LDR no banco de dados: {e}")
            self.session.rollback()

# Funções para lidar com MQTT
def on_message(client, userdata, msg, db):
    try:
        # Decodificando a mensagem recebida
        payload = msg.payload.decode("utf-8")
        reading = json.loads(payload)  # JSON no formato {"red": 0.5, "green": 0.2, "blue": 0.8}

        red = reading.get("red")
        green = reading.get("green")
        blue = reading.get("blue")
        print(blue,red,green)
        if red is not None and green is not None and blue is not None:
            # Inserir os dados no banco de dados PostgreSQL
            db.insert_ldr_reading(red, green, blue)
        else:
            logging.error(f"Dados inválidos recebidos: {payload}")
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")

def main():
    # Configuração do MQTT
    MQTT_BROKER = "broker.emqx.io"
    MQTT_PORT = 1883
    MQTT_TOPIC = "ldr/readings"

    # Inicializa a classe DB para interagir com o banco de dados
    db = DB()  # Aqui a instância de DB é criada

    # Configuração do cliente MQTT
    client = mqtt.Client()
    client.on_message = lambda client, userdata, msg: on_message(client, userdata, msg, db)

    try:
        # Conectar-se ao broker MQTT e assinar o tópico
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.subscribe(MQTT_TOPIC)
        logging.info(f"Assinado no tópico {MQTT_TOPIC} e aguardando mensagens...")

        # Iniciar o loop MQTT para receber mensagens
        client.loop_forever()
    except Exception as e:
        logging.error(f"Erro na conexão com o MQTT: {e}")
    finally:
        db.close_connection()  # Fecha a conexão com o banco de dados quando terminar

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
