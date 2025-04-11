# main.py

import time
from weather import get_accumulated_precipitation
from blockchain import send_trigger_transaction
from config import RAIN_THRESHOLD

def main():
    policy_id = 1  # Identificador de exemplo para a apólice
    
    print("Iniciando Oráculo de Seguro Paramétrico (Modo Simulação com API simulada)...")
    
    while True:
        print("\nConsultando dados climáticos (acumulação para 10 dias)...")
        accumulated_precipitation = get_accumulated_precipitation()
        
        if accumulated_precipitation is None:
            print("Erro ao obter dados climáticos. Tentando novamente na próxima consulta...")
        else:
            print(f"Chuva acumulada dos últimos 10 dias: {accumulated_precipitation} mm")
            if accumulated_precipitation > RAIN_THRESHOLD:
                print(f"🚨 Gatilho ativado! Acumulação de chuva ultrapassa {RAIN_THRESHOLD} mm.")
                timestamp = int(time.time())
                send_trigger_transaction(policy_id, accumulated_precipitation, timestamp)
            else:
                print("Condições não atendidas: sem acionamento do seguro.")
        
        print("Aguardando 60 segundos para a próxima verificação...\n")
        time.sleep(60)

if __name__ == "__main__":
    main()
