# blockchain.py

import time
from config import CONTRACT_ADDRESS, SEND_REAL_TX

def send_trigger_transaction(policy_id, precipitation, timestamp):
    """
    Simula (ou envia, se SEND_REAL_TX for True) a transação para acionar o endpoint do contrato.
    """
    if SEND_REAL_TX:
        # Aqui você usará o SDK da MultiversX para criar, assinar e enviar a transação.
        print(f"Enviando transação real para o contrato {CONTRACT_ADDRESS}...")
        time.sleep(1)
        print("Transação enviada!")
    else:
        print("Simulação: Preparando transação (não enviada).")
        print(f"Payload: trigger_payment(policy_id={policy_id}, precipitation={precipitation}, timestamp={timestamp})")
