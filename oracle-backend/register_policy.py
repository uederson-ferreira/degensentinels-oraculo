# register_policy.py

import time
import json
import os
from pathlib import Path
from multiversx_sdk import Account, Address, Transaction, DevnetEntrypoint, TransactionComputer
from config import CONTRACT_ADDRESS, PEM_PATH, CHAIN_ID, PROXY, SENDER_ADDRESS
from multiversx_sdk.wallet import UserPEM

# Pasta para armazenar as apólices
PASTA_APOLICES = "apolices"
os.makedirs(PASTA_APOLICES, exist_ok=True)

def gerar_novo_id():
    arquivos = [f for f in os.listdir(PASTA_APOLICES) if f.startswith("apolice_") and f.endswith(".json")]
    return len(arquivos) + 1

def salvar_json(caminho, dados):
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

def registrar_apolice():
    print("\n📋 Cadastro de nova apólice")

    local = input("📍 Local de cobertura: ").strip()
    limite_chuva = int(input("💧 Limite de chuva acumulada (mm): "))
    dias_chuva = int(input("⏱️ Dias de chuva (dias): "))
    indemnizacao = int(input("💰 Valor da indenização (em wei): "))
    dias_validade = int(input("📅 Em quantos dias expira o contrato? "))

    expiration = int(time.time()) + dias_validade * 86400
    policy_id = gerar_novo_id()
    print(f"🆔 ID: {policy_id}")

    # Função auxiliar para converter valores para hexadecimal com número par de caracteres
    def h(x):
        hex_str = hex(x)[2:] if isinstance(x, int) else x.encode("utf-8").hex()
        return hex_str.zfill(len(hex_str) + (len(hex_str) % 2))
    
    # Concatena os argumentos na ordem: policy_id, contratante, local, limite_chuva, dias_chuva, valor_indemnizacao, expiration
    contratante_hex = Address.from_bech32(SENDER_ADDRESS).hex()
    args = "@".join([
        h(policy_id),
        contratante_hex,
        h(local),
        h(limite_chuva),
        h(dias_chuva),
        h(indemnizacao),
        h(expiration)
    ])

    # Cria o payload e converte para bytes
    data_str = f"registerPolicy@{args}"
    data_bytes = data_str.encode()  # Convertendo para bytes

    # Carrega o signer a partir do arquivo PEM e cria a conta usando a chave secreta
    signer = UserPEM.from_file(Path(PEM_PATH))
    sender = Account(secret_key=signer.secret_key)
    
    # Cria o objeto Address para o remetente a partir do SENDER_ADDRESS
    sender_address = Address.from_bech32(SENDER_ADDRESS)

    # Cria o provedor de rede com o endpoint da Devnet
    provider = DevnetEntrypoint().create_network_provider()
    account_on_chain = provider.get_account(sender_address)
    sender.nonce = account_on_chain.nonce

    # Cria a transação com os parâmetros definidos
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

    # Assina a transação passando o objeto Transaction diretamente
    signature = sender.sign_transaction(tx)
    tx.signature = signature

    # Envia a transação e obtém o hash
    tx_hash = provider.send_transaction(tx)
    print(f"\n✅ Transação enviada! Hash: {tx_hash.hex()}")

    # Salva os dados da apólice em um arquivo JSON
    apolice = {
        "policy_id": policy_id,
        "local": local,
        "limite_chuva": limite_chuva,
        "dias_chuva": dias_chuva,
        "valor_indemnizacao": indemnizacao,
        "expiration": expiration,
        "tx_hash": tx_hash.hex(),
        "timestamp_criacao": int(time.time())
    }
    salvar_json(f"{PASTA_APOLICES}/apolice_{policy_id}.json", apolice)

    # Atualiza a lista de apólices monitoradas
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