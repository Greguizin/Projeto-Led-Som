import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models import LdrReading
from dotenv import load_dotenv
import os

class DB:
    def __init__(self) -> None:
        """Objeto responsável por cuidar do acesso ao banco de dados com as leituras e imagens"""
        load_dotenv(encoding='utf-8')
        logging.info("Criando conexão com Banco de Dados... ")
        db_host = os.getenv("DB_HOST")
        db_user = os.getenv("DB_USER")
        db_pass = os.getenv("DB_PASS")
        db_name = os.getenv("DB_NAME")

        connection_string = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"
        self.engine = create_engine(connection_string, echo=False)
        self.session = Session(self.engine)
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
