# register_policy.py

import time
import json
import os
from multiversx_sdk.core import Address, TransactionPayload
from multiversx_sdk.wallet import UserSigner
from multiversx_sdk.transactions import Transaction
from multiversx_sdk.network_providers import ApiNetworkProvider
from config import CONTRACT_ADDRESS

# CONFIGURAÇÕES
PROXY = "https://devnet-api.multiversx.com"
CHAIN_ID = "D"
PEM_PATH = "smart-contracts/carteiras/carteira1/erd1e7q3eqcdpl29kw8n76q6rzg67ptqve34r40ppnfx3g373fegsjusnwxrt5.pem"
SENDER_ADDRESS = "erd1e7q3eqcdpl29kw8n76q6rzg67ptqve34r40ppnfx3g373fegsjusnwxrt5"
APOLICE_DIR = "oracle-backend/apolices"

os.makedirs(APOLICE_DIR, exist_ok=True)

# GERA O PRÓXIMO ID DISPONÍVEL
def find_next_policy_id(provider):
    for i in range(1, 1000):
        query = {
            "scAddress": CONTRACT_ADDRESS,
            "funcName": "getPolicy",
            "args": [hex(i)[2:]],
        }
        try:
            response = provider.do_post("/vm-values/query", query)
            if response.get("data", {}).get("returnCode") == "error":
                return i
        except Exception:
            return i
    raise Exception("⚠️ Muitos IDs usados, revise o contrato.")

# ATUALIZA ARQUIVO DE MONITORAMENTO
def append_to_monitor_list(policy_id):
    monitor_file = f"{APOLICE_DIR}/apolices_monitoradas.json"
    if os.path.exists(monitor_file):
        with open(monitor_file, "r") as f:
            ids = json.load(f)
    else:
        ids = []
    if policy_id not in ids:
        ids.append(policy_id)
    with open(monitor_file, "w") as f:
        json.dump(ids, f, indent=2)

# INÍCIO
print("📋 Cadastro de nova apólice (com JSON e monitoramento)")

provider = ApiNetworkProvider(PROXY)
policy_id = find_next_policy_id(provider)
print(f"🔢 ID automático atribuído: {policy_id}")

# DADOS
local = input("📍 Local da apólice (ex: Barcarena-PA): ")
duracao_dias = int(input("⏱️ Duração (em dias) para somar chuvas: "))
limite_chuva = int(input("🌧️ Limite de chuva acumulada (mm): "))
valor_egld = float(input("💰 Valor da indenização em EGLD (ex: 1.0): "))
dias_validade = int(input("📅 Validade da apólice (dias): "))
expiration = int(time.time()) + dias_validade * 86400
valor_indemnizacao = int(valor_egld * 10**18)

# HEX CONVERSÃO PARA PAYLOAD
hex_args = [
    f"{policy_id:02x}",
    Address.from_bech32(SENDER_ADDRESS).hex(),
    local.encode().hex(),
    f"{limite_chuva:02x}",
    f"{duracao_dias:02x}",
    f"{valor_indemnizacao:x}",
    f"{expiration:x}"
]
payload_str = "registerPolicy@" + "@".join(hex_args)
payload = TransactionPayload.from_str(payload_str)

# TRANSAÇÃO
account = provider.get_account(Address.from_bech32(SENDER_ADDRESS))
signer = UserSigner.from_pem_file(PEM_PATH)

tx = Transaction(
    nonce=account.nonce,
    sender=Address.from_bech32(SENDER_ADDRESS),
    receiver=Address.from_bech32(CONTRACT_ADDRESS),
    gas_limit=50_000_000,
    chain_id=CHAIN_ID,
    payload=payload,
    value=0
)

tx.signature = signer.sign(tx.serialize_for_signing().hex())
tx_hash = provider.send_transaction(tx)

# ✅ SALVA JSON DA APÓLICE
dados = {
    "policy_id": policy_id,
    "local": local,
    "duracao_dias": duracao_dias,
    "limite_chuva": limite_chuva,
    "valor_indemnizacao": valor_indemnizacao,
    "expiration": expiration,
    "contratante": SENDER_ADDRESS
}
with open(f"{APOLICE_DIR}/apolice_{policy_id}.json", "w") as f:
    json.dump(dados, f, indent=2)

# 📌 Atualiza a lista de apólices monitoradas
append_to_monitor_list(policy_id)

print(f"\n✅ Apólice registrada com sucesso!")
print(f"📄 Arquivo salvo: apolices/apolice_{policy_id}.json")
print(f"📊 Adicionada ao monitoramento em apolices_monitoradas.json")
print(f"🔎 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")