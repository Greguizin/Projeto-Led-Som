from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
import time
from mqtt import setup_mqtt_listener

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do Banco de Dados PostgreSQL
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_user = os.getenv("DB_USER")
db_pass = os.getenv("DB_PASS")
db_name = os.getenv("DB_NAME")

# Criar engine do SQLAlchemy
engine = create_engine(
    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
)

# Base declarativa para mapeamento de tabelas
Base = declarative_base()
Base.metadata.create_all(engine)

if __name__ == "__main__":
    # Configurar o listener MQTT
    mqtt_client = setup_mqtt_listener(engine)

    try:
        while True:
            time.sleep(1)  # Mantém o programa rodando
    except KeyboardInterrupt:
        print("Encerrando o programa...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()