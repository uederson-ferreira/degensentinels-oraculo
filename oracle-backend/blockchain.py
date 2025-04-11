# blockchain.py

import time
from multiversx_sdk import Address, Transaction
from multiversx_sdk.wallet import UserSigner
from multiversx_sdk.network_providers import ApiNetworkProvider
from config import CONTRACT_ADDRESS, SEND_REAL_TX, SENDER_ADDRESS, PEM_PATH, CHAIN_ID, PROXY

def send_trigger_transaction(policy_id: int, precipitation: float, timestamp: int):
    """
    Envia uma transação real para acionar o contrato inteligente na Devnet.
    """
    if not SEND_REAL_TX:
        print("Simulação: Preparando transação (não enviada).")
        print(f"Payload: triggerPayment(policy_id={policy_id}, precipitation={precipitation}, timestamp={timestamp})")
        return

    # Função auxiliar para converter valores para hexadecimal com número par de caracteres
    def h(x):
        hex_str = hex(x)[2:] if isinstance(x, int) else str(x).encode("utf-8").hex()
        return hex_str.zfill(len(hex_str) + (len(hex_str) % 2))

    # Monta o payload da função triggerPayment; ex: "triggerPayment@<policy_id>@<precipitation>@<timestamp>"
    # Aqui, usamos h() para garantir a formatação correta (você pode ajustar conforme seu contrato espera)
    payload_str = f"triggerPayment@{h(policy_id)}@{h(int(precipitation * 10))}@{h(timestamp)}"
    
    # Observe que, para payloads simples, você pode enviar a string diretamente (ou convertê-la para bytes se necessário)
    # Se o contrato espera bytes, você pode usar: data=payload_str.encode()
    
    provider = ApiNetworkProvider(PROXY)
    account = provider.get_account(Address.from_bech32(SENDER_ADDRESS))
    signer = UserSigner.from_pem_file(PEM_PATH)

    tx = Transaction(
        nonce=account.nonce,
        sender=Address.from_bech32(SENDER_ADDRESS),
        receiver=Address.from_bech32(CONTRACT_ADDRESS),
        gas_limit=15_000_000,
        chain_id=CHAIN_ID,
        data=payload_str.encode(),
        value=0
    )

    # Assina a transação – aqui usamos o método sign() do UserSigner
    # O método sign() espera a transação serializada em hexadecimal
    tx.signature = signer.sign(tx.serialize_for_signing().hex())
    
    tx_hash = provider.send_transaction(tx)

    print(f"✅ Transação enviada! Hash: {tx_hash}")
    print(f"🔎 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")