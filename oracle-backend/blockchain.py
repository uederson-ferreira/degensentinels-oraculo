# blockchain.py

import time
from multiversx_sdk.core import Address, TransactionPayload
from multiversx_sdk.wallet import UserSigner
from multiversx_sdk.transactions import Transaction
from multiversx_sdk.network_providers import ApiNetworkProvider

from config import CONTRACT_ADDRESS, SEND_REAL_TX

# CONFIGURAÇÕES
PROXY = "https://devnet-api.multiversx.com"
CHAIN_ID = "D"
PEM_PATH = "smart-contracts/carteiras/carteira1/erd1e7q3eqcdpl29kw8n76q6rzg67ptqve34r40ppnfx3g373fegsjusnwxrt5.pem"
SENDER_ADDRESS = "erd1e7q3eqcdpl29kw8n76q6rzg67ptqve34r40ppnfx3g373fegsjusnwxrt5"

def send_trigger_transaction(policy_id: int, precipitation: float, timestamp: int):
    """
    Envia uma transação real para acionar o contrato inteligente na Devnet.
    """
    if not SEND_REAL_TX:
        print("Simulação: Preparando transação (não enviada).")
        print(f"Payload: trigger_payment(policy_id={policy_id}, precipitation={precipitation}, timestamp={timestamp})")
        return

    # Constrói o payload
    data = f"triggerPayment@{policy_id:02x}@{int(precipitation * 10):02x}@{timestamp:x}"
    payload = TransactionPayload.from_str(data)

    provider = ApiNetworkProvider(PROXY)
    account = provider.get_account(Address.from_bech32(SENDER_ADDRESS))
    signer = UserSigner.from_pem_file(PEM_PATH)

    tx = Transaction(
        nonce=account.nonce,
        sender=Address.from_bech32(SENDER_ADDRESS),
        receiver=Address.from_bech32(CONTRACT_ADDRESS),
        gas_limit=15_000_000,
        chain_id=CHAIN_ID,
        payload=payload,
        value=0
    )

    tx.signature = signer.sign(tx.serialize_for_signing().hex())
    tx_hash = provider.send_transaction(tx)

    print(f"✅ Transação enviada! Hash: {tx_hash}")
    print(f"🔎 Explorer: https://devnet-explorer.multiversx.com/transactions/{tx_hash}")
