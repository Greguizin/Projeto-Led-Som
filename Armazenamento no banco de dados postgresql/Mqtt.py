import logging
import json

def on_message(client, userdata, msg, db):
    try:
        payload = msg.payload.decode("utf-8")
        reading = json.loads(payload)  # JSON no formato {"red": 0.5, "green": 0.2, "blue": 0.8}

        red = reading.get("red")
        green = reading.get("green")
        blue = reading.get("blue")
        print(blue, red, green)
        if red is not None and green is not None and blue is not None:
            db.insert_ldr_reading(red, green, blue)
        else:
            logging.error(f"Dados inválidos recebidos: {payload}")
    except json.JSONDecodeError as e:
        logging.error(f"Erro ao decodificar JSON: {e}")
    except Exception as e:
        logging.error(f"Erro ao processar mensagem: {e}")
