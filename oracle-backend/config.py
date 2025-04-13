# config.py
import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# ⚙️ Informações do contrato e carteira
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")  # Endereço do contrato
PEM_PATH = os.getenv("PEM_PATH")                  # Caminho para o arquivo .pem da carteira
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")      # Endereço da carteira do remetente
CHAIN_ID = os.getenv("CHAIN_ID", "D")             # ID da cadeia (D = Devnet)
PROXY = os.getenv("PROXY", "https://devnet-api.multiversx.com")  # Proxy da rede

# 🌦️ API do OpenWeatherMap (usado se for consultar clima real)
API_KEY = os.getenv("OPENWEATHER_API_KEY")
LATITUDE = float(os.getenv("LATITUDE", -23.5505))
LONGITUDE = float(os.getenv("LONGITUDE", -46.6333))

# 🚨 Parâmetros de controle
RAIN_THRESHOLD = float(os.getenv("RAIN_THRESHOLD", 100.0))  # Limite default de chuva (mm)
SEND_REAL_TX = os.getenv("SEND_REAL_TX", "False").lower() in ("1", "true", "yes")