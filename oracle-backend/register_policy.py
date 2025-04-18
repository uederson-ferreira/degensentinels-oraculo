# register_policy.py

import time
import json
import os
from pathlib import Path
from multiversx_sdk import Account, Address, Transaction, DevnetEntrypoint
from config import CONTRACT_ADDRESS, CHAIN_ID, PROXY, SENDER_ADDRESS
from multiversx_sdk.wallet import UserPEM
from blockchain import PEM_PATH

PASTA_APOLICES = "apolices"
PASTA_EXCLUIDAS = os.path.join(PASTA_APOLICES, "apolices_excluidas")
os.makedirs(PASTA_APOLICES, exist_ok=True)
os.makedirs(PASTA_EXCLUIDAS, exist_ok=True)

def gerar_novo_id():
    """
    Gera um novo ID incremental, considerando também apólices movidas para a pasta 'apolices_excluidas'.
    """
    ids_usados = set()

    for pasta in [PASTA_APOLICES, PASTA_EXCLUIDAS]:
        arquivos = [f for f in os.listdir(pasta) if f.startswith("apolice_") and f.endswith(".json")]
        for nome in arquivos:
            try:
                id_str = nome.replace("apolice_", "").replace(".json", "")
                ids_usados.add(int(id_str))
            except:
                continue

    if not ids_usados:
        return 1

    return max(ids_usados) + 1

def salvar_json(caminho, dados):
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

def registrar_apolice():
    print("\n📋 Cadastro de nova apólice")

    local = input("📍 Local de cobertura: ").strip()
    limite_chuva = int(input("💧 Limite de chuva acumulada (mm): "))
    dias_chuva = int(input("⏱️ Intervalo entre acionamentos (dias): "))
    indenizacao = int(input("💰 Valor da indenização (em wei): "))
    dias_validade = int(input("📅 Em quantos dias expira o contrato? "))
    limite_acionamentos = int(input("🔁 Limite de acionamentos (0 = ilimitado): "))

    expiration = int(time.time()) + dias_validade * 86400
    policy_id = gerar_novo_id()
    print(f"🆔 ID: {policy_id}")

    def h(x):
        hex_str = hex(x)[2:] if isinstance(x, int) else x.encode("utf-8").hex()
        return hex_str.zfill(len(hex_str) + (len(hex_str) % 2))

    contratante_hex = Address.from_bech32(SENDER_ADDRESS).hex()
    
    args = "@".join([
        h(policy_id),
        contratante_hex,
        h(local),
        h(limite_chuva),
        h(dias_chuva),
        h(indenizacao),
        h(expiration),
        h(limite_acionamentos)
    ])

    data_str = f"registerPolicy@{args}"
    data_bytes = data_str.encode()

    signer = UserPEM.from_file(Path(PEM_PATH))
    sender = Account(secret_key=signer.secret_key)
    sender_address = Address.from_bech32(SENDER_ADDRESS)    
    
    provider = DevnetEntrypoint().create_network_provider()
    sender.nonce = provider.get_account(sender_address).nonce

    tx = Transaction(
        nonce=sender.nonce,
        sender=sender_address,
        receiver=Address.from_bech32(CONTRACT_ADDRESS),
        value=0,
        gas_limit=100000000,
        gas_price=1000000000,
        chain_id=CHAIN_ID,
        data=data_bytes
    )

    tx.signature = sender.sign_transaction(tx)
    tx_hash = provider.send_transaction(tx)

    print(f"\n✅ Transação enviada! Hash: {tx_hash.hex()}")

    apolice = {
        "policy_id": policy_id,
        "local": local,
        "limite_chuva": limite_chuva,
        "dias_chuva": dias_chuva,
        "valor_indenizacao": indenizacao,
        "expiration": expiration,
        "tx_hash": tx_hash.hex(),
        "timestamp_criacao": int(time.time()),
        "limite_acionamentos": limite_acionamentos,
        "acionamentos": 0,
        "ativo": True
    }

    salvar_json(f"{PASTA_APOLICES}/apolice_{policy_id}.json", apolice)

    monitor_path = f"{PASTA_APOLICES}/apolices_monitoradas.json"
    monitoradas = []
    if os.path.exists(monitor_path):
        with open(monitor_path, "r") as f:
            monitoradas = json.load(f)

    monitoradas.append({"policy_id": policy_id, "ativo": True})
    salvar_json(monitor_path, monitoradas)

    print("📝 Apólice salva e monitoramento atualizado.\n")

if __name__ == "__main__":
    registrar_apolice()
