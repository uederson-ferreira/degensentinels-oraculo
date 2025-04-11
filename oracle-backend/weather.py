# weather.py

import requests

def get_accumulated_precipitation():
    url = "http://localhost:5050/onecall"
    headers = {
        "User-Agent": "Mozilla/5.0 (OraculoUederson)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        daily = data.get("daily", [])
        accumulated = sum(float(day.get("rain", 0.0)) for day in daily[:10])
        return accumulated
    except Exception as e:
        print("Erro ao buscar dados da API simulada:", e)
        return None
