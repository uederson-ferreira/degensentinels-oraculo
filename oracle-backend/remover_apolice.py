# remover_apolice.py

import os
import json

APOLICE_DIR = "oracle-backend/apolices"
MONITOR_FILE = f"{APOLICE_DIR}/apolices_monitoradas.json"

def remover_apolice():
    if not os.path.exists(MONITOR_FILE):
        print("⚠️ Nenhuma apólice monitorada.")
        return

    with open(MONITOR_FILE, "r") as f:
        ids = json.load(f)

    print("📋 Apólices monitoradas:")
    for i in ids:
        print(f" - ID {i}")

    try:
        policy_id = int(input("\n🗑️ Digite o ID da apólice que deseja remover: "))
        if policy_id in ids:
            ids.remove(policy_id)
            with open(MONITOR_FILE, "w") as f:
                json.dump(ids, f, indent=2)
            print(f"✅ Apólice {policy_id} removida do monitoramento.")
        else:
            print("❌ ID não encontrado na lista de apólices monitoradas.")
    except Exception as e:
        print("Erro ao remover:", e)

if __name__ == "__main__":
    remover_apolice()
