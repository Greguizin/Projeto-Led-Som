from sqlalchemy.orm import Session
from models import LdrReading

def fetch_data_from_postgresql(engine):
    """Busca os dados da tabela 'ldr_readings' no banco de dados PostgreSQL."""
    try:
        with Session(engine) as session:
            result = session.query(LdrReading.red, LdrReading.green, LdrReading.blue).all()
            return [list(row) for row in result]
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return []