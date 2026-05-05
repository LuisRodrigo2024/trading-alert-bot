import os
import logging
import requests
from dotenv import load_dotenv

# Cargar variables de entorno (local)
load_dotenv()

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

def main():
    logging.info("Bot iniciado correctamente")

    if not TOKEN:
        logging.error("No se encontró TOKEN en variables de entorno")
        return

    # Ejemplo simple de loop (puedes reemplazarlo por tu lógica real)
    while True:
        try:
            # EJEMPLO: llamada a API (puedes cambiarlo por tu trading logic)
            response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
            data = response.json()

            price = data["bpi"]["USD"]["rate"]
            logging.info(f"BTC Price: {price}")

        except Exception as e:
            logging.error(f"Error: {e}")

        import time
        time.sleep(60)

if __name__ == "__main__":
    main()
