# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
PEM_PATH = os.getenv("PEM_PATH")
CHAIN_ID = os.getenv("CHAIN_ID", "D")
PROXY = os.getenv("PROXY", "https://devnet-api.multiversx.com")
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")

# Parâmetros para consulta do OpenWeatherMap (não utilizados na simulação)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
LATITUDE = -23.5505
LONGITUDE = -46.6333

# Limite de chuva para acionar o seguro (em mm acumulados em 10 dias)
RAIN_THRESHOLD = 100.0

# Flag para envio real da transação (False para simulação)
SEND_REAL_TX = False