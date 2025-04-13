# blockchain.py

import time
import json
import os
from pathlib import Path 
from multiversx_sdk import Address, Transaction, Account
from multiversx_sdk.wallet import UserSigner
from multiversx_sdk.network_providers import ApiNetworkProvider
from config import CONTRACT_ADDRESS, SEND_REAL_TX, SENDER_ADDRESS, PEM_PATH, CHAIN_ID, PROXY

from dotenv import load_dotenv

load_dotenv()

PASTA_PEM = os.getenv("PASTA_PEM")
BASE_DIR = Path(os.getcwd()).parent
PEM_PATH = BASE_DIR / (PASTA_PEM + "1") / f"{SENDER_ADDRESS}.pem"

APOLICE_DIR = "apolices"
MONITOR_FILE = f"{APOLICE_DIR}/apolices_monitoradas.json"

def send_trigger_transaction(policy_id: int, precipitation: float, timestamp: int):
    """
    Envia uma transação para acionar o seguro na blockchain, conforme os dados do oráculo.
    Atualiza o arquivo local se o envio for real.
    """
    if not SEND_REAL_TX:
        print("💡 Modo simulação: nenhuma transação será enviada.")
        print(f"Simulação de triggerPayment(policy_id={policy_id}, chuva={precipitation:.2f} mm, timestamp={timestamp})")
        return

    # Converte milímetros para inteiro (ex: 25.7 mm => 257)
    chuva_em_decimos = int(precipitation * 10)

    # Função auxiliar para gerar hex seguro
    def h(x):
        hex_str = hex(x)[2:] if isinstance(x, int) else str(x).encode("utf-8").hex()
        return hex_str.zfill(len(hex_str) + (len(hex_str) % 2))

    # Monta o payload conforme o contrato espera
    payload = f"triggerPayment@{h(policy_id)}@{h(chuva_em_decimos)}@{h(timestamp)}"

    # Setup do provider
    provider = ApiNetworkProvider(PROXY)

    # Re-obter o estado atual da conta para capturar o nonce atualizado
    account = provider.get_account(Address.from_bech32(SENDER_ADDRESS))
    current_nonce = account.nonce  # nonce atualizado

    # Configura o signer e a conta a partir do PEM
    signer_obj = UserSigner.from_pem_file(PEM_PATH)
    sender = Account(secret_key=signer_obj.secret_key)

    tx = Transaction(
        nonce=current_nonce,
        sender=Address.from_bech32(SENDER_ADDRESS),
        receiver=Address.from_bech32(CONTRACT_ADDRESS),
        value=0,
        gas_limit=15_000_000,
        chain_id=CHAIN_ID,
        data=payload.encode()
    )

    # Assinatura da transação utilizando o método sign_transaction do Account
    tx.signature = sender.sign_transaction(tx)
    tx_hash = provider.send_transaction(tx)

    print(f"✅ Transação enviada com sucesso! Hash: {tx_hash.hex()}")
    print(f"🔗 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash.hex()}")

    # Atualiza monitoramento local
    atualizar_monitoramento_local(policy_id)

def atualizar_monitoramento_local(policy_id: int):
    """
    Atualiza localmente o JSON monitorado para refletir um acionamento a mais.
    """
    if not os.path.exists(MONITOR_FILE):
        return

    with open(MONITOR_FILE, "r") as f:
        monitoradas = json.load(f)

    for apolice in monitoradas:
        if apolice["policy_id"] == policy_id:
            apolice["ativo"] = True  # Continua ativo até o contrato desativar
            break

    with open(MONITOR_FILE, "w") as f:
        json.dump(monitoradas, f, indent=2)

def atualizar_apolice_apos_acionamento(apolice: dict, timestamp: int):
    """
    Atualiza os dados locais da apólice após acionamento.
    Incrementa os acionamentos e define nova data de última atualização.
    """
    apolice["acionamentos"] = apolice.get("acionamentos", 0) + 1
    apolice["ultima_atualizacao"] = timestamp

    policy_id = apolice["policy_id"]
    path = os.path.join("apolices", f"apolice_{policy_id}.json")

    with open(path, "w") as f:
        json.dump(apolice, f, indent=2)

    print(f"💾 Apólice {policy_id} atualizada localmente com novo acionamento.")
