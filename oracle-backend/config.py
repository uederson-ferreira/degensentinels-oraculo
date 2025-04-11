# config.py
import os
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

# Parâmetros para consulta do OpenWeatherMap (não utilizados na simulação)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
LATITUDE = -23.5505
LONGITUDE = -46.6333

# Limite de chuva para acionar o seguro (em mm acumulados em 10 dias)
RAIN_THRESHOLD = 100.0

# Endereço do contrato (placeholder; será substituído após deploy)
CONTRACT_ADDRESS = "erd1qqplaceholder"

# Flag para envio real da transação (False para simulação)
SEND_REAL_TX = False
